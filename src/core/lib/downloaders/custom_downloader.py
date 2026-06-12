import logging

from typing import Optional, cast
from pathlib import Path
from pytubefix import AsyncYouTube, Stream

from ..protocols import VideoDownloaderProtocol
from ...custom_types import VideoDownloadResult, Configuration
from ..factories import ProgressBarFactory
from ...exceptions import ImpossibleDownloadPath
from ...utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, APPLICATION_LOGGER_NAME, UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, TEMPORARY_FILES_DIRECTORY_PATH
from ...utilities.validation import ensure_can_use_ffmpeg
from ...utilities.console import pick_from_streams, spaced_print
from ...utilities.file_conversion import convert_file
from ...utilities.os import resolve_safe_file_path
from ...utilities.pytubefix_extensions import get_youtube_from_stream

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class CustomDownloader(VideoDownloaderProtocol[list[VideoDownloadResult]]):
    def __init__(
        self, 
        configuration: Configuration, 
        progress_bar_factory: ProgressBarFactory,
        ffmpeg_executable_path: Optional[Path] = None
    ) -> None:
        self._configuration = configuration
        self._progress_bar_factory = progress_bar_factory
        self._ffmpeg_executable_path = ffmpeg_executable_path

    async def download(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        results: list[VideoDownloadResult] = []

        logger.debug(
            "convert_custom_downloads=%s skip_existing_files=%s", 
            self._configuration["download_behavior_configuration"]["convert_custom_downloads"] , 
            self._configuration["download_behavior_configuration"]["skip_existing_files"]
        )

        chosen_streams = pick_from_streams(await youtube_video.streams())

        for stream in chosen_streams:
            result = await self._inner_download(
                stream,
                download_directory,
                filename_prefix
            )

            results.append(result)

        return results


    async def undo_download(self, result: list[VideoDownloadResult]) -> None:
        ...


    async def _inner_download(
        self, 
        stream: Stream,
        download_directory: Path,
        filename_prefix: Optional[str]
    ) -> VideoDownloadResult:
        should_convert = self._configuration["download_behavior_configuration"]["convert_custom_downloads"] 
        custom_file_extension = self._configuration["download_behavior_configuration"]["convert_custom_downloads_to"]
        should_skip_existing_files = self._configuration["download_behavior_configuration"]["skip_existing_files"]

        youtube_video = cast(AsyncYouTube, get_youtube_from_stream(stream))

        if not should_convert:
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
            logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

            download_directory.rmdir()

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str(exception)
            }

        if converted_file_path.exists() and should_skip_existing_files:
            logger.debug(
                "download_cancelled due to a file already existing with the same name for video_id=%s converted_file_path=%s", 
                youtube_video.video_id, 
                converted_file_path
            )

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=converted_file_path)
            }
        
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

        conversion_bar = self._progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self._ffmpeg_executable_path), 
            [ temporary_video_download_result["download_path"] ], 
            [ converted_file_path ],
            [ "y" ],
            conversion_bar.on_progress
        )

        conversion_bar.close()
        spaced_print("Conversion was successful!") 

        return {
            "success": True,
            "youtube_video": youtube_video,
            "download_path": converted_file_path,
            "error_message": None
        }