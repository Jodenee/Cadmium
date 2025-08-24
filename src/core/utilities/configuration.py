from pathlib import Path
from typing import Any, Dict, Optional
from json import loads as json_loads, dumps as json_dumps

from ..custom_types import Configuration

default_configuration: Configuration = {
    "download_behavior_configuration": {
        "skip_existing_files": True,
        "convert_video_downloads": False,
        "convert_video_only_downloads": False,
        "convert_audio_only_downloads": False,
        "merge_best_of_both_downloads_into_one_file": False,
        "convert_video_downloads_to": "mp4",
        "convert_video_only_downloads_to": "mp4",
        "convert_audio_only_downloads_to": "mp3",
        "best_of_both_merged_file_format": "mp4"
    },
    "quality_of_life_configuration": {
        "custom_download_locations": {
            "use_custom_video_download_location": False,
            "use_custom_video_only_download_location": False,
            "use_custom_audio_download_location": False,
            "use_custom_best_of_both_download_location": False,
            
            "custom_video_download_location": "",
            "custom_video_only_download_location": "",
            "custom_audio_download_location": "",
            "custom_best_of_both_download_location": ""
        },
        "put_playlist_videos_in_folder": True,
        "display_chosen_stream_on_start_of_download": True,
        "clear_temporary_files_before_exiting": False
    },
    "warning_configuration": {
        "silence_undeleted_temp_file_warning": False,
        "silence_already_exists_warning": False
    },
    "ui_configuration": {
        "custom_download_bar_colour": None,
        "custom_convert_bar_colour": None,
        "custom_clear_directory_bar_colour": None
    }
}


def create_configuration_file(path: Path, configuration: Optional[Configuration] = None) -> None:
    file_content: str = json_dumps(configuration if configuration != None else default_configuration, indent=4)

    with path.open("a") as file:
        file.write(file_content)


def load_configuration(config_file_path: Path) -> Configuration:
    try:
        with config_file_path.open("r") as config_file:
            json_data: Dict[str, Any] = json_loads(config_file.read())

            return Configuration(**json_data)
    except BaseException:
        return default_configuration
