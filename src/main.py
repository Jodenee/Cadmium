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
import pick

# configure custom keybinds

ARROW_KEY_UP = 450
ARROW_KEY_DOWN = 456
ARROW_KEY_RIGHT = 261

pick.KEYS_UP += (ARROW_KEY_UP, ord("w"), ord("8"))
pick.KEYS_DOWN += (ARROW_KEY_DOWN, ord("s"), ord("2"))
pick.KEYS_SELECT += (ARROW_KEY_RIGHT, ord("d") )
pick.KEYS_ENTER += (459, )

from pathlib import Path
from typing import List, Optional, Tuple
from traceback import format_exc as get_traceback
from pick import Option, pick
from pytubefix.exceptions import BotDetection
from sys import exit

from core.enums import DownloadFormat, MediaType
from core.enums.main_menu_option import MainMenuOption
from core.exceptions import InvalidConfigurationError, ImpossibleDownloadPath
from core.custom_types import Configuration
from core.lib import Downloader, ProgressBarFactory
from core.utilities.configuration import load_configuration, create_configuration_file
from core.utilities.console import display_collection_download_result, display_video_download_result, spaced_print
from core.utilities.os import clear_console, clear_directory_files, count_directory_files, try_find_ffmpeg
from core.utilities.parse import parse_youtube_link_type
from core.utilities.constants import CONFIGURATION_FILE_PATH, DEFAULT_DOWNLOAD_LOCATIONS_MAP, DOWNLOAD_FORMAT_MENU_OPTIONS, DOWNLOADS_DIRECTORY_PATH, MAIN_MENU_OPTIONS, SELECT_MENU_INDICATOR, \
    TEMPORARY_FILE_EXTENSIONS, TEMPORARY_FILES_DIRECTORY_PATH, TO_DOWNLOAD_FILE_PATH

# constant values

configuration: Configuration = load_configuration(CONFIGURATION_FILE_PATH)
progress_bar_factory = ProgressBarFactory(configuration)

# Program

async def main() -> None:
    if not CONFIGURATION_FILE_PATH.exists(): 
        create_configuration_file(CONFIGURATION_FILE_PATH)

    # find external dependencies
    ffmpeg_executable_path: Optional[Path] = try_find_ffmpeg(configuration)

    # ensure required files exist
    TEMPORARY_FILES_DIRECTORY_PATH.mkdir(exist_ok=True)
    TO_DOWNLOAD_FILE_PATH.touch()

    # initialise objects
    downloader: Downloader = Downloader(
        configuration, 
        progress_bar_factory, 
        TEMPORARY_FILES_DIRECTORY_PATH, 
        ffmpeg_executable_path
    )

    if not configuration["warning_configuration"]["silence_existing_temporary_files_warning"]:
        number_of_existing_temp_files: int = count_directory_files(TEMPORARY_FILES_DIRECTORY_PATH, TEMPORARY_FILE_EXTENSIONS)

        if number_of_existing_temp_files > 0: 
            pick(
                [ "Continue" ], 
                f"WARNING: You have {number_of_existing_temp_files} temporary file(s) that can be removed! ({str(TEMPORARY_FILES_DIRECTORY_PATH)})", 
                indicator=SELECT_MENU_INDICATOR
            )

    while True:
        main_menu_option: MainMenuOption = pick(
            MAIN_MENU_OPTIONS, 
            f"Cadmium - v{__version__} (https://github.com/Jodenee/Cadmium)", 
            indicator=SELECT_MENU_INDICATOR
        )[0].value # type: ignore

        if main_menu_option == MainMenuOption.DOWNLOAD:
            download_format: DownloadFormat = pick(
                DOWNLOAD_FORMAT_MENU_OPTIONS, 
                "Which format should the videos be downloaded as", 
                indicator=SELECT_MENU_INDICATOR
            )[0].value # type: ignore

            if download_format == "back":
                continue

            download_location_override_configuration = configuration["quality_of_life_configuration"]["download_location_overrides"]
            download_format_str = download_format.replace(" ", "_")

            use_download_location_override = download_location_override_configuration[f"use_{download_format_str}_download_location_override"]
            download_location_override = download_location_override_configuration[f"{download_format_str}_download_location_override"]
            default_download_location = DEFAULT_DOWNLOAD_LOCATIONS_MAP[download_format]

            download_directory: Path

            if not use_download_location_override:
                DOWNLOADS_DIRECTORY_PATH.mkdir(exist_ok=True)
                default_download_location.mkdir(exist_ok=True)

                download_directory = default_download_location
            else:
                if (download_location_override == None):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "is empty")
                elif (not download_location_override.exists()):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "does not exist")      
                elif (download_location_override.is_file()):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "is a file")
                
                download_directory = download_location_override

            urls: List[str]

            with TO_DOWNLOAD_FILE_PATH.open("r") as file:
                urls = [ line.removesuffix("\n") for line in file.readlines() if not line.isspace() ]

            if len(urls) <= 0:
                pick(
                    [ "return to main menu" ], 
                    f"No YouTube urls found in ({str(TO_DOWNLOAD_FILE_PATH)}).",
                    SELECT_MENU_INDICATOR
                )
                continue

            print("Downloading videos...")

            for url in urls:
                mediaType = parse_youtube_link_type(url)
                spaced_print(f"Now downloading {mediaType.value} ({url})")  

                if mediaType == MediaType.VIDEO:
                    results = await downloader.download_video(url, download_format, download_directory)

                    await display_video_download_result(results)
                elif mediaType == MediaType.PLAYLIST:
                    result = await downloader.download_playlist(url, download_format, download_directory)

                    await display_collection_download_result(result)
                else:
                    result = await downloader.download_channel(url, download_format, download_directory)

                    await display_collection_download_result(result)

            input("\nDownloading complete! (Press enter to continue) ")
            clear_console()
        elif main_menu_option == MainMenuOption.EXIT:
            if configuration["quality_of_life_configuration"]["clear_temporary_files_before_exiting"]:
                total_files_to_remove = count_directory_files(TEMPORARY_FILES_DIRECTORY_PATH, TEMPORARY_FILE_EXTENSIONS)

                if total_files_to_remove > 0:
                    clear_directory_progress_bar = progress_bar_factory.clear_directory(
                        f"Clearing ({TEMPORARY_FILES_DIRECTORY_PATH})", 
                        total_files_to_remove
                    )

                    clear_directory_files(TEMPORARY_FILES_DIRECTORY_PATH, TEMPORARY_FILE_EXTENSIONS, clear_directory_progress_bar.on_progress)

                    clear_directory_progress_bar.close()
            
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
