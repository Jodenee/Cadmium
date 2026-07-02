from dataclasses import dataclass
from ffmpeg.types import Option

@dataclass(slots=True)
class FFmpegOptionArgs:
    """Wraps the arguments taken by `FFmpeg.option`."""
    key: str
    value: Option | None = None