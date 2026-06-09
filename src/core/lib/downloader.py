import logging

from pytubefix.async_youtube import AsyncYouTube
from pytubefix import Playlist, Stream, StreamQuery, Channel
from pathlib import Path
from typing import List, Optional, cast

from ..custom_types.collection_download_result import CollectionDownloadResult
from ..utilities.constants import ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, VIDEO_DOWNLOAD_CANCELLED_ERROR_MESSAGE, APPLICATION_LOGGER_NAME
from ..utilities.file_conversion import convert_file
from ..utilities.validation import ensure_can_use_ffmpeg
from ..utilities.console import pick_from_streams, spaced_print
from ..utilities.os import resolve_safe_file_path, safe_join_directory
from ..utilities.pytubefix_extensions import stream_repr

from ..lib import ProgressBarFactory
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


    async def download_video(
        self, 
        youtube_video_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> List[VideoDownloadResult]:
        logger.debug("downloading_video video_url=%s download_format=%s", youtube_video_url, download_format)

        youtube_video: AsyncYouTube = AsyncYouTube(youtube_video_url)
        streams: StreamQuery = await youtube_video.streams()
        download_results: List[VideoDownloadResult] = []

        if len(streams) == 0: 
            logger.debug("downloading_video url=%s cancelled due to have no streams available", youtube_video_url)

            return [{
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": f"Video ({await youtube_video.title()}) doesn't have any available streams."
            }]

        if download_format == DownloadFormat.VIDEO:
            video_download_result = await self._download_video(youtube_video, download_directory, filename_prefix)

            download_results.append(video_download_result)
        elif download_format == DownloadFormat.VIDEO_ONLY:
            video_only_download_result = await self._download_video_only(youtube_video, download_directory, filename_prefix)

            download_results.append(video_only_download_result)
        elif download_format == DownloadFormat.AUDIO_ONLY:
            audio_only_download_result = await self._download_audio_only(youtube_video, download_directory, filename_prefix)

            download_results.append(audio_only_download_result)
        elif download_format == DownloadFormat.BEST_OF_BOTH:
            download_results = await self._download_best_of_both(youtube_video, download_directory, filename_prefix)
        elif download_format == DownloadFormat.CUSTOM:
            chosen_streams: List[Stream] = pick_from_streams(streams)

            logger.debug("put_custom_streams_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_custom_streams_in_folder"])

            if self.configuration["quality_of_life_configuration"]["put_custom_streams_in_folder"]:
                download_directory = safe_join_directory(
                    download_directory,
                    await youtube_video.title(),
                    f"Video ({youtube_video.video_id})"
                )

                download_directory.mkdir(exist_ok=True, parents=True)

            download_results = await self._download_custom(youtube_video, chosen_streams, download_directory, filename_prefix)

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

        logger.info("finished downloading video %s", youtube_video_url)

        return download_results


    async def download_playlist(
        self, 
        playlist_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> CollectionDownloadResult:
        logger.info("downloading playlist playlist_url=%s download_format=%s", playlist_url, download_format)

        playlist: Playlist = Playlist(playlist_url)
        true_download_directory: Path = download_directory

        logger.debug("put_playlist_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, playlist.title, f"Playlist ({playlist.playlist_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: List[VideoDownloadResult] = []

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
        logger.info("downloading channel channel_url=%s download_format=%s", channel_url, download_format)

        channel: Channel = Channel(channel_url)
        true_download_directory: Path = download_directory

        logger.debug("put_channel_videos_in_folder=%s", self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"])

        if self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, channel.channel_name, f"Channel ({channel.channel_id})")
            true_download_directory.mkdir(exist_ok=True, parents=True)

        logger.debug("true_download_directory=%s", true_download_directory)

        failed_downloads: List[VideoDownloadResult] = []

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


    async def _download_video(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> VideoDownloadResult:
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_downloads_to"]
        should_skip_existing_files = self.configuration["download_behavior_configuration"]["skip_existing_files"]
        stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(progressive=True, only_audio=False, only_video=False)
            .desc()
            .first()
        )

        if stream == None:
            logger.debug("download_cancelled could not find a suitable stream video_id=%s", youtube_video.video_id)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
            }

        logger.debug("should_convert=%s should_skip_existing_files=%s", should_convert, should_skip_existing_files)

        # Early return when not converting to another file format
        if not should_convert:
            download_result = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                should_skip_existing_files,
                filename_prefix
            )

            return download_result
        
        logger.debug("custom_file_extension=%s", custom_file_extension)

        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
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
            logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

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
        
        temporary_video_download_result = await self._download_stream(
            youtube_video,
            stream,
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )

        if temporary_video_download_result["success"] is False:
            logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)
            
            return temporary_video_download_result

        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
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
    

    async def _download_video_only(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> VideoDownloadResult:
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_only_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_only_downloads_to"]
        should_skip_existing_files = self.configuration["download_behavior_configuration"]["skip_existing_files"]
        stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(is_dash=True, only_video=True)
            .first()
        )

        if stream == None:
            logger.debug("could not find a suitable stream for video_id=%s", youtube_video.video_id)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
            }

        logger.debug("should_convert=%s should_skip_existing_files=%s", should_convert, should_skip_existing_files)

        # Early return when not converting to another file format
        if not should_convert:
            download_result = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                should_skip_existing_files,
                filename_prefix
            )

            return download_result
        
        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_video_only_downloads_to"
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
            logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

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
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )

        if temporary_video_download_result["success"] is False:
            logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

            return temporary_video_download_result

        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
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


    async def _download_audio_only(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> VideoDownloadResult:
        should_convert = self.configuration["download_behavior_configuration"]["convert_audio_only_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_audio_only_downloads_to"]
        stream: Optional[Stream] = (
            (await youtube_video.streams())
            .filter(is_dash=True, only_audio=True)
            .desc()
            .first()
        )

        if stream == None:
            logger.debug("could not find a suitable stream for video_id=%s", youtube_video.video_id)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
            }

        # Early return when not converting to another file format
        if not should_convert:
            download_result = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename_prefix
            )

            return download_result

        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_audio_only_downloads_to"
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
            logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str(exception)
            }

        if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            return {
                "success": False,
                "youtube_video": youtube_video,
                "download_path": None,
                "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=converted_file_path)
            }

        temporary_video_download_result = await self._download_stream(
            youtube_video,
            stream,
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )

        if temporary_video_download_result["success"] is False:
            logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

            return temporary_video_download_result
        
        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
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


    async def _download_best_of_both(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> List[VideoDownloadResult]:   
        logger.debug("merge_best_of_both_downloads_into_one_file=%s", self.configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"])

        if not self.configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"]:
            true_download_directory: Path = safe_join_directory(
                download_directory, 
                await youtube_video.title(), 
                f"Video ({youtube_video.video_id})"
            )
            true_download_directory.mkdir(exist_ok=True, parents=True)

            video_only_download_result: VideoDownloadResult
            audio_only_download_result: VideoDownloadResult

            video_only_download_result = await self._download_video_only(
                youtube_video,
                true_download_directory,
                "Video-"
            )

            audio_only_download_result = await self._download_audio_only(
                youtube_video,
                true_download_directory,
                "Audio-"
            )

            # Clean up directory if nothing is downloaded
            if not video_only_download_result["success"] or not audio_only_download_result["success"]:
                true_download_directory.rmdir()

            return [ video_only_download_result, audio_only_download_result ]
        else:
            custom_file_extension = self.configuration["download_behavior_configuration"]["best_of_both_merged_file_format"]
            should_skip_existing_files = self.configuration["download_behavior_configuration"]["skip_existing_files"]
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

            logger.debug("should_skip_existing_files=%s", should_skip_existing_files)

            if video_stream == None or audio_stream == None:
                logger.debug("download_cancelled could not find a suitable stream for the video or audio stream video_stream=%s audio_stream=%s", youtube_video.video_id, video_stream, audio_stream)

                return [{
                    "success": False,
                    "youtube_video": youtube_video,
                    "download_path": None,
                    "error_message": str.format(UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE, video_title=youtube_video.title)
                }]
            
            ensure_can_use_ffmpeg(
                self.ffmpeg_executable_path, 
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
                logger.debug("download_cancelled due to an impossible download path video_id=%s", youtube_video.video_id)

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

            temporary_video_download_result = await self._download_stream(
                youtube_video,
                video_stream,
                self.temporary_files_directory_path,
                False,
                "Video-"
            )

            temporary_audio_download_result = await self._download_stream(
                youtube_video,
                audio_stream,
                self.temporary_files_directory_path,
                False,
                "Audio-"
            )

            if temporary_video_download_result["success"] is False or temporary_audio_download_result["success"] is False:
                logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

                return [ temporary_video_download_result, temporary_audio_download_result ]

            conversion_bar = self.progress_bar_factory.conversion(
                f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
                int(video_stream.durationMs)
            )

            await convert_file(
                cast(Path, self.ffmpeg_executable_path), 
                [ temporary_video_download_result["download_path"], temporary_audio_download_result["download_path"] ], 
                [ converted_file_path ],
                [ "y" ],
                conversion_bar.on_progress
            )

            conversion_bar.close()
            spaced_print("Conversion was successful!")

            return [{
                "success": True,
                "youtube_video": youtube_video,
                "download_path": converted_file_path,
                "error_message": None
            }]


    async def _download_custom(
        self, 
        youtube_video: AsyncYouTube, 
        chosen_streams: List[Stream], 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> List[VideoDownloadResult]:
        should_convert = self.configuration["download_behavior_configuration"]["convert_custom_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_custom_downloads_to"]
        should_skip_existing_files = self.configuration["download_behavior_configuration"]["skip_existing_files"]
        results: List[VideoDownloadResult] = []

        logger.debug("should_convert=%s should_skip_existing_files=%s", should_convert, should_skip_existing_files)

        for stream in chosen_streams:
            if not should_convert:
                download_result = await self._download_stream(
                    youtube_video,
                    stream,
                    download_directory, 
                    should_skip_existing_files,
                    f"{filename_prefix or ''}{stream.itag}-"
                )

                results.append(download_result)

                continue

            ensure_can_use_ffmpeg(
                self.ffmpeg_executable_path, 
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

                results.append({
                    "success": False,
                    "youtube_video": youtube_video,
                    "download_path": None,
                    "error_message": str.format(ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE, path=converted_file_path)
                })
                continue
            
            temporary_video_download_result = await self._download_stream(
                youtube_video,
                stream,
                self.temporary_files_directory_path,
                False,
                filename_prefix=f"{filename_prefix or ''}{stream.itag}-"
            )

            if temporary_video_download_result["success"] is False:
                logger.debug("downloading_video temporary file download failed video_id=%s", youtube_video.video_id)

                results.append(temporary_video_download_result)
                continue

            conversion_bar = self.progress_bar_factory.conversion(
                f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
                int(stream.durationMs)
            )

            await convert_file(
                cast(Path, self.ffmpeg_executable_path), 
                [ temporary_video_download_result["download_path"] ], 
                [ converted_file_path ],
                [ "y" ],
                conversion_bar.on_progress
            )

            conversion_bar.close()
            spaced_print("Conversion was successful!") 

            results.append({
                "success": True,
                "youtube_video": youtube_video,
                "download_path": converted_file_path,
                "error_message": None
            })

        return results
