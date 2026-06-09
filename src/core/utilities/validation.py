from pathlib import Path
from typing import Optional

from ..exceptions.invalid_configuration_error import InvalidConfigurationError

def ensure_can_use_ffmpeg(
    ffmpeg_executable_path: Optional[Path], 
    file_extension: Optional[str], 
    file_extension_configuration_name: str
) -> None:
    """Ensures that ffmpeg can be used by checking if all the required conditions are met.

    Args:
        ffmpeg_executable_path: An optional Path to the ffmpeg executable to be used.
        file_extension: The file extension to be converted to.
        file_extension_configuration_name: the file extension configuration name.

    Raises:
        InvalidConfigurationError: 
            Raised if any of the following conditions are met

            * `ffmpeg_executable_path` is None.
            * `file_extension` is None.
            * Length of `file_extension` is 0.
    """

    if ffmpeg_executable_path == None:
        raise InvalidConfigurationError(
            "FFmpeg", 
            "cannot convert videos without FFmpeg, please enable \"try_find_ffmpeg_path_automatically\" or manually set the path to the executable using the \"ffmpeg_executable_path\" setting"
        )
    elif file_extension == None or len(file_extension.strip()) == 0:
        raise InvalidConfigurationError(file_extension_configuration_name, "is empty")
