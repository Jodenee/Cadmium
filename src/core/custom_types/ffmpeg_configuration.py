from typing import Optional, TypedDict

class FFmpegConfiguration(TypedDict):
    use_ffmpeg: bool
    use_packaged_ffmpeg: bool
    use_path_ffmpeg: bool
    custom_ffmpeg_executable_path: Optional[str]
    