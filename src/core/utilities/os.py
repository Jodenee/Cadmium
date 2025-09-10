from os import environ, system as run_command
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, TypeVar
from platform import system
from re import sub as re_sub

from ..custom_types.configuration import Configuration
from ..enums.os import OperatingSystem
from ..exceptions.invalid_configuration_error import InvalidConfigurationError

# Generics

T = TypeVar('T')

# functions

def get_os() -> OperatingSystem:  
    try:
        return OperatingSystem[system().upper()]
    except KeyError:
        return OperatingSystem.UNKNOWN
    

def os_choose(map: Dict[OperatingSystem, T], default: T) -> T:
    try:
        return map[get_os()]
    except KeyError:
        return default


def safe_os_name(name: str, fallback_name: str, max_length: int = 255) -> str:
    replace_regex: Dict[OperatingSystem, str] = {
        OperatingSystem.WINDOWS: r"[\/\\?%*:|\"<>\x7F\x00-\x1F]|^\.+|\.+$",
        OperatingSystem.LINUX: r"[(\\0)\/.\-*?|&;<>#!]|^\.+|\.+$",
        OperatingSystem.DARWIN: r"[\/:*?\"<>|]",
        OperatingSystem.UNIX: r"",
        OperatingSystem.JAVA: r"",
        OperatingSystem.IOS: r"",
        OperatingSystem.ANDROID: r"",
        OperatingSystem.UNKNOWN: r""
    }
    reserved_filenames: Dict[OperatingSystem, Tuple[str, ...]] = {
        OperatingSystem.WINDOWS: (
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
        ),
        OperatingSystem.LINUX: (),
        OperatingSystem.DARWIN: (
            ".DS_Store",
            ".Trashes",
            ".VolumeIcon",
            ".Spotlight",
            ".fseventsd",
            ".TemporaryItems",
            ".DocumentRevisions",
            ".AppleDouble"
        ),
        OperatingSystem.UNIX: (),
        OperatingSystem.JAVA: (),
        OperatingSystem.IOS: (),
        OperatingSystem.ANDROID: (),
        OperatingSystem.UNKNOWN: ()
    }
    os: OperatingSystem = get_os()
    safe_name: str = re_sub(replace_regex[os], "", name).strip()
    upper_case_safe_name: str = safe_name.upper()

    for reserved_file_name in reserved_filenames[os]:
        if reserved_file_name == upper_case_safe_name: 
            safe_name = fallback_name

    if len(safe_name) == 0: 
        safe_name = fallback_name

    return safe_name[:max_length]


def safe_full_filename(full_filename: str, fallback_filename: str, filename_prefix: Optional[str] = None, max_length: int = 255, extension_override: Optional[str] = None) -> str:
    split_full_filename: List[str] = full_filename.rsplit(".", 1)
    filename: str = split_full_filename[0]
    file_extension: str = split_full_filename[len(split_full_filename) - 1] if extension_override == None else extension_override

    if filename_prefix is None:
        max_filename_length: int = max_length - (len(file_extension) + 1) # calculates how long the file's name can be
        safe_filename: str = safe_os_name(filename, fallback_filename, max_filename_length)

        return f"{safe_filename}.{file_extension}"
    else:
        max_filename_length: int = max_length - (len(file_extension) + len(filename_prefix) + 1) # calculates how long the file's name can be
        safe_filename: str = safe_os_name(filename, fallback_filename, max_filename_length)

        return f"{filename_prefix}{safe_filename}.{file_extension}"


def count_directory_files(path: Path, with_extensions: List[str]) -> int:
    return len([
        file for file in path.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ])


def clear_directory_files(path: Path, with_extensions: List[str], on_progress: Optional[Callable[[int], None]]):
    files_to_remove = [
        file for file in path.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ]

    for file_number, file in enumerate(files_to_remove, 1):
        file.unlink()

        if on_progress:
            on_progress(file_number)


def try_find_ffmpeg(configuration: Configuration) -> Optional[Path]:
    path_variable_separator = os_choose({
        OperatingSystem.LINUX: ":"
    }, ";")
    ffmpeg_filename = os_choose({
        OperatingSystem.LINUX: "ffmpeg"
    }, "ffmpeg.exe")
    system_path_variables = environ.get("PATH", "").split(path_variable_separator)

    if configuration["external_dependency_configuration"]["FFmpeg"]["try_find_ffmpeg_path_automatically"] and not configuration["external_dependency_configuration"]["FFmpeg"]["ffmpeg_executable_path"]:
        for path in system_path_variables:
            ffmpeg_path = Path(path) / ffmpeg_filename

            if ffmpeg_path.exists():
                return ffmpeg_path
    else:
        raw_ffmpeg_path = configuration["external_dependency_configuration"]["FFmpeg"]["ffmpeg_executable_path"]

        if raw_ffmpeg_path:
            ffmpeg_path = Path(raw_ffmpeg_path)

            if not ffmpeg_path.exists():
                raise InvalidConfigurationError("ffmpeg_path", f"{raw_ffmpeg_path} does not exist")
            
            return ffmpeg_path


def clear_console() -> None:
    run_command(os_choose({
        OperatingSystem.WINDOWS: "cls"
    }, "clear"))
