import logging

from os import environ, system as run_command
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union
from platform import system, machine
from re import Pattern, sub as re_sub

from core.exceptions.impossible_download_path import ImpossibleDownloadPath
from core.utilities.constants import DARWIN_RESERVED_FILENAME_CHARACTERS, DARWIN_RESERVED_FILENAMES, LINUX_RESERVED_FILENAME_CHARACTERS, MATCH_NOTHING, PACKAGED_FFMPEG_BINARIES_DIRECTORY_PATH, \
    WINDOWS_RESERVED_FILENAME_CHARACTERS, WINDOWS_RESERVED_FILENAMES, APPLICATION_LOGGER_NAME
from core.utilities.helpers import choose, collapse_whitespace

from ..custom_types.configuration import Configuration
from ..enums.os import OperatingSystem
from ..enums.cpu_architecture import CpuArchitecture
from ..exceptions.invalid_configuration_error import InvalidConfigurationError

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

# Platform information functions

def get_os() -> OperatingSystem:  
    """Determines the current operating system the application is running on. 

    Determines the current operating system the application is running on. By default `OperatingSystem.UNKNOWN` is returned if the 
    operating system cannot be determined.

    Returns:
        A `OperatingSystem` enum representing the current operating system.
    """

    raw_operating_system = system().upper()
    try:
        operating_system = OperatingSystem[system().upper()]
    except KeyError:
        operating_system = OperatingSystem.UNKNOWN

    logger.debug("raw_operating_system=%s", raw_operating_system)
    logger.debug("operating_system=%s", operating_system.name)

    return operating_system
    

def get_cpu_architecture() -> CpuArchitecture:  
    """Determines the current CPU architecture the application is running on. 

    Determines the current CPU architecture the application is running on. By default `CpuArchitecture.UNSUPPORTED` is returned if the 
    CPU architecture is not officially supported.

    Returns:
        A `OperatingSystem` enum representing the current operating system.
    """

    raw_cpu_architecture_map: Dict[str, CpuArchitecture] = {
        "x86_64": CpuArchitecture.x86_64,
        "AMD64": CpuArchitecture.x86_64,
        "aarch64": CpuArchitecture.ARM64,
        "arm64": CpuArchitecture.ARM64,
        "ARM64": CpuArchitecture.ARM64
    }

    raw_cpu_architecture = machine()

    try:
        cpu_architecture = raw_cpu_architecture_map[raw_cpu_architecture]
    except KeyError:
        cpu_architecture = CpuArchitecture.UNSUPPORTED

    logger.debug("raw_cpu_architecture=%s", raw_cpu_architecture)
    logger.debug("cpu_architecture=%s", cpu_architecture)

    return cpu_architecture


# OS constants
OPERATING_SYSTEM = get_os()
CPU_ARCHITECTURE = get_cpu_architecture()
MAX_OS_PATH_LENGTH = choose(OPERATING_SYSTEM, {
    OperatingSystem.WINDOWS: 255,
    OperatingSystem.DARWIN: 1024
}, 4096)
MAX_OS_FILENAME_LENGTH = choose(OPERATING_SYSTEM, {}, 255)

# OS action functions

def safe_os_name(name: str, fallback_name: str, max_length: int = MAX_OS_FILENAME_LENGTH) -> str:
    """Sanitizes a `string` to be fit for naming a file or folder.

    Sanitizes a `string` to be fit for naming a file or folder. If after sanitization the string is 
    empty or filled with only whitespace, the fallback name is returned.

    Args:
        name: A `string` containing the name to be sanitized.
        fallback_name: A fallback name if after sanitization the string is empty or filled with only whitespace.
        max_length: The maximum length of the name.

    Returns:
        The sanitized `string`.
    """

    replace_regex: Pattern[str] = choose(OPERATING_SYSTEM, {
        OperatingSystem.WINDOWS: WINDOWS_RESERVED_FILENAME_CHARACTERS,
        OperatingSystem.LINUX: LINUX_RESERVED_FILENAME_CHARACTERS,
        OperatingSystem.DARWIN: DARWIN_RESERVED_FILENAME_CHARACTERS,
    }, MATCH_NOTHING)
    reserved_filenames: Tuple[str, ...] = choose(OPERATING_SYSTEM, {
        OperatingSystem.WINDOWS: WINDOWS_RESERVED_FILENAMES,
        OperatingSystem.DARWIN: DARWIN_RESERVED_FILENAMES
    }, ())
    safe_name: str = collapse_whitespace(
        re_sub(replace_regex, "", name)
    )
    upper_case_safe_name: str = safe_name.upper()

    for reserved_file_name in reserved_filenames:
        if reserved_file_name == upper_case_safe_name: 
            logger.debug("upper_case_safe_name==\"%s\" returning fallback_name", reserved_file_name)
            safe_name = fallback_name

    if len(safe_name) == 0: 
        logger.debug("len(safe_name)==0 returning fallback_name")
        safe_name = fallback_name

    return safe_name[:max_length]


