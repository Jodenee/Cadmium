import logging

from typing import Optional, cast
from pathlib import Path
from pytubefix import AsyncYouTube, Stream

from ..protocols import VideoDownloaderProtocol
from ..factories import ProgressBarFactory
from ..downloaders import VideoOnlyDownloader, AudioOnlyDownloader
from ...custom_types import VideoDownloadResult, Configuration
from ...exceptions import ImpossibleDownloadPath
from ...utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, APPLICATION_LOGGER_NAME, UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, TEMPORARY_FILES_DIRECTORY_PATH
from ...utilities.validation import ensure_can_use_ffmpeg
from ...utilities.console import spaced_print
from ...utilities.file_conversion import convert_file
from ...utilities.os import resolve_safe_file_path, safe_join_directory

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class BestOfBothDownloader(VideoDownloaderProtocol[list[VideoDownloadResult]]):
    def __init__(
        self, 
        configuration: Configuration, 
        progress_bar_factory: ProgressBarFactory,
        video_only_downloader: VideoOnlyDownloader,
        audio_only_downloader: AudioOnlyDownloader,
        ffmpeg_executable_path: Optional[Path] = None
    ) -> None:
        self._configuration = configuration
        self._progress_bar_factory = progress_bar_factory
        self._ffmpeg_executable_path = ffmpeg_executable_path
        self._video_only_downloader = video_only_downloader
        self._audio_only_downloader = audio_only_downloader


    async def download(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        merge_download = self._configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"]
        results = list[VideoDownloadResult]

        logger.debug("merge_download=%s", self._configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"])

        if merge_download:
            results = await self._download_merged(youtube_video, download_directory, filename_prefix) 
        else: 
            results = await self._download_separate(youtube_video, download_directory, filename_prefix)
        
        logger.info("video download for %s was successful", youtube_video.video_id)

        return results


    async def undo_download(self, result: list[VideoDownloadResult]) -> None:
        ...


    async def _download_separate(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        true_download_directory: Path = safe_join_directory(
            download_directory, 
            await youtube_video.title(), 
            f"Video ({youtube_video.video_id})"
        )
        true_download_directory.mkdir(exist_ok=True, parents=True)

        video_only_download_result: VideoDownloadResult
        audio_only_download_result: VideoDownloadResult

        video_only_download_result = await self._video_only_downloader.download(
            youtube_video,
            true_download_directory,
            f"{filename_prefix or ""}Video-"
        )

        audio_only_download_result = await self._audio_only_downloader.download(
            youtube_video,
            true_download_directory,
            f"{filename_prefix or ""}Audio-"
        )

        # Clean up directory if nothing is downloaded
        if not video_only_download_result["success"] or not audio_only_download_result["success"]:
            spaced_print("Removing temporary files...")
            
            if video_only_download_result["success"] is True:
                video_only_download_result["download_path"].unlink()

            if audio_only_download_result["success"] is True:
                audio_only_download_result["download_path"].unlink()

            true_download_directory.rmdir()

            spaced_print("Temporary files successfully removed.")
            logger.info("temporary files successfully removed")

        return [ video_only_download_result, audio_only_download_result ]


    async def _download_merged(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        custom_file_extension = self._configuration["download_behavior_configuration"]["best_of_both_merged_file_format"]
        should_skip_existing_files = self._configuration["download_behavior_configuration"]["skip_existing_files"]
        delete_temporary_files = self._configuration["download_behavior_configuration"]["automatically_delete_temporary_files_after_download"]

        logger.info("searching for most suitable streams to download")

        video_stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(is_dash=True, only_video=True)
            .first()
        )
        audio_stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(is_dash=True, only_audio=True)
            .desc()
            .first()
        )

        if video_stream == None or audio_stream == None:
            logger.debug(
                "download_cancelled could not find a suitable stream for the video or audio stream video_stream=%s audio_stream=%s", 
                youtube_video.video_id, 
                video_stream, 
                audio_stream
            )

            return [{
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
            }]
        
        logger.info("suitable stream successfully found")
        logger.debug(
            "video_id=%s video_stream_itag=%s audio_stream_itag=%s should_skip_existing_files=%s custom_file_extension=%s delete_temporary_files=%s",
            youtube_video.video_id,
            video_stream.itag,
            audio_stream.itag, 
            should_skip_existing_files,
            custom_file_extension,
            delete_temporary_files
        )

        ensure_can_use_ffmpeg(
            self._ffmpeg_executable_path, 
            custom_file_extension, 
            "best_of_both_merged_file_format"
        )

        try:
            converted_file_path: Path = resolve_safe_file_path(
                download_directory, 
                video_stream.default_filename, 
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

            return [{
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str(exception)
            }]

        if converted_file_path.exists() and should_skip_existing_files:
            logger.debug(
                "download_cancelled due to a file already existing with the same name for video_id=%s converted_file_path=%s", 
                youtube_video.video_id, 
                converted_file_path
            )

            return [{
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=converted_file_path)
            }]

        logger.info("beginning stream download")

        temporary_video_download_result = await self._download_stream(
            youtube_video,
            video_stream,
            TEMPORARY_FILES_DIRECTORY_PATH,
            False,
            "Video-"
        )

        temporary_audio_download_result = await self._download_stream(
            youtube_video,
            audio_stream,
            TEMPORARY_FILES_DIRECTORY_PATH,
            False,
            "Audio-"
        )

        if temporary_video_download_result["success"] is False or temporary_audio_download_result["success"] is False:
            logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

            return [ temporary_video_download_result, temporary_audio_download_result ]

        logger.info("stream download successful")
        logger.info("beginning video conversion to %s", custom_file_extension)

        conversion_bar = self._progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(video_stream.durationMs)
        )

        await convert_file(
            cast(Path, self._ffmpeg_executable_path), 
            [ 
                ( temporary_video_download_result["download_path"], None ),
                ( temporary_audio_download_result["download_path"], None ) 
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
            logger.debug("removing temporary file path=%s video_id=%s", temporary_video_download_result["download_path"], youtube_video.video_id)
            logger.debug("removing temporary file path=%s video_id=%s", temporary_audio_download_result["download_path"], youtube_video.video_id)
            
            spaced_print("Removing temporary files...")

            temporary_video_download_result["download_path"].unlink()
            temporary_audio_download_result["download_path"].unlink()

            spaced_print("Temporary files successfully removed.")
            logger.info("temporary files successfully removed")

        return [{
            "success": True,
            "youtube_video": youtube_video,
            "download_path": converted_file_path,
            "error_message": None
        }]
