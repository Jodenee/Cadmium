from pathlib import Path
from typing import Optional

from core.exceptions.invalid_configuration_error import InvalidConfigurationError

def ensure_can_use_ffmpeg(
    should_convert: bool, 
    ffmpeg_executable_path: Optional[Path], 
    file_extension: Optional[str], 
    file_extension_configuration_name: str
) -> None:  
    if not should_convert: return

    if ffmpeg_executable_path == None:
        raise InvalidConfigurationError("FFmpeg", "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting")
    elif file_extension == None or len(file_extension.strip()) == 0:
        raise InvalidConfigurationError(file_extension_configuration_name, "is empty")
