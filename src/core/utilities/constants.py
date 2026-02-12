from typing import List
from core.custom_types.configuration import Configuration

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
