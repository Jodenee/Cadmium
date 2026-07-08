import logging

from typing import Optional, cast
from pathlib import Path
from pytubefix import AsyncYouTube, Stream

from ..temporary_file_storage import TemporaryFileStorage
from ..protocols import VideoDownloaderProtocol
from ..factories import ProgressBarFactory
from ..dataclasses import FFmpegFileArgs, FFmpegOptionArgs
from ...custom_types import VideoDownloadResult, Configuration
from ...exceptions import ImpossibleDownloadPath
from ...utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, APPLICATION_LOGGER_NAME, TEMPORARY_FILES_DIRECTORY_PATH
from ...utilities.validation import ensure_can_use_ffmpeg
from ...utilities.console import pick_from_streams, spaced_print
from ...utilities.file_conversion import convert_file
from ...utilities.os import resolve_safe_file_path, safe_join_directory
from ...utilities.pytubefix_extensions import get_youtube_from_stream

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class CustomDownloader(VideoDownloaderProtocol[list[VideoDownloadResult]]):
    """A downloader variant for downloading specific streams chosen by the user."""

    def __init__(
        self, 
        configuration: Configuration, 
        temporary_file_storage: TemporaryFileStorage,
        progress_bar_factory: ProgressBarFactory,
        ffmpeg_executable_path: Optional[Path] = None
    ) -> None:
        self._temporary_file_storage = temporary_file_storage
        self._configuration = configuration
        self._progress_bar_factory = progress_bar_factory
        self._ffmpeg_executable_path = ffmpeg_executable_path


    async def download(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        delete_temporary_files = self._configuration["download_behavior_configuration"]["automatically_delete_temporary_files_after_download"]
        put_in_custom_folder = self._configuration["quality_of_life_configuration"]["put_custom_streams_in_folder"]
        results: list[VideoDownloadResult] = []

        logger.info("prompting user for streams to download")

        chosen_streams = pick_from_streams(await youtube_video.streams())

        logger.debug(
            "video_id=%s stream_itags=%s should_convert=%s should_skip_existing_files=%s custom_file_extension=%s delete_temporary_files=%s put_custom_streams_in_folder=%s",
            youtube_video.video_id,
            tuple(map(lambda x: x.itag, chosen_streams)),
            self._configuration["download_behavior_configuration"]["convert_custom_downloads"], 
            self._configuration["download_behavior_configuration"]["skip_existing_files"],
            self._configuration["download_behavior_configuration"]["convert_custom_downloads_to"],
            self._configuration["download_behavior_configuration"]["automatically_delete_temporary_files_after_download"],
            put_in_custom_folder
        )

        if len(chosen_streams) == 0:
            logger.info("no streams chosen")
            
            return [{
                "success": False,
                "by_user_action": True,
                "youtube_video": youtube_video,
                "message": "was canceled by the user."
            }]

        logger.info("suitable stream(s) successfully chosen")

        if put_in_custom_folder:
            download_directory = safe_join_directory(
                download_directory, 
                await youtube_video.title(), 
                f"Video ({youtube_video.video_id})"
            )
            download_directory.mkdir(parents=True, exist_ok=True)

        for stream in chosen_streams:
            result = await self._custom_stream_download(
                stream,
                download_directory,
                filename_prefix
            )

            results.append(result)

        if all(map(lambda r: not r["success"], results)) and put_in_custom_folder:
            download_directory.rmdir()

        if delete_temporary_files:
            spaced_print("Removing temporary files...")
            self._temporary_file_storage.remove_temporary_files()
            spaced_print("Temporary files successfully removed.")

        logger.info("video download for %s was successful", youtube_video.video_id)
        return results


    async def _custom_stream_download(
        self, 
        stream: Stream,
        download_directory: Path,
        filename_prefix: Optional[str]
    ) -> VideoDownloadResult:
        should_convert = self._configuration["download_behavior_configuration"]["convert_custom_downloads"] 
        custom_file_extension = self._configuration["download_behavior_configuration"]["convert_custom_downloads_to"]
        should_skip_existing_files = self._configuration["download_behavior_configuration"]["skip_existing_files"]

        youtube_video = cast(AsyncYouTube, get_youtube_from_stream(stream))

        if not should_convert or stream.subtype == custom_file_extension:
            download_result = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                should_skip_existing_files,
                f"{filename_prefix or ''}{stream.itag}-"
            )

            return download_result

        ensure_can_use_ffmpeg(
            self._ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_custom_downloads_to"
        )

        try:
            converted_file_path: Path = resolve_safe_file_path(
                download_directory, 
                stream.default_filename, 
                f"Video ({youtube_video.video_id})", 
                f"{filename_prefix or ''}{stream.itag}-", 
                custom_file_extension
            )
        except ImpossibleDownloadPath as exception:
            logger.debug(
                "download_cancelled due to an impossible download path video_id=%s download_path=%s", 
                youtube_video.video_id,
                download_directory
            )

            return {
                "success": False,
                "by_user_action": False,
                "youtube_video": youtube_video,
                "message": str(exception)
            }

        if converted_file_path.exists() and should_skip_existing_files:
            logger.debug(
                "download_cancelled due to a file already existing with the same name for video_id=%s converted_file_path=%s", 
                youtube_video.video_id, 
                converted_file_path
            )

            return {
                "success": False,
                "by_user_action": False,
                "youtube_video": youtube_video,
                "message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=converted_file_path)
            }

        logger.info("beginning stream download")

        temporary_video_download_result = await self._download_stream(
            youtube_video,
            stream,
            TEMPORARY_FILES_DIRECTORY_PATH,
            False,
            filename_prefix=f"{filename_prefix or ''}{stream.itag}-"
        )

        if temporary_video_download_result["success"] is False:
            logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

            return temporary_video_download_result

        self._temporary_file_storage.register_temporary_file(temporary_video_download_result["download_path"])

        logger.info("stream download successful")
        logger.info("beginning video conversion to %s", custom_file_extension)

        conversion_bar = self._progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        conversion_result = await convert_file(
            cast(Path, self._ffmpeg_executable_path), 
            ( 
                FFmpegFileArgs(temporary_video_download_result["download_path"]), 
            ), 
            ( 
                FFmpegFileArgs(converted_file_path, { "c": "copy" }),
            ),
            ( 
                FFmpegOptionArgs("y"),
            ),
            conversion_bar.on_progress
        )

        conversion_bar.close(ensure_full=conversion_result.success)
        spaced_print("Conversion was successful.")

        logger.info("video conversion to %s successful", custom_file_extension)
        logger.info("stream download %s for %s was successful", stream.itag, youtube_video.video_id)

        return {
            "success": True,
            "youtube_video": youtube_video,
            "download_path": converted_file_path
        }
