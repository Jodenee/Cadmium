from typing import List
from re import compile as compile_regex

from core.custom_types.configuration import Configuration

# General constants to be used within the application
TEMPORARY_FILE_EXTENSIONS: List[str] = [ ".webm", ".m4a", ".mp4", ".mp3" ]
SELECT_MENU_INDICATOR: str = ">"
DEFAULT_CONFIGURATION: Configuration = {
    "download_behavior_configuration": {
        "skip_existing_files": True,

        "convert_video_downloads": False,
        "convert_video_only_downloads": False,
        "convert_audio_only_downloads": False,
        "merge_best_of_both_downloads_into_one_file": False,
        "convert_custom_downloads": False,
        
        "convert_video_downloads_to": "mp4",
        "convert_video_only_downloads_to": "mp4",
        "convert_audio_only_downloads_to": "mp3",
        "best_of_both_merged_file_format": "mp4",
        "convert_custom_downloads_to": "mp4"
    },
    "quality_of_life_configuration": {
        "download_location_overrides": {
            "use_video_download_location_override": False,
            "use_video_only_download_location_override": False,
            "use_audio_only_download_location_override": False,
            "use_best_of_both_download_location_override": False,
            "use_custom_download_location_override": False,
            
            "video_download_location_override": "",
            "video_only_download_location_override": "",
            "audio_only_download_location_override": "",
            "best_of_both_download_location_override": "",
            "custom_download_location_override": ""
        },
        "put_playlist_videos_in_folder": True,
        "put_channel_videos_in_folder": True,
        "put_custom_streams_in_folder": True,
        "display_chosen_stream_on_start_of_download": True,
        "clear_temporary_files_before_exiting": False
    },
    "warning_configuration": {
        "silence_existing_temporary_files_warning": False,
    },
    "ui_configuration": {
        "custom_download_bar_colour": "",
        "custom_convert_bar_colour": "",
        "custom_clear_directory_bar_colour": ""
    },
    "external_dependency_configuration": {
        "ffmpeg": {
            "use_ffmpeg": True,
            "use_packaged_ffmpeg": True,
            "use_path_ffmpeg": False,
            "custom_ffmpeg_executable_path": ""
        }
    }
}

# Media parsing regexes used to parse media type from url.
YOUTUBE_VIDEO_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/(?:watch\?v=|shorts\/)[\w\-]{11}(?:[&\?]\S*)?$")
YOUTUBE_PLAYLIST_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w\-]+$")
YOUTUBE_CHANNEL_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/@[\w\-\.]+$")

# OS specific regexes for removing reserved characters from filenames
WINDOWS_RESERVED_FILENAME_CHARACTERS = r"[\/\\?%*:|\"<>\x7F\x00-\x1F]|^\.+|\.+$"
LINUX_RESERVED_FILENAME_CHARACTERS = r"[(\\0)\/.\-*?|&;<>#!]|^\.+|\.+$"
DARWIN_RESERVED_FILENAME_CHARACTERS = r"[\/:*?\"<>|]"

# OS specific reserved filenames
WINDOWS_RESERVED_FILENAMES = (
    "CON", 
    "PRN", 
    "AUX", 
    "NUL",
    "COM1", 
    "COM2", 
    "COM3", 
    "COM4", 
    "COM5", 
    "COM6", 
    "COM7", 
    "COM8", 
    "COM9",
    "LPT1", 
    "LPT2", 
    "LPT3", 
    "LPT4", 
    "LPT5", 
    "LPT6", 
    "LPT7", 
    "LPT8", 
    "LPT9"
)
DARWIN_RESERVED_FILENAMES = (
    ".DS_Store",
    ".Trashes",
    ".VolumeIcon",
    ".Spotlight",
    ".fseventsd",
    ".TemporaryItems",
    ".DocumentRevisions",
    ".AppleDouble"
)