def safe_full_filename(
    full_filename: str, 
    fallback_filename: str, 
    filename_prefix: Optional[str] = None, 
    max_length: int = MAX_OS_FILENAME_LENGTH, 
    extension_override: Optional[str] = None
) -> str:
    """Sanitizes a filename (including extension) to be fit for the current operating system.

    Sanitizes a filename (including extension) to be fit for the current operating system. If after sanitization the filename is 
    empty or filled with only whitespace, the fallback filename is returned.

    Args:
        full_filename: A full filename (including extension).
        fallback_filename: A fallback filename if after sanitization the filename is empty or filled with only whitespace.
        filename_prefix: An optional prefix for the filename.
        max_length: The maximum length the filename (including extension) must conform to.
        extension_override: An optional override for the filename's extension.
    Returns:
        The sanitized filename.
    """

    split_full_filename: List[str] = full_filename.rsplit(".", 1)
    filename: str = split_full_filename[0]
    file_extension: str = split_full_filename[len(split_full_filename) - 1] if extension_override == None else extension_override
    max_filename_length: int = max_length - (len(filename_prefix or "") + len(file_extension) + 1) # calculates how long the file's name can be

    logger.debug("split_full_filename=%s", split_full_filename)
    logger.debug("max_filename_length=%s", max_filename_length)
    
    if max_filename_length <= 0:
        return ""

    safe_filename: str = safe_os_name(filename, fallback_filename, max_filename_length)

    return f"{filename_prefix or ''}{safe_filename}.{file_extension}"


def safe_join_directory(
    base: Path, 
    name: str, 
    fallback_name: str
) -> Path:
    """Safely joins a directory with another ensuring the operating system's path limit is not exceeded.

    Args:
        base: A `Path` to a directory.
        name: The name of the directory to join with `base`.
        fallback_name: A fallback directory name if after sanitization the directory name is empty or filled with only whitespace.

    Returns:
        The joined `Path`.

    Raises:
        ImpossibleDownloadPath:
            Raised if the length of the joined path is greater than the operating system's maximum path length.
    """    

    safe_directory_name = safe_os_name(
        name,
        fallback_name
    )
    path = base / safe_directory_name

    logger.debug("path=%s", path)

    if len(str(path)) > MAX_OS_PATH_LENGTH or safe_directory_name == "":
        logger.debug("MAX_OS_PATH_LENGTH=%s", MAX_OS_PATH_LENGTH)
        logger.debug("len_of_path=%s", len(str(path)))
        logger.debug("safe_directory_name=%s", safe_directory_name)

        raise ImpossibleDownloadPath(path)

    return path


def resolve_safe_file_path(
    directory: Path,
    filename: str, 
    fallback_filename: str, 
    filename_prefix: Optional[str] = None, 
    extension_override: Optional[str] = None
) -> Path:
    """Safely joins a directory with a filename by ensuring it does not exceed the operating systems path length limit.

    Args:
        directory: A `Path` to a directory.
        filename: The filename to be joined with `directory`.
        fallback_filename: A fallback filename if after sanitization the filename is empty or filled with only whitespace.
        filename_prefix: An optional prefix to be added to the filename.
        extension_override: An optional override for the filename's extension.

    Returns:
        The resolved full `Path` of the file.

    Raises:
        ImpossibleDownloadPath:
            Raised if the length of the resolved path is greater than the operating system's maximum path length.
    """

    safe_filename = safe_full_filename(
        filename,
        fallback_filename,
        filename_prefix,
        calculate_max_filename_length(directory),
        extension_override
    )

    if safe_filename == "":
        raise ImpossibleDownloadPath(directory)

    return directory / safe_filename


def calculate_max_filename_length(directory: Union[Path, str]) -> int:
    """Calculates the maximum filename length allowed in `directory` to not exceed the operating system's path limit.

    Args:
        directory: A `Pathlike` that leads to a directory.

    Returns:
        The maximum filename length allowed in `directory`.
    """    

    return min(MAX_OS_PATH_LENGTH - (len(str(directory)) + 1), MAX_OS_FILENAME_LENGTH)


def count_directory_files(directory: Path, with_extensions: List[str]) -> int:
    """Counts how many files are inside `directory` with a extensions in `with_extensions`.

    Args:
        directory: A `Pathlike` that leads to a directory.
        with_extensions: A `List` of file extensions to count.

    Returns:
        The total number of files inside `directory` with extension in `with_extensions`.
    """

    return len([
        file for file in directory.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ])


def clear_directory_files(directory: Path, with_extensions: List[str], on_progress: Optional[Callable[[int], None]] = None) -> None:
    """Clears `directory` of files with extension in `with_extensions`.

    Args:
        directory: A `Path` that leads to a directory.
        with_extensions: A `List` of file extensions to count.
        on_progress: A callback function to track the progress of clearing `directory`.
    """

    logger.info("Clearing all files from directory %s with extensions %s", directory, with_extensions)

    files_to_remove = [
        file for file in directory.iterdir() 
        if file.is_file() and file.suffix in with_extensions
    ]

    for file_number, file in enumerate(files_to_remove, 1):
        file.unlink()
        logger.info("Removed file %s", file)

        if on_progress:
            on_progress(file_number)


