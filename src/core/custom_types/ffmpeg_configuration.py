from typing import Optional, TypedDict

class FFmpegConfiguration(TypedDict):
    try_find_ffmpeg_path_automatically: bool
    ffmpeg_executable_path: Optional[str]
    