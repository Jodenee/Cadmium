import logging

from pytubefix.async_youtube import AsyncYouTube
from pytubefix import Playlist, StreamQuery, Channel
from pathlib import Path
from typing import Optional, cast

from ..lib.temporary_file_storage import TemporaryFileStorage
from ..custom_types.collection_download_result import CollectionDownloadResult
from ..utilities.constants import APPLICATION_LOGGER_NAME
from ..utilities.os import safe_join_directory
from ..utilities.console import spaced_print

from .factories import ProgressBarFactory
from .protocols import VideoDownloaderProtocol
from .downloaders import VideoDownloader, VideoOnlyDownloader, AudioOnlyDownloader, BestOfBothDownloader, CustomDownloader
from ..custom_types import Configuration, VideoDownloadResult, VideoDownloadResultFailure
from ..enums import DownloadFormat

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class Downloader:
    "A singleton wrapper class for all the different downloader variants"

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
        self.temporary_file_storage = TemporaryFileStorage()

        # Define downloader variants

        self.video_downloader = VideoDownloader(
            self.configuration,
            self.temporary_file_storage,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.video_only_downloader = VideoOnlyDownloader(
            self.configuration,
            self.temporary_file_storage,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.audio_only_downloader = AudioOnlyDownloader(
            self.configuration,
            self.temporary_file_storage,
            self.progress_bar_factory,
            self.ffmpeg_executable_path
        )
        self.best_of_both_downloader = BestOfBothDownloader(
            self.configuration,
            self.temporary_file_storage,
            self.progress_bar_factory,
            self.video_only_downloader,
            self.audio_only_downloader,
            self.ffmpeg_executable_path
        )
        self.custom_downloader = CustomDownloader(
            self.configuration,
            self.temporary_file_storage,
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
        filename_prefix: Optional[str] = None,
        clear_temporary_files: bool = True
    ) -> list[VideoDownloadResult]:
        """Download a youtube video

        Args:
            youtube_video_url: URL to the video.
            download_format: `DownloadFormat` enum to determine which stream to download.
            download_directory: `Path` to the directory where the video will be downloaded.
            filename_prefix: Optional prefix to append to the downloaded filename.

        Returns:
            A list of `VideoDownloadResult`.
        """

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
                "by_user_action": False,
                "youtube_video": youtube_video,
                "message": f"Video ({await youtube_video.title()}) doesn't have any available streams."
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
                    "failed_download video_id=%s message=%s", 
                    download_result["youtube_video"].video_id, 
                    download_result["message"]
                )

        logger.info("video download for %s has concluded", youtube_video.video_id)

        return download_results


    async def download_playlist(
        self, 
        playlist_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> CollectionDownloadResult:
        """Download the contents of a YouTube playlist.

        Args:
            playlist_url: URL to the playlist.
            download_format: `DownloadFormat` enum to determine which stream to download.
            download_directory: `Path` to the directory where the playlist contents will be downloaded.

        Returns:
            A `CollectionDownloadResult`.
        """

        logger.debug("downloading_playlist playlist_url=%s download_format=%s", playlist_url, download_format)

        playlist: Playlist = Playlist(playlist_url)
        true_download_directory: Path = download_directory

        logger.debug("put_playlist_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, playlist.title, f"Playlist ({playlist.playlist_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: list[VideoDownloadResultFailure] = []

        for video_url in playlist.url_generator():
            logger.debug("downloading playlist video video_url=%s", video_url)

            results = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory,
                clear_temporary_files=False
            )
            
            failed_downloads.extend(
                cast(
                    tuple[VideoDownloadResultFailure, ...], 
                    tuple(filter(lambda r: r["success"] is False, results))
                )
            )

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
        """Download the contents of a YouTube channel.

        Args:
            channel_url: URL to the channel.
            download_format: `DownloadFormat` enum to determine which stream to download.
            download_directory: `Path` to the directory where the channel contents will be downloaded.

        Returns:
            A `CollectionDownloadResult`.
        """

        logger.debug("downloading_channel channel_url=%s download_format=%s", channel_url, download_format)

        channel: Channel = Channel(channel_url)
        true_download_directory: Path = download_directory

        logger.debug("put_channel_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, channel.channel_name, f"Channel ({channel.channel_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: list[VideoDownloadResultFailure] = []

        for video_url in channel.video_urls:
            logger.debug("downloading channel video video_url=%s", video_url)

            results = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory,
                clear_temporary_files=False
            )

            failed_downloads.extend(
                cast(
                    tuple[VideoDownloadResultFailure, ...], 
                    tuple(filter(lambda r: r["success"] is False, results))
                )
            )

        logger.info("finished downloading channel %s", channel_url)

        return {
            "success": len(failed_downloads) == 0,
            "collection_type": "Channel",
            "collection_name": channel.channel_name,
            "failed_downloads": failed_downloads,
            "download_directory_path": true_download_directory,
        }