def try_find_ffmpeg(configuration: Configuration) -> Optional[Path]:
    """Attempts to find an FFmpeg binary according with the user's configurations.

    Args:
        configuration: The user's configurations.  

    Returns:
        An optional `Path` to an FFmpeg binary.

    Raises:
        InvalidConfigurationError:
            Raised if any of the following conditions are met
            
            * `custom_ffmpeg_executable_path` configuration is set but does not exist,
            * `custom_ffmpeg_executable_path` configuration is set but does not lead to a file,
            * `use_path_ffmpeg` is enabled but ffmpeg could not be found in PATH,
            * `use_packaged_ffmpeg` is enabled and OS is unknown or CPU architecture is unsupported,
            * `use_packaged_ffmpeg` is enabled and Packaged FFmpeg binary not found.
    """

    logger.debug("use_ffmpeg=%s", configuration["external_dependency_configuration"]["ffmpeg"]["use_ffmpeg"])

    if not configuration["external_dependency_configuration"]["ffmpeg"]["use_ffmpeg"]:
        return

    path_variable_separator = choose(OPERATING_SYSTEM, {
        OperatingSystem.LINUX: ":"
    }, ";")
    ffmpeg_filename = choose(OPERATING_SYSTEM, {
        OperatingSystem.LINUX: "ffmpeg"
    }, "ffmpeg.exe")
    system_path_variables = environ.get("PATH", "").split(path_variable_separator)

    logger.debug("custom_ffmpeg_executable_path=%r", configuration["external_dependency_configuration"]["ffmpeg"]["custom_ffmpeg_executable_path"])
    logger.debug("use_path_ffmpeg=%r", configuration["external_dependency_configuration"]["ffmpeg"]["use_path_ffmpeg"])
    logger.debug("use_packaged_ffmpeg=%r", configuration["external_dependency_configuration"]["ffmpeg"]["use_packaged_ffmpeg"])

    if configuration["external_dependency_configuration"]["ffmpeg"]["custom_ffmpeg_executable_path"]:
        logger.info("attempting to resolve path to custom ffmpeg executable")
        raw_ffmpeg_path = configuration["external_dependency_configuration"]["ffmpeg"]["custom_ffmpeg_executable_path"]

        if raw_ffmpeg_path:
            ffmpeg_path = Path(raw_ffmpeg_path)

            if not ffmpeg_path.exists():
                raise InvalidConfigurationError("custom_ffmpeg_executable_path", f"{raw_ffmpeg_path} does not exist")
            elif not ffmpeg_path.is_file():
                raise InvalidConfigurationError("custom_ffmpeg_executable_path", f"{raw_ffmpeg_path} does not lead to a file")
            
            logger.info("found ffmpeg executable found at %s", ffmpeg_path)
            
            return ffmpeg_path
    elif configuration["external_dependency_configuration"]["ffmpeg"]["use_path_ffmpeg"]:
        logger.info("attempting to resolve path to ffmpeg executable in PATH")

        for path in system_path_variables:
            ffmpeg_path = Path(path) / ffmpeg_filename

            if ffmpeg_path.exists():
                logger.info("found ffmpeg executable found at %s", ffmpeg_path)
                return ffmpeg_path

        raise InvalidConfigurationError("use_path_ffmpeg", "FFmpeg was not found inside PATH")
    elif configuration["external_dependency_configuration"]["ffmpeg"]["use_packaged_ffmpeg"]:
        logger.info("attempting to resolve packaged ffmpeg executable")

        platform_ffmpeg_directory_name = f"{OPERATING_SYSTEM.value.lower()}_{CPU_ARCHITECTURE.value.lower()}"
        platform_ffmpeg_binary_path = PACKAGED_FFMPEG_BINARIES_DIRECTORY_PATH.joinpath(platform_ffmpeg_directory_name, "bin", ffmpeg_filename)

        if OPERATING_SYSTEM == OperatingSystem.UNKNOWN or CPU_ARCHITECTURE == CpuArchitecture.UNSUPPORTED:
            raise InvalidConfigurationError("use_packaged_ffmpeg", "Could not determine necessary platform specs to load appropriate FFmpeg binary")
        elif not platform_ffmpeg_binary_path.exists():
            raise InvalidConfigurationError("use_packaged_ffmpeg", "Packaged FFmpeg binary does not exist, please do a fresh install of Cadmium to fix this issue")
        
        logger.info("found ffmpeg executable found at %s", platform_ffmpeg_binary_path)
        
        return platform_ffmpeg_binary_path


def clear_console() -> None:
    "Clears all text from console."     

    run_command(choose(OPERATING_SYSTEM, {
        OperatingSystem.WINDOWS: "cls"
    }, "clear"))
