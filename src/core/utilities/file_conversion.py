from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress

async def convert_file(
    ffmpeg_executable_path: Union[str, Path], 
    input_file_paths: List[str | Path], 
    output_file_paths: List[str | Path],
    options: Optional[List[str]],
    progress_callback: Callable[[Progress], None]
) -> None:
    ffmpeg = FFmpeg(str(ffmpeg_executable_path))

    for input_file in input_file_paths:
        ffmpeg.input(input_file)

    for output_file in output_file_paths:
        ffmpeg.output(output_file)
    
    if options:
        for option in options:
            ffmpeg.option(option)

    ffmpeg.on("progress", progress_callback)

    try:
        await ffmpeg.execute()
    except:
        ffmpeg.terminate()
        raise
