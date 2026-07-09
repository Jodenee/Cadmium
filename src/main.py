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

__version__ = "1.1.0"

import asyncio
import pick
import logging
import argparse

# configure custom keybinds

ARROW_KEY_UP = 450
ARROW_KEY_DOWN = 456
ARROW_KEY_RIGHT = 261

pick.KEYS_UP += (ARROW_KEY_UP, ord("w"), ord("W"), ord("8"))
pick.KEYS_DOWN += (ARROW_KEY_DOWN, ord("s"), ord("S"), ord("2"))
pick.KEYS_SELECT += (ARROW_KEY_RIGHT, ord("d"), ord("D") )
pick.KEYS_ENTER += (459, )

from pathlib import Path
from typing import Optional
from pick import pick
from pytubefix.exceptions import BotDetection
from sys import exit
from logging.handlers import RotatingFileHandler

from core.enums import DownloadFormat, MediaType
from core.enums.main_menu_option import MainMenuOption
from core.exceptions import InvalidConfigurationError
from core.custom_types import Configuration
from core.lib import Downloader, ProgressBarFactory
from core.utilities.configuration import load_configuration, create_configuration_file
from core.utilities.console import display_collection_download_result, display_video_download_result, spaced_print
from core.utilities.os import clear_console, count_directory_files, try_find_ffmpeg, OPERATING_SYSTEM, CPU_ARCHITECTURE
from core.utilities.parse import parse_youtube_link_type
from core.utilities.constants import CONFIGURATION_FILE_PATH, DEFAULT_DOWNLOAD_LOCATIONS_MAP, DOWNLOAD_FORMAT_MENU_OPTIONS, DOWNLOADS_DIRECTORY_PATH, MAIN_MENU_OPTIONS, SELECT_MENU_INDICATOR, \
    TEMPORARY_FILE_EXTENSIONS, TEMPORARY_FILES_DIRECTORY_PATH, TO_DOWNLOAD_FILE_PATH, LOGGING_DIRECTORY_PATH, APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

parser = argparse.ArgumentParser(
    description=(
        "Cadmium is a python command line application made to conveniently download youtube videos for without the risk of accidentally " 
        "installing malware or getting overwhelmed with ads. It's a great all in one tool that has all the features you'll ever need for downloading youtube videos. "
        "Make sure to check for updates here -> https://github.com/Jodenee/Cadmium/releases/latest"
    )
)
parser.add_argument(
    "--initialise_only", 
    action="store_true",
    help="To initialise the files cadmium requires and exit immediately after"
)

# constant values

configuration: Configuration = load_configuration(CONFIGURATION_FILE_PATH)
progress_bar_factory = ProgressBarFactory(configuration)

# Program

def bootstrap() -> None:
    parsed_arguments = parser.parse_args()

    # Create configuration file if it does not exist
    if not CONFIGURATION_FILE_PATH.exists(): 
        create_configuration_file(CONFIGURATION_FILE_PATH)

    # Configure application logging
    global_logger = logging.getLogger()

    global_logger.handlers.clear()

    global_logger.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    if configuration["logging_configuration"]["enabled"]:
        LOGGING_DIRECTORY_PATH.mkdir(exist_ok=True, parents=True)

        handler = RotatingFileHandler(
            LOGGING_DIRECTORY_PATH / "cadmium.log",
            maxBytes=2 * 1024 * 1024, # 2MB
            backupCount=3,
            encoding="utf-8"
        )
    else: 
        handler = logging.NullHandler()

    handler.setFormatter(formatter)
    global_logger.addHandler(handler)

    # Ensure required directories and files exist
    TEMPORARY_FILES_DIRECTORY_PATH.mkdir(exist_ok=True, parents=True)
    TO_DOWNLOAD_FILE_PATH.touch()

    if parsed_arguments.initialise_only:
        exit(0)


