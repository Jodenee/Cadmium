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
from ...utilities.console import spaced_print
from ...utilities.file_conversion import convert_file
from ...utilities.os import resolve_safe_file_path

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class VideoDownloader(VideoDownloaderProtocol[VideoDownloadResult]):
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
    ) -> VideoDownloadResult:
        should_convert = self._configuration["download_behavior_configuration"]["convert_video_downloads"] 
        custom_file_extension = self._configuration["download_behavior_configuration"]["convert_video_downloads_to"]
        should_skip_existing_files = self._configuration["download_behavior_configuration"]["skip_existing_files"]
        delete_temporary_files = self._configuration["download_behavior_configuration"]["automatically_delete_temporary_files_after_download"]

        logger.info("searching for most suitable stream to download")

        stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(progressive=True, only_audio=False, only_video=False)
            .desc()
            .first()
        )

        if stream == None:
            logger.debug(
                "download_cancelled could not find a suitable stream video_id=%s", 
                youtube_video.video_id
            )

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
            }

        logger.info("suitable stream successfully found")
        logger.debug(
            "video_id=%s stream_itag=%s should_convert=%s should_skip_existing_files=%s custom_file_extension=%s delete_temporary_files=%s",
            youtube_video.video_id,
            stream.itag,
            should_convert, 
            should_skip_existing_files,
            custom_file_extension,
            delete_temporary_files
        )

        # Early return when not converting to another file format
        if not should_convert or stream.subtype == custom_file_extension:
            download_result: VideoDownloadResult = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                should_skip_existing_files,
                filename_prefix
            )

            return download_result

        ensure_can_use_ffmpeg(
            self._ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_video_downloads_to"
        )

        try:
            converted_file_path: Path = resolve_safe_file_path(
                download_directory, 
                stream.default_filename, 
                f"Video ({youtube_video.video_id})", 
                filename_prefix, 
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
                "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=download_directory)
            }

        logger.info("beginning stream download")

        temporary_video_download_result = await self._download_stream(
            youtube_video,
            stream,
            TEMPORARY_FILES_DIRECTORY_PATH, 
            False,
            filename_prefix
        )

        if temporary_video_download_result["success"] is False:
            logger.debug(
                "downloading_video temporary file download failed video_id=%s", 
                youtube_video.video_id
            )
            
            return temporary_video_download_result
        
        logger.info("stream download successful")
        logger.info("beginning video conversion to %s", custom_file_extension)

        conversion_bar = self._progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self._ffmpeg_executable_path), 
            [ 
                ( temporary_video_download_result["download_path"], None ) 
            ], 
            [ 
                ( converted_file_path, None ) 
            ],
            [ { "y": None } ],
            conversion_bar.on_progress
        )

        conversion_bar.close()
        spaced_print("Conversion was successful.")

        logger.info("video conversion to %s successful", custom_file_extension)

        if delete_temporary_files:
            logger.info("removing temporary files")
            logger.debug(
                "removing temporary file path=%s video_id=%s", 
                temporary_video_download_result["download_path"], 
                youtube_video.video_id
            )

            spaced_print("Removing temporary files...")

            temporary_video_download_result["download_path"].unlink()

            spaced_print("Temporary files successfully removed.")
            logger.info("temporary files successfully removed")

        logger.info("video download for %s was successful", youtube_video.video_id)

        return {
            "success": True,
            "youtube_video": youtube_video,
            "download_path": converted_file_path,
            "error_message": None
        }


    async def undo_download(self, result: VideoDownloadResult) -> None:
        ...
