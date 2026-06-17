from dataclasses import dataclass
from ffmpeg.types import Option

@dataclass(slots=True)
class FFmpegOptionArgs:
    key: str
    value: Option | None = None