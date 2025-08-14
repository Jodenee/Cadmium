from typing import Dict, List, Literal, Optional, Tuple

from platform import system
from re import sub as re_sub


def safe_os_name(name: str, fallback_name: str, max_length: int = 255) -> str:
    replace_regex: Dict[str, str] = {
        "Windows": r"[\/\\?%*:|\"<>\x7F\x00-\x1F]|^\.+|\.+$",
        "Linux": r"[(\\0)\/.\-*?|&;<>#!]|^\.+|\.+$",
        "Java": r"",
        "": r""
    }
    reserved_filenames: Dict[str, Tuple[str, ...]] = {
        "Windows": (
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
        "Linux": (),
        "Java": (),
        "": () # When the operating system cannot be determined assume no reserved file names exist
    }
    os_name: Literal["Windows", "Linux", "Java", ""] = system() # type: ignore # Function only returns "Windows", "Linux", "Java" and "" only.
    safe_name: str = re_sub(replace_regex[os_name], "", name).strip()
    upper_case_safe_name: str = safe_name.upper()

    for reserved_file_name in reserved_filenames[os_name]:
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