async def main() -> None:
    bootstrap()

    logger = logging.getLogger(APPLICATION_LOGGER_NAME)

    logger.info("running Cadmium v%s", __version__)
    logger.debug("OPERATING_SYSTEM=%s CPU_ARCHITECTURE=%s", OPERATING_SYSTEM.name, CPU_ARCHITECTURE.name)

    # Find external dependencies
    ffmpeg_executable_path: Optional[Path] = try_find_ffmpeg(configuration)

    # Initialise objects
    downloader: Downloader = Downloader(
        configuration, 
        progress_bar_factory, 
        TEMPORARY_FILES_DIRECTORY_PATH, 
        ffmpeg_executable_path
    )

    # Warn user if temporary files exist
    if not configuration["warning_configuration"]["silence_existing_temporary_files_warning"]:
        number_of_existing_temp_files: int = count_directory_files(TEMPORARY_FILES_DIRECTORY_PATH, TEMPORARY_FILE_EXTENSIONS)

        if number_of_existing_temp_files > 0: 
            pick(
                [ "Continue" ], 
                f"WARNING: You have {number_of_existing_temp_files} temporary file(s) that can be removed! ({str(TEMPORARY_FILES_DIRECTORY_PATH)})", 
                indicator=SELECT_MENU_INDICATOR
            )

    while True:
        logger.info("viewing main menu")

        main_menu_option: MainMenuOption = pick(
            MAIN_MENU_OPTIONS, 
            f"Cadmium - v{__version__} (https://github.com/Jodenee/Cadmium)", 
            indicator=SELECT_MENU_INDICATOR
        )[0].value # type: ignore

        logger.debug("main_menu_option=%s", main_menu_option.name)

        if main_menu_option == MainMenuOption.DOWNLOAD:
            download_format: DownloadFormat = pick(
                DOWNLOAD_FORMAT_MENU_OPTIONS, 
                "Which format should the videos be downloaded as", 
                indicator=SELECT_MENU_INDICATOR
            )[0].value # type: ignore

            logger.debug("download_format=%s", download_format)

            if download_format == "back":
                continue

            download_location_override_configuration = configuration["quality_of_life_configuration"]["download_location_overrides"]
            delete_temporary_files = configuration["download_behavior_configuration"]["automatically_delete_temporary_files_after_download"]
            download_format_str = download_format.replace(" ", "_")

            use_download_location_override = download_location_override_configuration[f"use_{download_format_str}_download_location_override"]
            download_location_override = download_location_override_configuration[f"{download_format_str}_download_location_override"]
            default_download_location = DEFAULT_DOWNLOAD_LOCATIONS_MAP[download_format]

            logger.debug("use_download_location_override=%s", use_download_location_override)

            download_directory: Path

            if use_download_location_override:
                if (download_location_override == None):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "is empty")
                elif (not download_location_override.exists()):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "does not exist")      
                elif (download_location_override.is_file()):
                    raise InvalidConfigurationError(f"{download_format_str}_download_location_override", "is a file")

                download_directory = download_location_override
            else:
                DOWNLOADS_DIRECTORY_PATH.mkdir(exist_ok=True, parents=True)
                default_download_location.mkdir(exist_ok=True, parents=True)

                download_directory = default_download_location

            logger.debug("download_directory=%s", download_directory)

            urls: list[str]

            with TO_DOWNLOAD_FILE_PATH.open("r") as file:
                urls = [ line.removesuffix("\n") for line in file.readlines() if not line.isspace() ]

            logger.debug("urls=%s", urls)

            if len(urls) <= 0:
                pick(
                    [ "return to main menu" ], 
                    f"No YouTube urls found in ({str(TO_DOWNLOAD_FILE_PATH)}).",
                    SELECT_MENU_INDICATOR
                )
                continue

            print("Downloading videos...")

            for url in urls:
                parse_result = parse_youtube_link_type(url)

                if parse_result.success is False:
                    spaced_print(f"Skipping ({url}) as it could not be parsed...")
                    continue

                spaced_print(f"Now downloading {parse_result.mediaType.value} ({url})")  

                if parse_result.mediaType == MediaType.VIDEO:
                    results = await downloader.download_video(url, download_format, download_directory)

                    await display_video_download_result(results)
                elif parse_result.mediaType == MediaType.PLAYLIST:
                    result = await downloader.download_playlist(url, download_format, download_directory)

                    await display_collection_download_result(result)
                else:
                    result = await downloader.download_channel(url, download_format, download_directory)

                    await display_collection_download_result(result)

            if delete_temporary_files and downloader.temporary_file_storage.has_files:
                spaced_print("Removing temporary files...")
                downloader.temporary_file_storage.remove_temporary_files()
                spaced_print("Temporary files successfully removed.")

            input("\nDownloading complete! (Press enter to continue) ")
            clear_console()
        elif main_menu_option == MainMenuOption.EXIT:
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BotDetection:
        logger.error("cadmium was detected as a bot by YouTube")
        spaced_print("Cadmium was detected as a bot, please refrain from downloading more videos for a while to prevent getting limited or blocked.")
    except InvalidConfigurationError as exception:
        logger.exception("cadmium ran into a fatal exception")
        spaced_print(f"Fatal Error: {exception}")
    except KeyboardInterrupt:
        logger.info("Exiting application")
        exit(0)
    except SystemExit as e:
        exit(0)
    except BaseException:
        logger.exception("cadmium ran into an unexpected exception")

        spaced_print(
            f"Fatal Error: Cadmium ran into an unexpected error." 
            "\n\nDear user,\nApologies for the inconvenience, If you would like to see this problem fixed please consider going to Cadmium's reporting page (https://github.com/Jodenee/Cadmium/issues/new?template=bug_report.md) and creating a report by following the steps shown in the template. " 
            "Thank you"
        )
    else:
        logger.info("Exiting application")
        exit(0)
    
    input("\nPress enter to close the program... ")
    logger.info("Exiting application")
