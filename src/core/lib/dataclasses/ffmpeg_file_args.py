from dataclasses import dataclass
from pathlib import Path
from ffmpeg.types import Option

@dataclass(slots=True)
class FFmpegFileArgs:
    """Wraps the arguments taken by `FFmpeg.input` or `FFmpeg.output`"""

    url: str | Path
    options: dict[str, Option | None] | None = None