import sys
from pathlib import Path
from re import compile as compile_regex

from pick import Option

from ..custom_types.configuration import Configuration
from ..enums.download_format import DownloadFormat
from ..enums.main_menu_option import MainMenuOption

# General constants to be used within the application
TEMPORARY_FILE_EXTENSIONS: list[str] = [ ".webm", ".m4a", ".mp4", ".mp3" ]
SELECT_MENU_INDICATOR: str = ">"
DEFAULT_CONFIGURATION: Configuration = {
    "download_behavior_configuration": {
        "skip_existing_files": True,
        "automatically_delete_temporary_files_after_download": True,

        "convert_video_downloads": True,
        "convert_video_only_downloads": True,
        "convert_audio_only_downloads": True,
        "merge_best_of_both_downloads_into_one_file": True,
        "convert_custom_downloads": True,
        
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
        
        "display_chosen_stream_on_start_of_download": True
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
    },
    "logging_configuration": {
        "enabled": True
    }
}

# Constant paths

if getattr(sys, "frozen", False):
    # If ran as an executable file
    PROJECT_ROOT_DIRECTORY: Path = Path(sys.executable).parent.resolve()
    BINARIES_DIRECTORY_PATH: Path = PROJECT_ROOT_DIRECTORY / "_internal" / "core" / "bin"
else:
    # if ran with Python
    PROJECT_ROOT_DIRECTORY: Path = Path(__file__).parents[2].resolve() 
    BINARIES_DIRECTORY_PATH: Path = PROJECT_ROOT_DIRECTORY / "core" / "bin"

PACKAGED_FFMPEG_BINARIES_DIRECTORY_PATH: Path = BINARIES_DIRECTORY_PATH / "ffmpeg"

TO_DOWNLOAD_FILE_PATH: Path = PROJECT_ROOT_DIRECTORY / "to_download.txt"
CONFIGURATION_FILE_PATH: Path = PROJECT_ROOT_DIRECTORY / "configuration.json"
TEMPORARY_FILES_DIRECTORY_PATH: Path = PROJECT_ROOT_DIRECTORY / "temporary_files"
DOWNLOADS_DIRECTORY_PATH: Path = PROJECT_ROOT_DIRECTORY / "downloads"
LOGGING_DIRECTORY_PATH: Path = PROJECT_ROOT_DIRECTORY / "logs"

DEFAULT_DOWNLOAD_LOCATIONS_MAP: dict[DownloadFormat, Path] = {
    DownloadFormat.VIDEO: DOWNLOADS_DIRECTORY_PATH / "video",
    DownloadFormat.VIDEO_ONLY: DOWNLOADS_DIRECTORY_PATH / "video_only",
    DownloadFormat.AUDIO_ONLY: DOWNLOADS_DIRECTORY_PATH / "audio_only",
    DownloadFormat.BEST_OF_BOTH: DOWNLOADS_DIRECTORY_PATH / "best_of_both",
    DownloadFormat.CUSTOM: DOWNLOADS_DIRECTORY_PATH / "custom"
}

# Menu options
MAIN_MENU_OPTIONS: tuple[Option, ...] = (
    Option(MainMenuOption.DOWNLOAD.value, MainMenuOption.DOWNLOAD, "Download videos."),
    Option(f"{MainMenuOption.EDIT_CONFIGURATION.value} (Coming soon)", MainMenuOption.EDIT_CONFIGURATION, "Edit Cadmium's configuration.", enabled=False),
    Option(MainMenuOption.EXIT.value, MainMenuOption.EXIT, "Exit the program.")
)
DOWNLOAD_FORMAT_MENU_OPTIONS: tuple[Option, ...] = (
    Option(DownloadFormat.VIDEO.value, DownloadFormat.VIDEO, "Downloads both video and audio tracks but at low quality."), 
    Option(DownloadFormat.VIDEO_ONLY.value, DownloadFormat.VIDEO_ONLY, "Downloads only the video track but at high quality."), 
    Option(DownloadFormat.AUDIO_ONLY.value, DownloadFormat.AUDIO_ONLY, "Downloads only the audio track but at high quality."), 
    Option(DownloadFormat.BEST_OF_BOTH.value, DownloadFormat.BEST_OF_BOTH, "Downloads both the video and audio tracks but at high quality."),
    Option(DownloadFormat.CUSTOM.value, DownloadFormat.CUSTOM, "Downloads any streams of your choosing."),
    Option("back", "back", "Go back to the main menu without downloading anything.")
)

# Media parsing regexes used to parse media type from url.
YOUTUBE_VIDEO_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/(?:watch\?v=|shorts\/)[\w\-]{11}(?:[&\?]\S*)?$")
YOUTUBE_PLAYLIST_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w\-]+$")
YOUTUBE_CHANNEL_REGEX = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/@[\w\-\.]+$")

# OS specific regexes for removing reserved characters from filenames
WINDOWS_RESERVED_FILENAME_CHARACTERS = compile_regex(r"[\/\\?%*:|\"<>\x7F\x00-\x1F]|^\.+|\.+$")
LINUX_RESERVED_FILENAME_CHARACTERS = compile_regex(r"[(\\0)\/.\-*?|&;<>#!]|^\.+|\.+$")
DARWIN_RESERVED_FILENAME_CHARACTERS = compile_regex(r"[\/:*?\"<>|]")

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

# Error messages
UNABLE_TO_FIND_A_SUITABLE_STREAM_ERROR_MESSAGE = "Video ({video_title}) could not find a suitable stream."
VIDEO_DOWNLOAD_CANCELLED_ERROR_MESSAGE = "Video ({video_title}) download has been cancelled."
ALREADY_EXISTS_AT_PATH_ERROR_MESSAGE = "Already exists at ({path})."

# Miscellaneous regexes
MATCH_NOTHING = compile_regex(r"")
MATCH_CONSECUTIVE_SPACES = compile_regex(r"\s+")

# Logging
APPLICATION_LOGGER_NAME = "cadmium"