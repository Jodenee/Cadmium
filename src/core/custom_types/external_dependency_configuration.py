from typing import TypedDict

from .ffmpeg_configuration import FFmpegConfiguration

class ExternalDependencyConfiguration(TypedDict):
    FFmpeg: FFmpegConfiguration
    