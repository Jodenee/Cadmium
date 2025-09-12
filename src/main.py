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

__version__ = "1.0.0"

import asyncio
import sys
import pick

from core.exceptions.impossible_download_path import ImpossibleDownloadPath

ARROW_KEY_UP = 450
ARROW_KEY_DOWN = 456
ARROW_KEY_RIGHT = 261

pick.KEYS_UP += (ARROW_KEY_UP, ord("w"), ord("8"))
pick.KEYS_DOWN += (ARROW_KEY_DOWN, ord("s"), ord("2"))
pick.KEYS_SELECT += (ord("d"), ARROW_KEY_RIGHT )
pick.KEYS_ENTER += (459, )

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from traceback import format_exc as get_traceback
from pick import Option, pick
from pytubefix.exceptions import BotDetection
from sys import exit

from core.enums import DownloadFormat, MediaType
from core.enums.main_menu_option import MainMenuOption
from core.exceptions import InvalidConfigurationError
from core.custom_types import Configuration, DownloadConfiguration
from core.lib import ClearDirectoryDisplay
from core.utilities.configuration import load_configuration, create_configuration_file
from core.utilities.console import print_failed_downloads, spaced_print
from core.utilities.download import Downloader
from core.utilities.os import clear_console, clear_directory_files, count_directory_files, try_find_ffmpeg
from core.utilities.parse import parse_youtube_link_type

# Required + default files/directories

if getattr(sys, "frozen", False):
    project_root_directory: Path = Path(sys.executable).parent.resolve() # If run as an exe
