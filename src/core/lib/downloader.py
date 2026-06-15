import logging

from pytubefix.async_youtube import AsyncYouTube
from pytubefix import Playlist, Stream, StreamQuery, Channel
from pathlib import Path
from typing import Optional, cast

from ..custom_types.collection_download_result import CollectionDownloadResult
from ..utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, VIDEO_DOWNLOAD_CANCELLED_ERROR_MESSAGE, APPLICATION_LOGGER_NAME
from ..utilities.file_conversion import convert_file
from ..utilities.validation import ensure_can_use_ffmpeg
from ..utilities.console import pick_from_streams, spaced_print
from ..utilities.os import resolve_safe_file_path, safe_join_directory
from ..utilities.pytubefix_extensions import stream_repr

from .factories import ProgressBarFactory
from .protocols import VideoDownloaderProtocol
from .downloaders import VideoDownloader, VideoOnlyDownloader, AudioOnlyDownloader, BestOfBothDownloader, CustomDownloader
from ..custom_types import Configuration, VideoDownloadResult
from ..enums import DownloadFormat
from ..exceptions import ImpossibleDownloadPath

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class Downloader:
    def __init__(
        self, 
        configuration: Configuration, 
        progress_bar_factory: ProgressBarFactory,
        temporary_files_directory_path: Path, 
        ffmpeg_executable_path: Optional[Path] = None
    ) -> None:
        self.configuration = configuration
        self.progress_bar_factory = progress_bar_factory
        self.temporary_files_directory_path = temporary_files_directory_path
        self.ffmpeg_executable_path = ffmpeg_executable_path

        # Define downloader subclasses

        self.video_downloader = VideoDownloader(
            self.configuration,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.video_only_downloader = VideoOnlyDownloader(
            self.configuration,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.audio_only_downloader = AudioOnlyDownloader(
            self.configuration,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.best_of_both_downloader = BestOfBothDownloader(
            self.configuration,
            self.progress_bar_factory,
            self.video_only_downloader,
            self.audio_only_downloader,
            self.ffmpeg_executable_path
        )
        self.custom_downloader = CustomDownloader(
            self.configuration,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )

        self.downloaders: dict[
            DownloadFormat, VideoDownloaderProtocol[VideoDownloadResult] | VideoDownloaderProtocol[list[VideoDownloadResult]]
        ] = {
            DownloadFormat.VIDEO: self.video_downloader,
            DownloadFormat.VIDEO_ONLY: self.video_only_downloader,
            DownloadFormat.AUDIO_ONLY: self.audio_only_downloader,
            DownloadFormat.BEST_OF_BOTH: self.best_of_both_downloader,
            DownloadFormat.CUSTOM: self.custom_downloader,
        }


    async def download_video(
        self, 
        youtube_video_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> list[VideoDownloadResult]:
        logger.debug("downloading_video video_url=%s download_format=%s", youtube_video_url, download_format.name)

        youtube_video: AsyncYouTube = AsyncYouTube(youtube_video_url)
        streams: StreamQuery = await youtube_video.streams()
        download_results: list[VideoDownloadResult] = []

        logger.info("beginning video download for %s", youtube_video.video_id)

        if len(streams) == 0: 
            logger.debug("downloading_video url=%s cancelled due to have no streams available", youtube_video_url)
            logger.info("video download for %s was unsuccessful", youtube_video.video_id)

            return [{
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": f"Video ({await youtube_video.title()}) doesn't have any available streams."
            }]
        
        result: VideoDownloadResult | list[VideoDownloadResult] = ( 
            await self.downloaders[download_format]
                .download(youtube_video, download_directory, filename_prefix)
        )

        if isinstance(result, list):
            download_results = result
        else: 
            download_results.append(result)

        for download_result in download_results:
            if download_result["success"] is True:
                logger.debug(
                    "successful_download video_id=%s download_path=%s", 
                    download_result["youtube_video"].video_id, 
                    download_result["download_path"]
                )
            else:
                logger.debug(
                    "failed_download video_id=%s error_message=%s", 
                    download_result["youtube_video"].video_id, 
                    download_result["error_message"]
                )

        logger.info("video download for %s has concluded", youtube_video.video_id)

        return download_results


    async def download_playlist(
        self, 
        playlist_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> CollectionDownloadResult:
        logger.debug("downloading_playlist playlist_url=%s download_format=%s", playlist_url, download_format)

        playlist: Playlist = Playlist(playlist_url)
        true_download_directory: Path = download_directory

        logger.debug("put_playlist_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, playlist.title, f"Playlist ({playlist.playlist_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: list[VideoDownloadResult] = []

        for video_url in playlist.url_generator():
            results = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory
            )

            for result in results:
                if not result["success"]:
                    failed_downloads.append(result)

        logger.info("finished downloading playlist %s", playlist_url)

        return {
            "success": len(failed_downloads) == 0,
            "collection_type": "Playlist",
            "collection_name": playlist.title,
            "failed_downloads": failed_downloads,
            "download_directory_path": true_download_directory
        }


    async def download_channel(
        self, 
        channel_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> CollectionDownloadResult:
        logger.debug("downloading_channel channel_url=%s download_format=%s", channel_url, download_format)

        channel: Channel = Channel(channel_url)
        true_download_directory: Path = download_directory

        logger.debug("put_channel_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, channel.channel_name, f"Channel ({channel.channel_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: list[VideoDownloadResult] = []

        for video_url in channel.video_urls:
            results = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory
            )

            for result in results:
                if not result["success"]:
                    failed_downloads.append(result)

        logger.info("finished downloading channel %s", channel_url)

        return {
            "success": len(failed_downloads) == 0,
            "collection_type": "Channel",
            "collection_name": channel.channel_name,
            "failed_downloads": failed_downloads,
            "download_directory_path": true_download_directory,
        }


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

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen stream info: {stream_repr(stream)}")

        download_bar = self.progress_bar_factory.download(
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
