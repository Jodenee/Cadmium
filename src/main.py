"""
MIT License

Copyright (c) 2025 Jodene Borg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.0.0"

import asyncio

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pick import Option, pick

from pytubefix.exceptions import BotDetection

from core.enums import DownloadFormat, MediaType
from core.exceptions import InvalidSettingError, ConfigurationFileCorruptError
from core.custom_types import Configuration, DownloadConfiguration
from core.lib import ClearDirectoryDisplay
from core.utilities.configuration import load_configuration, create_configuration_file
from core.utilities.console import spaced_print
from core.utilities.download import Downloader
from core.utilities.os import clear_directory_files, count_directory_files, try_find_ffmpeg
from core.utilities.validation import parse_youtube_link_type

# Required + default files/directories

project_root_directory: Path = Path(__file__).parent.resolve()

to_download_file: Path = project_root_directory.joinpath("to_download.txt")
configuration_file_path: Path = project_root_directory.joinpath("configuration.json")
temporary_files_directory_path: Path = project_root_directory.joinpath("temporary_files")
downloads_directory_path: Path = project_root_directory.joinpath("downloads")

default_video_download_directory_path: Path = downloads_directory_path.joinpath("video")
default_video_only_download_directory_path: Path = downloads_directory_path.joinpath("video_only")
default_audio_download_directory_path: Path = downloads_directory_path.joinpath("audio_only")
default_best_of_both_download_directory_path: Path = downloads_directory_path.joinpath("best_of_both")
default_custom_download_directory_path: Path = downloads_directory_path.joinpath("custom")

# constant values

configuration: Configuration = load_configuration(configuration_file_path)

temporary_file_extensions = [ ".webp", ".m4a", ".mp4", ".mp3" ]

select_menu_indicator = ">"

download_format_options: Tuple[Option, ...] = (
    Option(DownloadFormat.VIDEO.value, DownloadFormat.VIDEO, "Downloads both video and audio tracks but at low quality."), 
    Option(DownloadFormat.VIDEO_ONLY.value, DownloadFormat.VIDEO_ONLY, "Downloads only the video track but at high quality."), 
    Option(DownloadFormat.AUDIO_ONLY.value, DownloadFormat.AUDIO_ONLY, "Downloads only the audio track but at high quality."), 
    Option(DownloadFormat.BEST_OF_BOTH.value, DownloadFormat.BEST_OF_BOTH, "Downloads both the video and audio tracks but at high quality."),
    Option(DownloadFormat.CUSTOM.value, DownloadFormat.CUSTOM, "Downloads any streams of your choosing.")
)

download_format_to_custom_download_configurations: Dict[DownloadFormat, DownloadConfiguration] = {
    DownloadFormat.VIDEO: {
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_video_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["video_download_location_override"],
        "default_download_location": default_video_download_directory_path
    },
    DownloadFormat.VIDEO_ONLY: {
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_video_only_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["video_only_download_location_override"],
        "default_download_location": default_video_only_download_directory_path
    },
    DownloadFormat.AUDIO_ONLY: {
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_audio_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["audio_download_location_override"],
        "default_download_location": default_audio_download_directory_path
    },
    DownloadFormat.BEST_OF_BOTH: {
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_best_of_both_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["best_of_both_download_location_override"],
        "default_download_location": default_best_of_both_download_directory_path
    },
    DownloadFormat.CUSTOM: {
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_custom_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["custom_download_location_override"],
        "default_download_location": default_custom_download_directory_path
    }
}

# find external dependencies

ffmpeg_executable_path: Optional[Path] = try_find_ffmpeg(configuration)

# program

async def main() -> None:
    if not configuration_file_path.exists(): 
        create_configuration_file(configuration_file_path)

    temporary_files_directory_path.mkdir(exist_ok=True)
    to_download_file.touch()

    downloader: Downloader = Downloader(configuration, temporary_files_directory_path, ffmpeg_executable_path)

    print(f"Cadmium - v{__version__}")

    if not configuration["warning_configuration"]["silence_undeleted_temp_file_warning"]:
        number_of_existing_temp_files: int = count_directory_files(temporary_files_directory_path, temporary_file_extensions)

        if number_of_existing_temp_files > 0: 
            spaced_print(f"WARNING: You have {number_of_existing_temp_files} temporary file(s)!")

    while True:
        download_format: DownloadFormat = pick(
            download_format_options, 
            "Pick which format should the media be downloaded as", 
            indicator=select_menu_indicator
        )[0].value # type: ignore

        download_configuration = download_format_to_custom_download_configurations[download_format]
        download_directory: Path

        if not download_configuration["use_download_location_override"]:
            downloads_directory_path.mkdir(exist_ok=True)
            download_configuration["default_download_location"].mkdir(exist_ok=True)

            download_directory = download_configuration["default_download_location"]
        else:
            custom_download_directory = download_configuration["download_location_override"]

            if (custom_download_directory == None):
                raise InvalidSettingError(f"custom_{str(download_format)}_download_location", "is empty")

            download_directory = Path(custom_download_directory).resolve()

            if (not download_directory.exists()):
                raise InvalidSettingError(f"custom_{str(download_format)}_download_location", "does not exist")
            
            if (not download_directory.is_file()):
                raise InvalidSettingError(f"custom_{str(download_format)}_download_location", "is a file")

        urls: List[str]

        with to_download_file.open("r") as file:
            urls = [ line.removesuffix("\n") for line in file.readlines() if not line.isspace() ]

        for url in urls:
            mediaType = parse_youtube_link_type(url)

            spaced_print(f"Now downloading {mediaType.value} ({url})")

            if (mediaType == MediaType.VIDEO):
                result = await downloader.download_video(url, download_format, download_directory)

                if not result["success"]:
                    spaced_print(result["error_message"])
                    continue
                
                spaced_print(f"Video ({result["youtube_video_title"]}) was downloaded successfully! ({result["download_path"]})")
            else:
                result = await downloader.download_playlist(url, download_format, download_directory)
                spaced_print(f"Playlist ({result["playlist_name"]}) was downloaded successfully! ({result["download_directory_path"]})")


        run_program_again: str = pick(
            ("Yes", "No"), 
            "Would you like to run the program again?", 
            indicator=select_menu_indicator
        )[0] # type: ignore

        if run_program_again == "Yes":
            continue

        # remove temporary files if enabled before exiting
        if configuration["quality_of_life_configuration"]["clear_temporary_files_before_exiting"]:
            total_files_to_remove = count_directory_files(temporary_files_directory_path, temporary_file_extensions)
            clear_directory_display = ClearDirectoryDisplay(
                f"Clearing ({temporary_files_directory_path})", 
                total_files_to_remove, 
                configuration
            )

            clear_directory_files(temporary_files_directory_path, temporary_file_extensions, clear_directory_display.on_progress)

            clear_directory_display.progress_bar.close()
        
        break
                    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BotDetection:
        spaced_print("Cadmium was detected as a bot, please refrain from downloading more videos for a while to prevent getting limited or blocked.")
    except (InvalidSettingError, ConfigurationFileCorruptError) as exception:
        spaced_print(str(exception))
    except KeyboardInterrupt:
        exit(0)
    except BaseException as exception:
        spaced_print(f"Unexpected exception was raised. Please make an issue on the github with this error. \n{exception.__class__.__name__}: {exception}")
    else:
        exit(0)
        
    input("Press enter to close the program... ")