else:
    project_root_directory: Path = Path(__file__).parent.resolve() # if run with python interpreter

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
temporary_file_extensions = [ ".webm", ".m4a", ".mp4", ".mp3" ]
select_menu_indicator = ">"
main_menu_options: Tuple[Option, ...] = (
    Option(MainMenuOption.DOWNLOAD.value, MainMenuOption.DOWNLOAD, "Download videos."),
    Option(f"{MainMenuOption.EDIT_CONFIGURATION.value} (Coming soon)", MainMenuOption.EDIT_CONFIGURATION, "Edit Cadmium's configuration.", enabled=False),
    Option(MainMenuOption.EXIT.value, MainMenuOption.EXIT, "Exit the program.")
)
download_format_menu_options: Tuple[Option, ...] = (
    Option(DownloadFormat.VIDEO.value, DownloadFormat.VIDEO, "Downloads both video and audio tracks but at low quality."), 
    Option(DownloadFormat.VIDEO_ONLY.value, DownloadFormat.VIDEO_ONLY, "Downloads only the video track but at high quality."), 
    Option(DownloadFormat.AUDIO_ONLY.value, DownloadFormat.AUDIO_ONLY, "Downloads only the audio track but at high quality."), 
    Option(DownloadFormat.BEST_OF_BOTH.value, DownloadFormat.BEST_OF_BOTH, "Downloads both the video and audio tracks but at high quality."),
    Option(DownloadFormat.CUSTOM.value, DownloadFormat.CUSTOM, "Downloads any streams of your choosing."),
    Option("back", "back", "Go back to the main menu without downloading anything.")
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
        "use_download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["use_audio_only_download_location_override"],
        "download_location_override": configuration["quality_of_life_configuration"]["download_location_overrides"]["audio_only_download_location_override"],
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

    downloader: Downloader = Downloader(configuration, select_menu_indicator, temporary_files_directory_path, ffmpeg_executable_path)

    if not configuration["warning_configuration"]["silence_existing_temporary_files_warning"]:
        number_of_existing_temp_files: int = count_directory_files(temporary_files_directory_path, temporary_file_extensions)

        if number_of_existing_temp_files > 0: 
            pick(
                [ "Continue" ], 
                f"WARNING: You have {number_of_existing_temp_files} temporary file(s) that can be removed! ({str(temporary_files_directory_path)})", 
                indicator=select_menu_indicator
            )

    while True:
        main_menu_option: MainMenuOption = pick(
            main_menu_options, 
            f"Cadmium - v{__version__} (https://github.com/Jodenee/Cadmium)", 
            indicator=select_menu_indicator
        )[0].value # type: ignore

        if main_menu_option == MainMenuOption.DOWNLOAD:
            download_format: DownloadFormat = pick(
                download_format_menu_options, 
                "Which format should the videos be downloaded as", 
                indicator=select_menu_indicator
            )[0].value # type: ignore

            if download_format == "back":
                continue

            download_configuration = download_format_to_custom_download_configurations[download_format]
            download_directory: Path

            if not download_configuration["use_download_location_override"]:
                downloads_directory_path.mkdir(exist_ok=True)
                download_configuration["default_download_location"].mkdir(exist_ok=True)

                download_directory = download_configuration["default_download_location"]
            else:
                custom_download_directory = download_configuration["download_location_override"]

                if (custom_download_directory == None):
                    raise InvalidConfigurationError(f"{str(download_format)}_download_location_override", "is empty")

                download_directory = Path(custom_download_directory).resolve()

                if (not download_directory.exists()):
                    raise InvalidConfigurationError(f"{str(download_format)}_download_location_override", "does not exist")      
                elif (download_directory.is_file()):
                    raise InvalidConfigurationError(f"{str(download_format)}_download_location_override", "is a file")

            urls: List[str]

            with to_download_file.open("r") as file:
                urls = [ line.removesuffix("\n") for line in file.readlines() if not line.isspace() ]

            if len(urls) <= 0:
                pick(
                    [ "return to main menu" ], 
                    f"No YouTube urls found in ({str(to_download_file)}).",
                    select_menu_indicator
                )
                continue

            for index, url in enumerate(urls):
                mediaType = parse_youtube_link_type(url)

                spaced_print(f"Now downloading {mediaType.value} ({url})") if index > 0 else print(f"Now downloading {mediaType.value} ({url})")

                if mediaType == MediaType.VIDEO:
                    result = await downloader.download_video(url, download_format, download_directory)

                    if result["success"]:
                        spaced_print(f"Video ({result['youtube_video_title']}) was downloaded successfully! ({result['download_path']})")
                    else:
                        spaced_print(f"An error occurred while downloading Video ({result['youtube_video_title']}) {result['error_message']}")
                elif mediaType == MediaType.PLAYLIST:
                    result = await downloader.download_playlist(url, download_format, download_directory)

                    if result["success"]:
                        spaced_print(f"Playlist ({result['playlist_name']}) was downloaded successfully! ({result['download_directory_path']})")
                    else:
                        spaced_print(f"An error occurred while downloading Playlist ({result['playlist_name']})")
                        spaced_print(f"Failed to download the following:")

                        print_failed_downloads(result["failed_downloads"])
                else:
                    result = await downloader.download_channel(url, download_format, download_directory)

                    if result["success"]:
                        spaced_print(f"Channel ({result['channel_name']}) was downloaded successfully! ({result['download_directory_path']})")
                    else:
                        spaced_print(f"An error occurred while downloading Channel ({result['channel_name']})")
                        spaced_print(f"Failed to download the following:")

                        print_failed_downloads(result["failed_downloads"])

            input("\nDownloading complete! (Press enter to continue) ")
            clear_console()
        elif main_menu_option == MainMenuOption.EXIT:
            if configuration["quality_of_life_configuration"]["clear_temporary_files_before_exiting"]:
                total_files_to_remove = count_directory_files(temporary_files_directory_path, temporary_file_extensions)

                if total_files_to_remove > 0:
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
    except (InvalidConfigurationError, ImpossibleDownloadPath) as exception:
        spaced_print(f"Fatal Error: {exception}")
    except KeyboardInterrupt:
        exit(0)
    except BaseException as exception:
        spaced_print(
            f"Fatal Error: Unexpected error was raised. Please make an issue on the GitHub with the following error.\n\n"
            f"{exception.__class__.__name__}: {exception}\n"
            f"Full Traceback:\n{get_traceback()}"
        )
    else:
        exit(0)
    
    input("\nPress enter to close the program... ")
