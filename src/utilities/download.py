from typing import Optional, Tuple

from pytubefix import YouTube, Playlist, Stream, StreamQuery
from ffmpeg import FFmpeg, Progress
from pathlib import Path

from custom_types import Configuration
from enums import DownloadFormat
from exceptions import DownloadDirectoryIsAFileError, NoStreamsFoundError, PathDoesNotExistError, VideoDownloadSkipped
from utilities.callbacks import video_download_progress_callback
from utilities.console import spaced_print
from utilities.os import safe_full_filename, safe_os_name

class Downloader:
    def __init__(self, configuration: Configuration, temp_files_directory_path: Path):
        self.configuration = configuration
        self.temp_files_directory_path = temp_files_directory_path


    def download_video(self, youtube_video_url: str, download_format: DownloadFormat, download_directory: Path, filename_prefix: Optional[str] = None) -> Tuple[str, Path]:
        if not download_directory.exists(): raise PathDoesNotExistError(str(download_directory))
        if not download_directory.is_dir(): raise DownloadDirectoryIsAFileError(str(download_directory))

        youtube_video: YouTube = YouTube(youtube_video_url)
        youtube_video.register_on_progress_callback(video_download_progress_callback)

        streams: StreamQuery = youtube_video.streams

        if len(streams) == 0: raise NoStreamsFoundError(youtube_video.title)

        download_path: Path

        if download_format == DownloadFormat.VIDEO:
            download_path = self._download_video(youtube_video, download_directory, filename_prefix)
        elif download_format == DownloadFormat.VIDEO_ONLY:
            download_path = self._download_video_only(youtube_video, download_directory, filename_prefix)
        elif download_format == DownloadFormat.AUDIO_ONLY:
            download_path = self._download_audio_only(youtube_video, download_directory, filename_prefix)
        elif download_format == DownloadFormat.BEST_OF_BOTH:
            download_path = self._download_best_of_both(youtube_video, download_directory, filename_prefix)

        return youtube_video.title, download_path


    def download_playlist(self, playlist_url: str, download_format: DownloadFormat, download_directory: Path) -> Tuple[str, Path]:
        if not download_directory.exists(): raise PathDoesNotExistError(str(download_directory))
        if not download_directory.is_dir(): raise DownloadDirectoryIsAFileError(str(download_directory))

        playlist: Playlist = Playlist(playlist_url)
        true_download_directory: Path

        if self.configuration["quality_of_life_configuration"]["put_playlist_videos_in_folder"]:
            true_download_directory = download_directory.joinpath(safe_os_name(playlist.title, f"Playlist ({playlist.playlist_id})"))

            if not true_download_directory.exists(): true_download_directory.mkdir()
        else:
            true_download_directory = download_directory

        for video_url in playlist.url_generator():
            try:
                youtube_video_title, file_download_location = self.download_video(
                    youtube_video_url=video_url, 
                    download_format=download_format, 
                    download_directory=true_download_directory
                )
            except NoStreamsFoundError as exception:
                spaced_print(str(exception))
            else:
                spaced_print(f"Video ({youtube_video_title}) was downloaded successfully! ({file_download_location})")

        return playlist.title, true_download_directory


    def _download_video(self, youtube_video: YouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        chosen_video_stream: Optional[Stream] = youtube_video.streams.filter(progressive=True, only_audio=False, only_video=False).desc().first()

        if chosen_video_stream == None:
            raise NoStreamsFoundError(youtube_video.title)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen video chosen_stream: {chosen_video_stream}")

        raw_downloaded_file_path: Optional[str] = chosen_video_stream.download(
            output_path=str(download_directory), 
            skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
            filename=safe_full_filename(
                full_filename=chosen_video_stream.default_filename, 
                fallback_filename=f"Video ({youtube_video.video_id})", 
                filename_prefix=filename_prefix
            )
        )

        if (raw_downloaded_file_path == None):
            raise VideoDownloadSkipped(youtube_video.title)
        
        return Path(raw_downloaded_file_path)
    

    def _download_video_only(self, youtube_video: YouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        video_only_stream: Optional[Stream] = youtube_video.streams.filter(is_dash=True, only_video=True).first()

        if (video_only_stream == None):
            raise NoStreamsFoundError(youtube_video.title)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen video only chosen_stream: {video_only_stream}")

        if not self.configuration["quality_of_life_configuration"]["convert_video_only_downloads_to_mp4"] and video_only_stream.mime_type == "video/mp4":
            download_file_path = video_only_stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=video_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix=filename_prefix
                )
            )

            if (download_file_path == None):
                raise VideoDownloadSkipped(youtube_video.title)

            return Path(download_file_path)
        else:
            converted_file_full_filename: str = safe_full_filename(
                full_filename=video_only_stream.default_filename.split(".")[0] + ".mp4",
                fallback_filename=f"Video ({youtube_video.video_id})",
                filename_prefix=filename_prefix
            )

            temp_file_download_path: Optional[str] = video_only_stream.download(
                output_path=str(self.temp_files_directory_path),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=video_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Video-"
                )
            )

            if temp_file_download_path == None:
                raise VideoDownloadSkipped(youtube_video.title)
                
            download_file_path = Path(temp_file_download_path)
            converted_file_path: Path = download_directory.joinpath(converted_file_full_filename)

            if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                if not self.configuration["warning_configuration"]["silence_already_exists_warning"]: 
                    spaced_print(f"WARNING: ({youtube_video.title}) already exists!")
                
                return converted_file_path

            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )

            @ffmpeg.on("progress")
            def on_progress(progress: Progress):
                current_converted_file_size_in_mb: float = round(progress.size / 1_000_000, 2)

                spaced_print(
                    f"""Converting ({youtube_video.title}) to mp4...\n
                    Current file size {current_converted_file_size_in_mb}Mb ({progress.bitrate}Kbp/s)"""
                )
                
            spaced_print(f"Converting ({youtube_video.title}) to mp4...")

            ffmpeg.execute()

            spaced_print("Conversion was successful!")

            return converted_file_path


    def _download_audio_only(self, youtube_video: YouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        chosen_audio_only_stream: Optional[Stream] = youtube_video.streams.filter(is_dash=True, only_audio=True).desc().first()

        if chosen_audio_only_stream == None:
            raise NoStreamsFoundError(youtube_video.title)

        if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
            spaced_print(f"Chosen audio only chosen_stream: {chosen_audio_only_stream}")

        if not self.configuration["quality_of_life_configuration"]["convert_audio_only_downloads_to_mp3"]:
            download_file_location: Optional[str] = chosen_audio_only_stream.download(
                output_path=str(download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=chosen_audio_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix=filename_prefix
                )
            )

            if download_file_location == None:
                raise VideoDownloadSkipped(youtube_video.title)

            return Path(download_file_location)
        else:
            true_download_directory: Path = self.temp_files_directory_path
            converted_file_full_filename: str = safe_full_filename(
                full_filename=chosen_audio_only_stream.default_filename.split(".")[0] + ".mp3",
                fallback_filename=f"Video ({youtube_video.video_id})",
                filename_prefix=filename_prefix
            )

            download_file_location: Optional[str] = chosen_audio_only_stream.download(
                output_path=str(true_download_directory),
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=chosen_audio_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Audio-"
                )
            )

            if (download_file_location == None):
                raise NoStreamsFoundError(youtube_video.title)

            download_file_path: Path = Path(download_file_location)
            converted_file_path: Path = download_directory.joinpath(converted_file_full_filename)

            if converted_file_path.exists() and self.configuration["download_behavior_configuration"]["skip_existing_files"]:
                if not self.configuration["warning_configuration"]["silence_already_exists_warning"]: 
                    spaced_print(f"WARNING: ({youtube_video.title}) already exists!")
                
                return converted_file_path
            
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(download_file_path)
                .output(converted_file_path)
            )

            @ffmpeg.on("progress")
            def on_progress(progress: Progress):
                current_converted_file_size_in_mb: float = round(progress.size / 1_000_000, 2)

                spaced_print(
                    f"""Converting ({youtube_video.title}) to mp3...\n
                    Current file size {current_converted_file_size_in_mb}Mb ({progress.bitrate}Kbp/s)"""
                )
                
            spaced_print(f"Converting ({youtube_video.title}) to mp3...")

            ffmpeg.execute()

            spaced_print("Conversion was successful!")

            return converted_file_path   


    def _download_best_of_both(self, youtube_video: YouTube, download_directory: Path, filename_prefix: Optional[str] = None) -> Path:
        video_only_stream: Optional[Stream] = youtube_video.streams.filter(is_dash=True, only_video=True).first()
        audio_only_stream: Optional[Stream] = youtube_video.streams.filter(is_dash=True, only_audio=True).desc().first()

        if video_only_stream == None:
            raise NoStreamsFoundError(youtube_video.title)

        if audio_only_stream == None:
            raise NoStreamsFoundError(youtube_video.title)
        
        if not self.configuration["quality_of_life_configuration"]["combine_best_of_both_downloads_into_one_file"]:
            unsafe_folder_name: str = video_only_stream.default_filename.split(".")[0]
            true_download_directory: Path = download_directory.joinpath(
                safe_os_name(
                    unsafe_folder_name,
                    f"Video ({youtube_video.video_id})"
                )
            )

            if not true_download_directory.exists(): 
                true_download_directory.mkdir()

            self._download_video_only(
                youtube_video=youtube_video,
                download_directory=true_download_directory,
                filename_prefix="Video-"
            )

            self._download_audio_only(
                youtube_video=youtube_video,
                download_directory=true_download_directory,
                filename_prefix="Audio-"
            )

            return true_download_directory
        else:
            if self.configuration["quality_of_life_configuration"]["display_chosen_stream_on_start_of_download"]:
                spaced_print(f"Chosen video only chosen_stream: {video_only_stream}")
                spaced_print(f"Chosen audio only chosen_stream: {audio_only_stream}")

            video_only_file_path: Optional[str] = video_only_stream.download(
                output_path=str(self.temp_files_directory_path), 
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=video_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Video-"
                )
            )

            audio_only_file_path: Optional[str] = audio_only_stream.download(
                output_path=str(self.temp_files_directory_path), 
                skip_existing=self.configuration["download_behavior_configuration"]["skip_existing_files"],
                filename=safe_full_filename(
                    full_filename=audio_only_stream.default_filename, 
                    fallback_filename=f"Video ({youtube_video.video_id})", 
                    filename_prefix="Audio-"
                )
            )

            if (video_only_file_path == None or audio_only_file_path == None):
                raise VideoDownloadSkipped(youtube_video.title)

            merged_full_filename: str = safe_full_filename(
                full_filename=video_only_stream.default_filename.split(".")[0] + ".mp4",
                fallback_filename=f"Video ({youtube_video.video_id})",
                filename_prefix=filename_prefix
            )
            merged_file_path: Path = download_directory.joinpath(merged_full_filename)

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

            @ffmpeg.on("progress")
            def on_progress(progress: Progress):
                current_converted_file_size_in_mb: float = round(progress.size / 1_000_000, 2)

                spaced_print(
                    f"""Merging ({youtube_video.title}) audio and video into one mp4 file...\n
                    Current file size {current_converted_file_size_in_mb}Mb ({progress.bitrate}Kbp/s)"""
                )

            spaced_print(f"Merging ({youtube_video.title}) audio and video into one mp4 file...")

            ffmpeg.execute()
            
            spaced_print("Merge Successful!")

            return merged_file_path
