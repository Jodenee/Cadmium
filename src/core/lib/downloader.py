from typing import List, Optional, cast

from pick import pick, Option
from pytubefix.async_youtube import AsyncYouTube
from pytubefix import YouTube, Playlist, Stream, StreamQuery, Channel
from pytubefix.exceptions import MaxRetriesExceeded
from pathlib import Path

from core.utilities.file_conversion import convert_file
from core.utilities.validation import ensure_can_use_ffmpeg
from core.utilities.console import pick_from_streams, spaced_print
from core.utilities.os import calculate_max_filename_length, resolve_safe_file_path, safe_join_directory, safe_full_filename, safe_os_name, MAX_OS_PATH_LENGTH
from core.utilities.pytubefix_extensions import get_channel_video_urls, stream_repr

from ..lib import ProgressBarFactory
from ..custom_types import Configuration, VideoDownloadResult, PlaylistDownloadResult, FailedDownloadInformation, ChannelDownloadResult
from ..enums import DownloadFormat
from ..exceptions import NoStreamsFoundError, VideoDownloadSkipped, DownloadCancelled, ImpossibleDownloadPath

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
    ) -> VideoDownloadResult:
        youtube_video: AsyncYouTube = AsyncYouTube(youtube_video_url)
        streams: StreamQuery = await youtube_video.streams()
        youtube_video_title: str = await youtube_video.title()

        if len(streams) == 0: 
            raise NoStreamsFoundError(youtube_video_title)

        download_path: Path

        try:
            if download_format == DownloadFormat.VIDEO:
                download_path = await self._download_video(youtube_video, download_directory, filename_prefix)
            elif download_format == DownloadFormat.VIDEO_ONLY:
                download_path = await self._download_video_only(youtube_video, download_directory, filename_prefix)
            elif download_format == DownloadFormat.AUDIO_ONLY:
                download_path = await self._download_audio_only(youtube_video, download_directory, filename_prefix)
            elif download_format == DownloadFormat.BEST_OF_BOTH:
                download_path = await self._download_best_of_both(youtube_video, download_directory, filename_prefix)
            elif download_format == DownloadFormat.CUSTOM:
                chosen_streams: List[Stream] = pick_from_streams(streams)

                if self.configuration["quality_of_life_configuration"]["put_custom_streams_in_folder"]:
                    true_download_directory_name = safe_os_name(
                        await youtube_video.title(),
                        f"Video ({youtube_video.video_id})"
                    ) 
                    download_directory = download_directory / true_download_directory_name

                    if len(str(download_directory)) > MAX_OS_PATH_LENGTH:
                        raise ImpossibleDownloadPath(download_directory)
                    
                    download_directory.mkdir(exist_ok=True)

                download_path = await self._download_custom(youtube_video, chosen_streams, download_directory, filename_prefix)
        except (VideoDownloadSkipped, DownloadCancelled, MaxRetriesExceeded) as exception:
            return {
                "success": False,
                "youtube_video_title": youtube_video_title,
                "download_path": None,
                "error_message": str(exception)
            }

        return {
            "success": True,
            "youtube_video_title": youtube_video_title,
            "download_path": download_path,
            "error_message": None
        }


    async def download_playlist(
        self, 
        playlist_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> PlaylistDownloadResult:
        playlist: Playlist = Playlist(playlist_url)
        true_download_directory: Path = download_directory

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, playlist.title, f"Playlist ({playlist.playlist_id})")
            true_download_directory.mkdir(exist_ok=True)

        failed_downloads: List[FailedDownloadInformation] = []

        for video_url in playlist.url_generator():
            video_download_result = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory
            )

            if not video_download_result["success"]:
                failed_downloads.append({
                    "youtube_video_url":  video_url, 
                    "youtube_video_title": video_download_result["youtube_video_title"], 
                    "error_message": cast(str, video_download_result["error_message"])
                })
                continue

        return {
            "success": len(failed_downloads) == 0,
            "playlist_name": str(playlist.title),
            "failed_downloads": failed_downloads,
            "download_directory_path": true_download_directory,
        }


    async def download_channel(
        self, 
        channel_url: str, 
        download_format: DownloadFormat, 
        download_directory: Path
    ) -> ChannelDownloadResult:
        channel: Channel = Channel(channel_url)
        true_download_directory: Path = download_directory

        if self.configuration["quality_of_life_configuration"]["put_channel_videos_in_folder"]:
            true_download_directory = safe_join_directory(download_directory, channel.channel_name, f"Channel ({channel.channel_id})")
            true_download_directory.mkdir(exist_ok=True)

        failed_downloads: List[FailedDownloadInformation] = []

        for video_url in get_channel_video_urls(channel):
            print(isinstance(video_url, YouTube))
            video_download_result = await self.download_video(
                video_url, 
                download_format, 
                true_download_directory
            )

            if not video_download_result["success"]:
                failed_downloads.append({
                    "youtube_video_url": video_url, 
                    "youtube_video_title": video_download_result["youtube_video_title"], 
                    "error_message": cast(str, video_download_result["error_message"])
                })
                continue

        return {
            "success": len(failed_downloads) == 0,
            "channel_name": channel.channel_url,
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
    ) -> Path:
        youtube_video_title = await youtube_video.title()
        fallback_filename = f"Video ({youtube_video.video_id})" if stream.includes_video_track else f"Audio ({youtube_video.video_id})"
        max_filename_length = calculate_max_filename_length(download_directory)
        safe_filename = safe_full_filename(
            full_filename=youtube_video_title, 
            fallback_filename=fallback_filename, 
            filename_prefix=filename_prefix,
            max_length=max_filename_length
        )

        if safe_filename == "":
            raise ImpossibleDownloadPath(download_directory)
        
        video_full_file_path = download_directory / safe_filename

        if video_full_file_path.exists() and skip_existing_files:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

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
            filename=safe_filename
        )

        download_bar.close()

        if (download_path == None):
            raise DownloadCancelled(youtube_video_title)
        
        return Path(download_path)


    async def _download_video(
        self, 
        youtube_video: 
        AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> Path:
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_downloads_to"]
        should_skip_existing_files = self.configuration["download_behavior_configuration"]["skip_existing_files"]
        stream: Optional[Stream] = (await youtube_video.streams()).filter(progressive=True, only_audio=False, only_video=False).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())

        # Early return when not converting to another file format
        if not should_convert:
            video_download_location = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                should_skip_existing_files,
                filename_prefix
            )

            return video_download_location
        
        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_video_downloads_to"
        )
        
        converted_file_path: Path = resolve_safe_file_path(
            download_directory, 
            stream.default_filename, 
            f"Video ({youtube_video.video_id})", 
            filename_prefix, 
            custom_file_extension
        )

        if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")
        
        temporary_video_path = await self._download_stream(
            youtube_video,
            stream,
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )
        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
            [ temporary_video_path ], 
            [ converted_file_path ],
            [ "y" ],
            conversion_bar.on_progress
        )

        conversion_bar.close()
        spaced_print("Conversion was successful!")

        return converted_file_path    
    

    async def _download_video_only(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> Path:
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_only_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_only_downloads_to"]
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())

        # Early return when not converting to another file format
        if not should_convert:
            video_download_location = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename_prefix
            )

            return video_download_location
        
        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_video_only_downloads_to"
        )

        converted_file_path: Path = resolve_safe_file_path(
            download_directory, 
            stream.default_filename, 
            f"Video ({youtube_video.video_id})", 
            filename_prefix, 
            custom_file_extension
        )

        if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

        temporary_video_path = await self._download_stream(
            youtube_video,
            stream,
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )
        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
            [ temporary_video_path ], 
            [ converted_file_path ],
            [ "y" ],
            conversion_bar.on_progress
        )

        conversion_bar.close()
        spaced_print("Conversion was successful!")

        return converted_file_path


    async def _download_audio_only(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> Path:
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_downloads_to"]
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())

        # Early return when not converting to another file format
        if not should_convert:
            video_download_location = await self._download_stream(
                youtube_video,
                stream,
                download_directory, 
                self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename_prefix
            )

            return video_download_location

        ensure_can_use_ffmpeg(
            self.ffmpeg_executable_path, 
            custom_file_extension, 
            "convert_audio_only_downloads_to"
        )

        converted_file_path: Path = resolve_safe_file_path(
            download_directory, 
            stream.default_filename, 
            f"Video ({youtube_video.video_id})", 
            filename_prefix, 
            custom_file_extension
        )

        if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

        temporary_video_path = await self._download_stream(
            youtube_video,
            stream,
            self.temporary_files_directory_path, 
            False,
            filename_prefix
        )
        conversion_bar = self.progress_bar_factory.conversion(
            f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
            int(stream.durationMs)
        )

        await convert_file(
            cast(Path, self.ffmpeg_executable_path), 
            [ temporary_video_path ], 
            [ converted_file_path ],
            [ "y" ],
            conversion_bar.on_progress
        )

        conversion_bar.close()
        spaced_print("Conversion was successful!")

        return converted_file_path


    async def _download_best_of_both(
        self, 
        youtube_video: AsyncYouTube, 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> Path:    
        if not self.configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"]:
            true_download_directory: Path = safe_join_directory(
                download_directory, 
                await youtube_video.title(), 
                f"Video ({youtube_video.video_id})"
            )

            if true_download_directory.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")
            
            true_download_directory.mkdir(exist_ok=True)

            try:
                await self._download_video_only(
                    youtube_video,
                    true_download_directory,
                    "Video-"
                )

                await self._download_audio_only(
                    youtube_video,
                    true_download_directory,
                    "Audio-"
                )
            except ImpossibleDownloadPath:
                if not any(true_download_directory.iterdir()):
                    true_download_directory.rmdir()

                raise

            return true_download_directory
        else:
            custom_file_extension = self.configuration["download_behavior_configuration"]["best_of_both_merged_file_format"]
            video_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()
            audio_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

            if video_stream == None or audio_stream == None:
                raise NoStreamsFoundError(await youtube_video.title())
            
            ensure_can_use_ffmpeg(
                self.ffmpeg_executable_path, 
                custom_file_extension, 
                "best_of_both_merged_file_format"
            )

            converted_file_path: Path = resolve_safe_file_path(
                download_directory, 
                video_stream.default_filename, 
                f"Video ({youtube_video.video_id})", 
                filename_prefix, 
                custom_file_extension
            )

            if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            temporary_video_path = await self._download_stream(
                youtube_video,
                video_stream,
                self.temporary_files_directory_path,
                False,
                "Video-"
            )

            temporary_audio_path = await self._download_stream(
                youtube_video,
                audio_stream,
                self.temporary_files_directory_path,
                False,
                "Audio-"
            )

            conversion_bar = self.progress_bar_factory.conversion(
                f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
                int(video_stream.durationMs)
            )

            await convert_file(
                cast(Path, self.ffmpeg_executable_path), 
                [ temporary_video_path, temporary_audio_path ], 
                [ converted_file_path ],
                [ "y" ],
                conversion_bar.on_progress
            )

            conversion_bar.close()
            spaced_print("Conversion was successful!")

            return converted_file_path  


    async def _download_custom(
        self, 
        youtube_video: AsyncYouTube, 
        chosen_streams: List[Stream], 
        download_directory: Path, 
        filename_prefix: Optional[str] = None
    ) -> Path:
        should_convert = self.configuration["download_behavior_configuration"]["convert_custom_downloads"] 
        custom_file_extension = self.configuration["download_behavior_configuration"]["convert_custom_downloads_to"]

        for stream in chosen_streams:
            if not should_convert:
                await self._download_stream(
                    youtube_video,
                    stream,
                    download_directory, 
                    self.configuration["download_behavior_configuration"]["skip_existing_files"],
                    f"{filename_prefix or ''}{stream.itag}-"
                )

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
            except ImpossibleDownloadPath:
                if not any(download_directory.iterdir()):
                    download_directory.rmdir()

                raise

            if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")
            
            temporary_video_path = await self._download_stream(
                youtube_video,
                stream,
                self.temporary_files_directory_path,
                False,
                filename_prefix=f"{filename_prefix or ''}{stream.itag}-"
            )

            conversion_bar = self.progress_bar_factory.conversion(
                f"Converting ({await youtube_video.title()}) to ({custom_file_extension})",
                int(stream.durationMs)
            )

            await convert_file(
                cast(Path, self.ffmpeg_executable_path), 
                [ temporary_video_path ], 
                [ converted_file_path ],
                [ "y" ],
                conversion_bar.on_progress
            )

            conversion_bar.close()
            spaced_print("Conversion was successful!") 

        return download_directory
