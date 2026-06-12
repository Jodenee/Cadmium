import logging

from typing import Protocol, Optional
from abc import abstractmethod
from pathlib import Path
from pytubefix import AsyncYouTube, Stream

from ...exceptions import ImpossibleDownloadPath
from ...custom_types import VideoDownloadResult, Configuration
from ...utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, APPLICATION_LOGGER_NAME, VIDEO_DOWNLOAD_CANCELLED_ERROR_MESSAGE
from ...utilities.console import spaced_print
from ..factories import ProgressBarFactory
from ...utilities.os import resolve_safe_file_path
from ...utilities.pytubefix_extensions import stream_repr

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class VideoDownloaderProtocol[ReturnType](Protocol):
    _configuration: Configuration
    _progress_bar_factory: ProgressBarFactory
    _ffmpeg_executable_path: Optional[Path]

    @abstractmethod
    async def download(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> ReturnType:
        ...

    @abstractmethod
    async def undo_download(self, result: ReturnType) -> None:
        ...

    async def _download_stream(
        self, 
        youtube_video: AsyncYouTube, 
        stream: Stream, 
        download_directory: Path, 
        skip_existing_files: bool,
        filename_prefix: Optional[str] = None
    ) -> VideoDownloadResult:
        youtube_video_title = await youtube_video.title()
        fallback_filename = f"Video ({youtube_video.video_id})" if stream.includes_video_track else f"Audio ({youtube_video.video_id})"

        logger.debug(
            "downloading_stream video_id=%s stream_itag=%s download_directory=%s video_title=%s", 
            youtube_video.video_id, 
            stream.itag, 
            download_directory, 
            youtube_video_title
        )
        
        try:
            video_full_file_path = resolve_safe_file_path(
                download_directory,
                stream.default_filename,
                fallback_filename,
                filename_prefix
            )
        except ImpossibleDownloadPath as exception:
            logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str(exception)
            }
        
        if video_full_file_path.exists() and skip_existing_files:
            logger.debug("download_cancelled A file already existing with the same name video_id=%s stream_itag=%s path=%s", youtube_video.video_id, stream.itag, video_full_file_path)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=video_full_file_path)
            }

        if self._configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen stream info: {stream_repr(stream)}")

        download_bar = self._progress_bar_factory.download(
            f"Downloading ({youtube_video_title})", 
            stream.filesize,
            youtube_video
        )

        download_path: Optional[str] = stream.download(
            output_path=str(download_directory), 
            skip_existing=skip_existing_files,
            filename=video_full_file_path.name
        )

        download_bar.close()

        if (download_path == None):
            logger.debug("download_cancelled due to user intervention video_id=%s stream_itag=%s", youtube_video.video_id, stream.itag)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(VIDEO_DOWNLOAD_CANCELLED_ERROR_MESSAGE, video_title=youtube_video_title)
            } 
        
        return {
            "success": True,
            "youtube_video": youtube_video,
            "download_path": Path(download_path),
            "error_message": None
        } 
