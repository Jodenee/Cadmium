from typing import Any, Generator, List, Optional, Tuple,cast

from pick import pick, Option
from pytubefix.async_youtube import AsyncYouTube
from pytubefix import YouTube, Playlist, Stream, StreamQuery, Channel
from pytubefix.exceptions import MaxRetriesExceeded
from ffmpeg.asyncio import FFmpeg
from pathlib import Path

from ..lib import MediaDownloadDisplay, MediaConversionDisplay
from ..custom_types import Configuration, VideoDownloadResult, PlaylistDownloadResult, FailedDownloadInformation, ChannelDownloadResult
from ..enums import DownloadFormat, OperatingSystem
from ..exceptions import NoStreamsFoundError, VideoDownloadSkipped, DownloadCancelled, InvalidConfigurationError, ImpossibleDownloadPath
from .console import spaced_print
from .os import os_choose, safe_full_filename, safe_os_name, MAX_OS_FILENAME_LENGTH, MAX_OS_PATH_LENGTH
from .pytubefix_extensions import stream_default_filename, stream_repr

class Downloader:
    def __init__(self, configuration: Configuration, select_menu_indicator: str, temporary_files_directory_path: Path, ffmpeg_executable_path: Optional[Path] = None):
        self.configuration = configuration
        self.select_menu_indicator = select_menu_indicator
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
                download_path = await self._download_custom(youtube_video, download_directory, filename_prefix)
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
            true_download_directory = download_directory.joinpath(safe_os_name(playlist.title, f"Playlist ({playlist.playlist_id})"))

            if not true_download_directory.exists(): true_download_directory.mkdir()

        failed_downloads: List[FailedDownloadInformation] = []

        for video_url in playlist.url_generator():
            video_download_result = await self.download_video(
                youtube_video_url=video_url, 
                download_format=download_format, 
                download_directory=true_download_directory
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
            true_download_directory = download_directory.joinpath(safe_os_name(channel.channel_name, f"Channel ({channel.channel_id})"))
            true_download_directory.mkdir(exist_ok=True)

        failed_downloads = []

        video: YouTube
        for video in cast(Generator[YouTube, Any, None], channel.url_generator()):
            video_download_result = await self.download_video(
                youtube_video_url=video.watch_url, 
                download_format=download_format, 
                download_directory=true_download_directory
            )

            if not video_download_result["success"]:
                failed_downloads.append({
                    "youtube_video_url": video.title, 
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


    async def _download_video(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(progressive=True, only_audio=False, only_video=False).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())
        
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_downloads"] 
        video_custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_downloads_to"]

        if should_convert and not self.ffmpeg_executable_path:
            raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")
        elif video_custom_file_extension == None or len(video_custom_file_extension.strip()) == 0 and should_convert:
            raise InvalidConfigurationError("convert_video_only_downloads_to", "is empty")

        safe_filename = safe_full_filename(
            full_filename=await stream_default_filename(stream), 
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix,
            extension_override=None if not should_convert else video_custom_file_extension,
            max_length=min(MAX_OS_PATH_LENGTH - (len(str(download_directory)) + 1), MAX_OS_FILENAME_LENGTH)
        )

        if safe_filename == "":
            raise ImpossibleDownloadPath(download_directory)

        video_full_file_path = download_directory / safe_filename

        if video_full_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen stream info: {stream_repr(stream)}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        if not should_convert:
            download_path: Optional[str] = stream.download(
                output_path=str(download_directory), 
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_filename
            )
            download_display.progress_bar.close()

            if (download_path == None):
                raise DownloadCancelled(await youtube_video.title())
        
            return Path(download_path)
        else:
            temporary_file_full_filename = safe_full_filename(
                full_filename=await stream_default_filename(stream), 
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix="Video-",
                max_length=min(MAX_OS_PATH_LENGTH - (len(str(self.temporary_files_directory_path)) + 1), MAX_OS_FILENAME_LENGTH)
            )

            if temporary_file_full_filename == "":
                raise ImpossibleDownloadPath(self.temporary_files_directory_path)

            temporary_file_download_path: Optional[str] = stream.download(
                output_path=str(self.temporary_files_directory_path),
                skip_existing=False,
                filename=temporary_file_full_filename
            )
            download_display.progress_bar.close()

            if temporary_file_download_path == None:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")
                
            download_file_path = Path(temporary_file_download_path)
            converted_file_path: Path = download_directory / safe_filename

            ffmpeg = (
                FFmpeg(str(self.ffmpeg_executable_path))
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )

            conversion_display = MediaConversionDisplay(
                f"Converting ({await youtube_video.title()}) to ({video_custom_file_extension})",
                stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            try:
                await ffmpeg.execute()

                conversion_display.progress_bar.n = conversion_display.progress_bar.total
                conversion_display.progress_bar.refresh()
            except:
                ffmpeg.terminate()
                raise

            conversion_display.progress_bar.close()
            spaced_print("Conversion was successful!")

            return converted_file_path    
    

    async def _download_video_only(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()

        if (stream == None):
            raise NoStreamsFoundError(await youtube_video.title())
        
        should_convert = self.configuration["download_behavior_configuration"]["convert_video_only_downloads"] 
        video_only_custom_file_extension = self.configuration["download_behavior_configuration"]["convert_video_only_downloads_to"]

        if should_convert and not self.ffmpeg_executable_path:
            raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")
        
        if video_only_custom_file_extension == None or len(video_only_custom_file_extension.strip()) == 0 and should_convert:
            raise InvalidConfigurationError("convert_video_only_downloads_to", "is empty")
        
        safe_filename = safe_full_filename(
            full_filename=await stream_default_filename(stream),
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix,
            extension_override=None if not should_convert else video_only_custom_file_extension,
            max_length=min(MAX_OS_PATH_LENGTH - (len(str(download_directory)) + 1), MAX_OS_FILENAME_LENGTH)
        )

        if safe_filename == "":
            raise ImpossibleDownloadPath(download_directory)

        safe_full_video_file_path = download_directory / safe_filename
        
        if safe_full_video_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen stream info: {stream_repr(stream)}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        if not should_convert:
            download_file_path = stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_filename
            )
            download_display.progress_bar.close()

            if (download_file_path == None):
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            return Path(download_file_path)
        else:
            if not self.ffmpeg_executable_path:
                raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")

            temporary_file_full_filename = safe_full_filename(
                full_filename=await stream_default_filename(stream), 
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix="Video-",
                max_length=min(MAX_OS_PATH_LENGTH - (len(str(self.temporary_files_directory_path)) + 1), MAX_OS_FILENAME_LENGTH)
            )
            temporary_file_download_path: Optional[str] = stream.download(
                output_path=str(self.temporary_files_directory_path),
                skip_existing=False,
                filename=temporary_file_full_filename
            )
            download_display.progress_bar.close()

            if temporary_file_download_path == None:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")
                
            download_file_path = Path(temporary_file_download_path)

            ffmpeg = (
                FFmpeg(str(self.ffmpeg_executable_path))
                .option("y")
                .input(download_file_path)
                .output(safe_full_video_file_path)
            )

            conversion_display = MediaConversionDisplay(
                f"Converting ({await youtube_video.title()}) to ({video_only_custom_file_extension})",
                stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            try:
                await ffmpeg.execute()

                conversion_display.progress_bar.n = conversion_display.progress_bar.total
                conversion_display.progress_bar.refresh()
            except:
                ffmpeg.terminate()
                raise

            conversion_display.progress_bar.close()
            spaced_print("Conversion was successful!")

            return safe_full_video_file_path


    async def _download_audio_only(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())
        
        should_convert = self.configuration["download_behavior_configuration"]["convert_audio_only_downloads"] 
        video_custom_file_extension = self.configuration["download_behavior_configuration"]["convert_audio_only_downloads_to"]

        if should_convert and not self.ffmpeg_executable_path:
            raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")

        if video_custom_file_extension == None or len(video_custom_file_extension.strip()) == 0 and should_convert:
            raise InvalidConfigurationError("convert_video_only_downloads_to", "is empty")

        safe_filename = safe_full_filename(
            full_filename=await stream_default_filename(stream), 
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix,
            extension_override=None if not should_convert else video_custom_file_extension
        )
        safe_full_audio_file_path = download_directory / safe_filename
        
        if safe_full_audio_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen stream info: {stream_repr(stream)}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        if not self.configuration["download_behavior_configuration"]["convert_audio_only_downloads"]:
            download_file_location: Optional[str] = stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_filename
            )
            download_display.progress_bar.close()

            if download_file_location == None:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            return Path(download_file_location)
        else:
            if not self.ffmpeg_executable_path:
                raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")

            download_file_location: Optional[str] = stream.download(
                output_path=str(self.temporary_files_directory_path),
                skip_existing=False,
                filename=safe_full_filename(
                    full_filename=await stream_default_filename(stream), 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Audio-"
                )
            )
            download_display.progress_bar.close()

            if (download_file_location == None):
                raise NoStreamsFoundError(await youtube_video.title())

            download_file_path: Path = Path(download_file_location)
            converted_file_path: Path = download_directory / safe_filename
            
            ffmpeg = (
                FFmpeg(str(self.ffmpeg_executable_path))
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )          

            conversion_display = MediaConversionDisplay(
                f"Converting ({await youtube_video.title()}) to ({video_custom_file_extension})",
                stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            try:
                await ffmpeg.execute()

                conversion_display.progress_bar.n = conversion_display.progress_bar.total
                conversion_display.progress_bar.refresh()
            except:
                ffmpeg.terminate()
                raise

            conversion_display.progress_bar.close()
            print("\nConversion was successful!", end="\n")
            
            return converted_file_path   


    async def _download_best_of_both(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:    
        if not self.configuration["download_behavior_configuration"]["merge_best_of_both_downloads_into_one_file"]:
            safe_folder_name = safe_os_name(
                await youtube_video.title(),
                f"Video ({youtube_video.video_id})"
            )

            true_download_directory: Path = download_directory / safe_folder_name

            if true_download_directory.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            if len(str(true_download_directory)) <= MAX_OS_PATH_LENGTH:
                true_download_directory.mkdir(exist_ok=True)
            else:
                raise ImpossibleDownloadPath(true_download_directory)

            await self._download_video_only(
                youtube_video=youtube_video,
                download_directory=true_download_directory,
                filename_prefix="Video-"
            )

            await self._download_audio_only(
                youtube_video=youtube_video,
                download_directory=true_download_directory,
                filename_prefix="Audio-"
            )

            return true_download_directory
        else:
            if not self.ffmpeg_executable_path:
                raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")

            video_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()
            audio_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

            if video_stream == None:
                raise NoStreamsFoundError(await youtube_video.title())

            if audio_stream == None:
                raise NoStreamsFoundError(await youtube_video.title())
            
            merged_file_extension = self.configuration["download_behavior_configuration"]["best_of_both_merged_file_format"]

            if merged_file_extension == None or len(merged_file_extension.strip()) == 0:
                raise InvalidConfigurationError("convert_video_only_downloads_to", "is empty")
            
            merged_filename = safe_full_filename(
                full_filename=await stream_default_filename(video_stream),
                fallback_filename=f"Video ({youtube_video.video_id})",
                filename_prefix=filename_prefix,
                extension_override=merged_file_extension
            )
            merged_file_path = download_directory / merged_filename

            if len(str(merged_file_path)) > MAX_OS_PATH_LENGTH:
                raise ImpossibleDownloadPath(download_directory)

            if merged_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
                spaced_print(f"Chosen video stream info: {stream_repr(video_stream)}")
                spaced_print(f"Chosen audio stream info: {stream_repr(audio_stream)}")

            video_download_display = MediaDownloadDisplay(
                f"Downloading ({await youtube_video.title()})", 
                video_stream.filesize, 
                self.configuration
            )
            youtube_video.register_on_progress_callback(video_download_display.show_progress_callback)

            video_only_safe_filename = safe_full_filename(
                full_filename=await stream_default_filename(video_stream), 
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix="Video-",
                max_length=min(MAX_OS_PATH_LENGTH - (len(str(self.temporary_files_directory_path)) + 1), MAX_OS_FILENAME_LENGTH)
            )

            if video_only_safe_filename == "":
                raise ImpossibleDownloadPath(self.temporary_files_directory_path)

            video_only_file_path: Optional[str] = video_stream.download(
                output_path=str(self.temporary_files_directory_path), 
                skip_existing=False,
                filename=video_only_safe_filename
            )
            video_download_display.progress_bar.close()

            audio_download_display = MediaDownloadDisplay(
                f"Downloading ({await youtube_video.title()})", 
                audio_stream.filesize, 
                self.configuration
            )
            youtube_video.register_on_progress_callback(audio_download_display.show_progress_callback)

            audio_only_safe_filename = safe_full_filename(
                full_filename=await stream_default_filename(audio_stream),
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix="Audio-",
                max_length=min(MAX_OS_PATH_LENGTH - (len(str(self.temporary_files_directory_path)) + 1), MAX_OS_FILENAME_LENGTH)
            )

            if audio_only_safe_filename == "":
                raise ImpossibleDownloadPath(self.temporary_files_directory_path)

            audio_only_file_path: Optional[str] = audio_stream.download(
                output_path=str(self.temporary_files_directory_path), 
                skip_existing=False,
                filename=audio_only_safe_filename
            )
            audio_download_display.progress_bar.close()

            if (video_only_file_path == None or audio_only_file_path == None):
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            ffmpeg = (
                FFmpeg(str(self.ffmpeg_executable_path))
                .option("y")
                .input(video_only_file_path)
                .input(audio_only_file_path)
                .output(merged_file_path)
            )

            conversion_display = MediaConversionDisplay(
                f"Merging ({await youtube_video.title()})",
                video_stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            try:
                await ffmpeg.execute()

                conversion_display.progress_bar.n = conversion_display.progress_bar.total
                conversion_display.progress_bar.refresh()
            except:
                ffmpeg.terminate()
                raise

            conversion_display.progress_bar.close()
            spaced_print("Merge Successful!")

            return merged_file_path


    async def _download_custom(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        available_streams = await youtube_video.streams()

        if len(available_streams) == 0:
            raise NoStreamsFoundError(await youtube_video.title())

        true_download_directory = download_directory
        if self.configuration["quality_of_life_configuration"]["put_custom_streams_in_folder"]:
            true_download_directory_name = safe_os_name(
                await youtube_video.title(),
                f"Video ({youtube_video.video_id}) Streams"
            ) 

            true_download_directory = (download_directory / true_download_directory_name)
            true_download_directory.mkdir(exist_ok=True)

        options = [ Option(f"stream {stream.itag}", stream, stream_repr(stream)) for stream in available_streams]
        stream_pick_menu = pick(
            options, 
            "Pick the streams you wish to download. [Spacebar] to select/deselect and [Enter] to download.", 
            indicator=self.select_menu_indicator, 
            multiselect=True, 
            min_selection_count=1
        )

        should_convert = self.configuration["download_behavior_configuration"]["convert_custom_downloads"] 
        video_custom_file_extension = self.configuration["download_behavior_configuration"]["convert_custom_downloads_to"]

        if should_convert and not self.ffmpeg_executable_path:
            raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")

        if video_custom_file_extension == None or len(video_custom_file_extension.strip()) == 0 and should_convert:
            raise InvalidConfigurationError("convert_video_only_downloads_to", "is empty")

        for picked_option_info in stream_pick_menu:
            option: Option = cast(Tuple[Option, int], picked_option_info)[0]
            stream: Stream = cast(Stream, option.value)

            safe_filename = safe_full_filename(
                full_filename=await stream_default_filename(stream), 
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix=f"{filename_prefix or ''}{stream.itag}-",
                extension_override=None if not should_convert else video_custom_file_extension,
                max_length=os_choose({
                    OperatingSystem.WINDOWS: min(255 - (len(str(true_download_directory)) + 1), 255), # the added 1 is to include the delimiter into the calculation
                    OperatingSystem.DARWIN: min(1024 - (len(str(true_download_directory)) + 1), 255)
                }, min(4096 - (len(str(true_download_directory)) + 1), 255)) 
            )
            safe_full_file_path = true_download_directory / safe_filename
            
            if safe_full_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(f"Already exists in ({download_directory}).")

            if not should_convert:
                download_display = MediaDownloadDisplay(
                    f"Downloading Stream {stream.itag} ({await youtube_video.title()})", 
                    stream.filesize, 
                    self.configuration
                )
                youtube_video.register_on_progress_callback(download_display.show_progress_callback)

                download_path: Optional[str] = stream.download(
                    output_path=str(true_download_directory), 
                    skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                    filename=safe_filename
                )
                download_display.progress_bar.close()

                if (download_path == None):
                    raise DownloadCancelled(await youtube_video.title())
            else:        
                download_display = MediaDownloadDisplay(
                    f"Downloading Stream {stream.itag} ({await youtube_video.title()})", 
                    stream.filesize, 
                    self.configuration
                )
                youtube_video.register_on_progress_callback(download_display.show_progress_callback)

                temporary_download_path: Optional[str] = stream.download(
                    output_path=str(self.temporary_files_directory_path), 
                    skip_existing=False,
                    filename=safe_full_filename(
                        full_filename=await stream_default_filename(stream),
                        fallback_filename=f"Video ({youtube_video.video_id})", 
                        filename_prefix=f"{stream.itag}-"
                    )
                )
                download_display.progress_bar.close()

                if (temporary_download_path == None):
                    raise DownloadCancelled(await youtube_video.title())
                
                temporary_file_download_path: Path = Path(temporary_download_path)
                converted_file_path: Path = true_download_directory / safe_filename
                
                ffmpeg = (
                    FFmpeg(str(self.ffmpeg_executable_path))
                    .option("y")
                    .input(temporary_file_download_path)
                    .output(converted_file_path)
                )

                conversion_display = MediaConversionDisplay(
                    f"Converting ({await youtube_video.title()})",
                    stream, 
                    ffmpeg, 
                    self.configuration
                )
                ffmpeg.on("progress", conversion_display.on_progress)
                
                try:
                    await ffmpeg.execute()

                    conversion_display.progress_bar.n = conversion_display.progress_bar.total
                    conversion_display.progress_bar.refresh()
                except:
                    ffmpeg.terminate()
                    raise

                conversion_display.progress_bar.close()
                spaced_print("Conversion Successful!")

        return true_download_directory
