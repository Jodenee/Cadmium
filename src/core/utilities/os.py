from os import environ, system as run_command
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, TypeVar
from platform import system, machine
from re import sub as re_sub

from ..custom_types.configuration import Configuration
from ..enums.os import OperatingSystem
from ..enums.cpu_architecture import CpuArchitecture
from ..exceptions.invalid_configuration_error import InvalidConfigurationError

# Generics

T = TypeVar('T')

# functions

def get_os() -> OperatingSystem:  
    try:
        return OperatingSystem[system().upper()]
    except KeyError:
        return OperatingSystem.UNKNOWN
    

def get_cpu_architecture() -> CpuArchitecture:  
    raw_cpu_architecture_map: Dict[str, CpuArchitecture] = {
        "x86_64": CpuArchitecture.x86_64,
        "AMD64": CpuArchitecture.x86_64,
        "aarch64": CpuArchitecture.ARM64,
        "arm64": CpuArchitecture.ARM64,
        "ARM64": CpuArchitecture.ARM64
    }

    try:
        raw_cpu_architecture = machine()

        return raw_cpu_architecture_map[raw_cpu_architecture]
    except KeyError:
        return CpuArchitecture.UNSUPPORTED
    

def os_choose(map: Dict[OperatingSystem, T], default: T) -> T:
    try:
        return map[get_os()]
    except KeyError:
        return default
    

def cpu_architecture_choose(map: Dict[CpuArchitecture, T], default: T) -> T:
    try:
        return map[get_cpu_architecture()]
    except KeyError:
        return default


# Constants

MAX_OS_PATH_LENGTH = os_choose({
    OperatingSystem.WINDOWS: 255,
    OperatingSystem.DARWIN: 1024
}, 4096)
MAX_OS_FILENAME_LENGTH = os_choose({}, 255)


def safe_os_name(name: str, fallback_name: str, max_length: int = 255) -> str:
    replace_regex: str = os_choose({
        OperatingSystem.WINDOWS: r"[\/\\?%*:|\"<>\x7F\x00-\x1F]|^\.+|\.+$",
        OperatingSystem.LINUX: r"[(\\0)\/.\-*?|&;<>#!]|^\.+|\.+$",
        OperatingSystem.DARWIN: r"[\/:*?\"<>|]",
    }, r"")
    reserved_filenames: Tuple[str, ...] = os_choose({
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
    }, ())
    safe_name: str = re_sub(replace_regex, "", name).strip()
    upper_case_safe_name: str = safe_name.upper()

    for reserved_file_name in reserved_filenames:
        if reserved_file_name == upper_case_safe_name: 
            safe_name = fallback_name

    if len(safe_name) == 0: 
        safe_name = fallback_name

    return safe_name[:max_length]


def safe_full_filename(
    full_filename: str, 
    fallback_filename: str, 
    filename_prefix: Optional[str] = None, 
    max_length: int = MAX_OS_FILENAME_LENGTH, 
    extension_override: Optional[str] = None
) -> str:
    split_full_filename: List[str] = full_filename.rsplit(".", 1)
    filename: str = split_full_filename[0]
    file_extension: str = split_full_filename[len(split_full_filename) - 1] if extension_override == None else extension_override

    max_filename_length: int = max_length - (len(filename_prefix or "") + len(file_extension) + 1) # calculates how long the file's name can be
    
    if max_filename_length <= 0:
        return ""

    safe_filename: str = safe_os_name(filename, fallback_filename, max_filename_length)

    return f"{filename_prefix or ''}{safe_filename}.{file_extension}"


def count_directory_files(path: Path, with_extensions: List[str]) -> int:
    return len([
        file for file in path.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ])


def clear_directory_files(path: Path, with_extensions: List[str], on_progress: Optional[Callable[[int], None]] = None):
    files_to_remove = [
        file for file in path.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ]

    for file_number, file in enumerate(files_to_remove, 1):
        file.unlink()

        if on_progress:
            on_progress(file_number)


def try_find_ffmpeg(configuration: Configuration, packaged_ffmpeg_binaries_directory_path: Path) -> Optional[Path]:
    if not configuration["external_dependency_configuration"]["ffmpeg"]["use_ffmpeg"]:
        return

    path_variable_separator = os_choose({
        OperatingSystem.LINUX: ":"
    }, ";")
    ffmpeg_filename = os_choose({
        OperatingSystem.LINUX: "ffmpeg"
    }, "ffmpeg.exe")
    system_path_variables = environ.get("PATH", "").split(path_variable_separator)

    if configuration["external_dependency_configuration"]["ffmpeg"]["custom_ffmpeg_executable_path"]:
        raw_ffmpeg_path = configuration["external_dependency_configuration"]["ffmpeg"]["custom_ffmpeg_executable_path"]

        if raw_ffmpeg_path:
            ffmpeg_path = Path(raw_ffmpeg_path)

            if not ffmpeg_path.exists():
                raise InvalidConfigurationError("custom_ffmpeg_executable_path", f"{raw_ffmpeg_path} does not exist")
            elif not ffmpeg_path.is_file():
                raise InvalidConfigurationError("custom_ffmpeg_executable_path", f"{raw_ffmpeg_path} does not lead to a file")
            
            return ffmpeg_path
    elif configuration["external_dependency_configuration"]["ffmpeg"]["use_path_ffmpeg"]:
        for path in system_path_variables:
            ffmpeg_path = Path(path) / ffmpeg_filename

            if ffmpeg_path.exists():
                return ffmpeg_path

        raise InvalidConfigurationError("use_path_ffmpeg", "FFmpeg was not found inside PATH")
    elif configuration["external_dependency_configuration"]["ffmpeg"]["use_packaged_ffmpeg"]:        
        os = get_os()
        cpu_architecture = get_cpu_architecture()
        platform_ffmpeg_directory_name = f"{os.value.lower()}_{cpu_architecture.value.lower()}"
        platform_ffmpeg_binary_path = packaged_ffmpeg_binaries_directory_path.joinpath(platform_ffmpeg_directory_name, "bin", ffmpeg_filename)

        if os == OperatingSystem.UNKNOWN or cpu_architecture == CpuArchitecture.UNSUPPORTED:
            raise InvalidConfigurationError("use_packaged_ffmpeg", "Could not determine necessary platform specs to load appropriate ffmpeg binary")
        elif not platform_ffmpeg_binary_path.exists():
            raise InvalidConfigurationError("use_packaged_ffmpeg", "Packaged ffmpeg binary does not exist, please do a fresh install of Cadmium to fix this issue")
        
        return platform_ffmpeg_binary_path


def clear_console() -> None:
    run_command(os_choose({
        OperatingSystem.WINDOWS: "cls"
    }, "clear"))
