from typing import List, Optional

from pytubefix.async_youtube import AsyncYouTube
from pytubefix import Playlist, Stream, StreamQuery
from ffmpeg import FFmpeg
from pathlib import Path

from ..lib import MediaDownloadDisplay, MediaConversionDisplay
from ..custom_types import Configuration, VideoDownloadResult, PlaylistDownloadResult
from ..enums import DownloadFormat
from ..exceptions import NoStreamsFoundError, VideoDownloadSkipped, DownloadCancelled
from .console import spaced_print
from .os import safe_full_filename, safe_os_name

class Downloader:
    def __init__(self, configuration: Configuration, temporary_files_directory_path: Path):
        self.configuration = configuration
        self.temporary_files_directory_path = temporary_files_directory_path


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
        except (VideoDownloadSkipped, DownloadCancelled) as exception:
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
        true_download_directory: Path

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = download_directory.joinpath(safe_os_name(playlist.title, f"Playlist ({playlist.playlist_id})"))

            if not true_download_directory.exists(): true_download_directory.mkdir()
        else:
            true_download_directory = download_directory

        failed_downloads: List[str] = []

        for video_url in playlist.url_generator():
            video_download_result = await self.download_video(
                youtube_video_url=video_url, 
                download_format=download_format, 
                download_directory=true_download_directory
            )

            if not video_download_result["success"]:
                spaced_print(video_download_result["error_message"])
                failed_downloads += video_url
                continue

            spaced_print(f"Video ({video_download_result["youtube_video_title"]}) was downloaded successfully! ({video_download_result["error_message"]})")

        return {
            "success": True,
            "playlist_name": str(playlist.title),
            "failed_downloads": failed_downloads,
            "download_directory_path": true_download_directory,
            "error_message": None
        }


    async def _download_video(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(progressive=True, only_audio=False, only_video=False).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())

        safe_filename = safe_full_filename(
            full_filename=stream.default_filename, 
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix
        )
        video_full_file_path = download_directory / safe_filename

        if video_full_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen video chosen_stream: {stream}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        download_path: Optional[str] = stream.download(
            output_path=str(download_directory), 
            skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
            filename=safe_filename
        )
        download_display.progress_bar.close()

        if (download_path == None):
            raise DownloadCancelled(await youtube_video.title())
        
        return Path(download_path)
    

    async def _download_video_only(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()

        if (stream == None):
            raise NoStreamsFoundError(await youtube_video.title())
        
        safe_filename = safe_full_filename(
            full_filename=stream.default_filename, 
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix,
            extension_override="mp4" if self.configuration["quality_of_life_configuration"]["convert_video_only_downloads_to_mp4"] else None
        )
        safe_full_video_file_path = download_directory / safe_filename
        
        if safe_full_video_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen video only chosen_stream: {stream}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        if not self.configuration["quality_of_life_configuration"]["convert_video_only_downloads_to_mp4"] and stream.mime_type == "video/mp4":
            download_file_path = stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_filename
            )
            download_display.progress_bar.close()

            if (download_file_path == None):
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

            return Path(download_file_path)
        else:
            temp_file_download_path: Optional[str] = stream.download(
                output_path=str(self.temporary_files_directory_path),
                skip_existing=False,
                filename=safe_full_filename(
                    full_filename=stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Video-"
                )
            )
            download_display.progress_bar.close()

            if temp_file_download_path == None:
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)
                
            download_file_path = Path(temp_file_download_path)
            converted_file_path: Path = download_directory / safe_filename

            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )

            conversion_display = MediaConversionDisplay(
                f"Converting ({await youtube_video.title()}) to (mp4)",
                stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            ffmpeg.execute()

            conversion_display.progress_bar.n = conversion_display.progress_bar.total
            conversion_display.progress_bar.refresh()

            conversion_display.progress_bar.close()
            spaced_print("Conversion was successful!")

            return converted_file_path


    async def _download_audio_only(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

        if stream == None:
            raise NoStreamsFoundError(await youtube_video.title())
        
        safe_filename = safe_full_filename(
            full_filename=stream.default_filename, 
            fallback_filename=f"Video ({youtube_video.video_id})", 
            filename_prefix=filename_prefix,
            extension_override="mp3" if self.configuration["quality_of_life_configuration"]["convert_audio_only_downloads_to_mp3"] else None
        )
        safe_full_audio_file_path = download_directory / safe_filename
        
        if safe_full_audio_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
            raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen audio only chosen_stream: {stream}")

        download_display = MediaDownloadDisplay(
            f"Downloading ({await youtube_video.title()})", 
            stream.filesize, 
            self.configuration
        )
        youtube_video.register_on_progress_callback(download_display.show_progress_callback)

        if not self.configuration["quality_of_life_configuration"]["convert_audio_only_downloads_to_mp3"]:
            download_file_location: Optional[str] = stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_filename
            )
            download_display.progress_bar.close()

            if download_file_location == None:
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

            return Path(download_file_location)
        else:
            true_download_directory: Path = self.temporary_files_directory_path

            download_file_location: Optional[str] = stream.download(
                output_path=str(true_download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=stream.default_filename, 
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
                FFmpeg()
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )          

            conversion_display = MediaConversionDisplay(
                f"Converting ({await youtube_video.title()}) to (mp3)",
                stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            ffmpeg.execute()

            conversion_display.progress_bar.n = conversion_display.progress_bar.total
            conversion_display.progress_bar.refresh()

            conversion_display.progress_bar.close()
            print("\nConversion was successful!", end="\n")
            
            return converted_file_path   


    async def _download_best_of_both(self, youtube_video: AsyncYouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:    
        if not self.configuration["quality_of_life_configuration"]["combine_best_of_both_downloads_into_one_file"]:
            safe_folder_name = safe_os_name(
                await youtube_video.title(),
                f"Video ({youtube_video.video_id})"
            )

            true_download_directory: Path = download_directory / safe_folder_name

            if true_download_directory.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

            true_download_directory.mkdir(exist_ok=True)

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
            video_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_video=True).first()
            audio_stream: Optional[Stream] = (await youtube_video.streams()).filter(is_dash=True, only_audio=True).desc().first()

            if video_stream == None:
                raise NoStreamsFoundError(await youtube_video.title())

            if audio_stream == None:
                raise NoStreamsFoundError(await youtube_video.title())
            
            merged_file_name = safe_full_filename(
                full_filename=video_stream.default_filename,
                fallback_filename=f"Video ({youtube_video.video_id})",
                filename_prefix=filename_prefix,
                extension_override="mp4"
            )
            merged_file_path = download_directory / merged_file_name

            if merged_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

            if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
                spaced_print(f"Chosen video only chosen_stream: {video_stream}")
                spaced_print(f"Chosen audio only chosen_stream: {audio_stream}")

            video_download_display = MediaDownloadDisplay(
                f"Downloading ({await youtube_video.title()})", 
                video_stream.filesize, 
                self.configuration
            )
            youtube_video.register_on_progress_callback(video_download_display.show_progress_callback)

            video_only_file_path: Optional[str] = video_stream.download(
                output_path=str(self.temporary_files_directory_path), 
                skip_existing=False,
                filename=safe_full_filename(
                    full_filename=video_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Video-"
                )
            )
            video_download_display.progress_bar.close()

            audio_download_display = MediaDownloadDisplay(
                f"Downloading ({await youtube_video.title()})", 
                audio_stream.filesize, 
                self.configuration
            )
            youtube_video.register_on_progress_callback(audio_download_display.show_progress_callback)

            audio_only_file_path: Optional[str] = audio_stream.download(
                output_path=str(self.temporary_files_directory_path), 
                skip_existing=False,
                filename=safe_full_filename(
                    full_filename=audio_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Audio-"
                )
            )
            audio_download_display.progress_bar.close()

            if (video_only_file_path == None or audio_only_file_path == None):
                raise VideoDownloadSkipped(await youtube_video.title(), download_directory)

            merged_file_path: Path = download_directory.joinpath(
                safe_full_filename(
                    full_filename=video_stream.default_filename,
                    fallback_filename=f"Video ({youtube_video.video_id})",
                    filename_prefix=filename_prefix,
                    extension_override="mp4"
                )
            )

            if merged_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                if not self.configuration["warning_configuration"]["silence_already_exists_warning"]:
                    spaced_print(f"WARNING: ({youtube_video.title}) already exists!")

                return merged_file_path

            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(video_only_file_path)
                .input(audio_only_file_path)
                .output(merged_file_path)
            )

            conversion_display = MediaConversionDisplay(
                f"Merging ({video_stream.title})",
                video_stream, 
                ffmpeg, 
                self.configuration
            )
            ffmpeg.on("progress", conversion_display.on_progress)
            
            ffmpeg.execute()

            conversion_display.progress_bar.n = conversion_display.progress_bar.total
            conversion_display.progress_bar.refresh()

            conversion_display.progress_bar.close()
            spaced_print("Merge Successful!")

            return merged_file_path
