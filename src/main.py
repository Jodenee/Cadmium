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

from pytubefix.exceptions import PytubeFixError, BotDetection
from ffmpeg import FFmpegError

from pathlib import Path
from typing import Dict, List

from enums import DownloadFormat, MediaType
from exceptions import DownloadDirectoryIsAFileError, PathDoesNotExistError, SettingCorruptError, SettingNotFoundError, VideoDownloadSkipped
from custom_types import Configuration, DownloadConfiguration
from utilities.configuration import load_configuration, create_configuration_file
from utilities.console import spaced_input, spaced_print
from utilities.download import Downloader
from utilities.validation import parse_youtube_link_type

# Required + default files/directories

project_root_directory: Path = Path(__file__).parent.resolve()

to_download_file: Path = project_root_directory.joinpath("to_download.txt")
configuration_file_path: Path = project_root_directory.joinpath("configuration.json")
temp_files_directory_path: Path = project_root_directory.joinpath("temporary_files")
downloads_folder_directory_path: Path = project_root_directory.joinpath("downloads")

default_video_download_directory_path: Path = downloads_folder_directory_path.joinpath("video")
default_video_only_download_directory_path: Path = downloads_folder_directory_path.joinpath("video_only")
default_audio_download_directory_path: Path = downloads_folder_directory_path.joinpath("audio_only")
default_best_of_both_download_directory_path: Path = downloads_folder_directory_path.joinpath("best_of_both")

# constant values

configuration: Configuration = load_configuration(configuration_file_path)

download_formats = (
    DownloadFormat.VIDEO, 
    DownloadFormat.VIDEO_ONLY, 
    DownloadFormat.AUDIO_ONLY, 
    DownloadFormat.BEST_OF_BOTH
)

download_format_to_custom_download_configurations: Dict[DownloadFormat, DownloadConfiguration] = {
    DownloadFormat.VIDEO: {
        "use_custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["use_custom_video_download_location"],
        "custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["custom_video_download_location"],
        "default_download_location": default_video_download_directory_path
    },
    DownloadFormat.VIDEO_ONLY: {
        "use_custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["use_custom_video_only_download_location"],
        "custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["custom_video_only_download_location"],
        "default_download_location": default_video_only_download_directory_path
    },
    DownloadFormat.AUDIO_ONLY: {
        "use_custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["use_custom_audio_download_location"],
        "custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["custom_audio_download_location"],
        "default_download_location": default_audio_download_directory_path
    },
    DownloadFormat.BEST_OF_BOTH: {
        "use_custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["use_custom_best_of_both_download_location"],
        "custom_download_location": configuration["quality_of_life_configuration"]["custom_download_locations"]["custom_best_of_both_download_location"],
        "default_download_location": default_best_of_both_download_directory_path
    }
}

def main() -> None:
    if not configuration_file_path.exists(): 
        create_configuration_file(configuration_file_path)
    if not temp_files_directory_path.exists(): 
        temp_files_directory_path.mkdir()
    if not to_download_file.exists(): 
        to_download_file.touch()

    downloader: Downloader = Downloader(configuration, temp_files_directory_path)

    if not configuration["warning_configuration"]["silence_undeleted_temp_file_warning"]:
        number_of_existing_temp_files: int = len([
            file for file in temp_files_directory_path.iterdir() if file.is_file()
        ])

        if number_of_existing_temp_files > 0: 
            spaced_print(f"WARNING: You have {number_of_existing_temp_files} undeleted temp file(s)!")

    spaced_print(f"Cadmium - v{__version__}")

    while True:
        print(f"Download formats: ({ ", ".join(download_formats) })")
        download_format_input: str = spaced_input("Select the format the media will be downloaded as: ").upper() # TODO: use a menu and validate input to prevent a key error

        download_format = DownloadFormat[download_format_input]

        download_configuration = download_format_to_custom_download_configurations[download_format]
        download_directory: Path

        if (not download_configuration["use_custom_download_location"]):
            download_directory = download_configuration["default_download_location"]
        else:
            custom_download_directory = download_configuration["custom_download_location"]

            if (custom_download_directory == None):
                print("path is empty")
                exit(1)

            download_directory = Path(custom_download_directory).resolve()

            if (not download_directory.exists()):
                print("path is not valid")
                exit(1)

        urls: List[str]

        with to_download_file.open("r") as file:
            urls = [line.removesuffix("\n") for line in file.readlines() if not line.isspace()]

        for url in urls:
            mediaType = parse_youtube_link_type(url)

            if (mediaType == MediaType.VIDEO):
                youtube_video_title, download_path = downloader.download_video(url, download_format, download_directory)
                spaced_print(f"Video ({youtube_video_title}) was downloaded successfully! ({download_path})")
            else:
                playlist_name, download_path = downloader.download_playlist(url, download_format, download_directory)
                spaced_print(f"Playlist ({playlist_name}) was downloaded successfully! ({download_path})")


        download_again_user_response: str = spaced_input("Would you like to download anything else? (y/n) ").lower()

        if download_again_user_response == "y":
            pass
        elif download_again_user_response == "n":
            break
        else:
            spaced_print("Invalid input given! Defaulted to n...")
            break

if __name__ == "__main__":
    try:
        main()
    except BotDetection:
        spaced_print("Cadmium was detected as a bot, please refrain from downloading more videos for a while to prevent getting limited or blocked.")
    except (SettingNotFoundError, PathDoesNotExistError, DownloadDirectoryIsAFileError, SettingCorruptError) as exception:
        spaced_print(str(exception))
    except (FFmpegError, PytubeFixError) as exception:
        spaced_print(f"Exception: {exception.__class__.__name__}: {exception}")
    except KeyboardInterrupt:
        exit(0)
    except BaseException as exception:
        spaced_print(f"Unexpected exception was raised. Please make an issue on the github with this error. \n{exception.__class__.__name__}: {exception}")
    else:
        exit(0)
        
    input("Press enter to close the program... ")