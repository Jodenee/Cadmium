import logging

from pathlib import Path
from typing import Callable, Optional, Union
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress
from ffmpeg.types import Option

from ..lib.dataclasses import FFmpegFileArgs, FFmpegOptionArgs
from .constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

async def convert_file(
    ffmpeg_executable_path: str | Path, 
    input_files: tuple[FFmpegFileArgs, ...], 
    output_files: tuple[FFmpegFileArgs, ...],
    options: tuple[FFmpegOptionArgs, ...],
    progress_callback: Optional[Callable[[Progress], None]] = None
) -> None:
    """Converts one or more files into one or more output files.

    Args:
        ffmpeg_executable_path: A `Path` to the FFmpeg executable to be used.
        input_file_paths: A list of paths to the files used as input.
        output_file_paths: A list of paths to be used to create the output files.
        options: A list of ffmpeg options.
        progress_callback: A callback function used to track conversion progress.

    Raises:
        FFmpegError:
            If FFmpeg process returns non-zero exit status.
    """    

    ffmpeg = FFmpeg(str(ffmpeg_executable_path))

    for input_file in input_files:
        ffmpeg.input(input_file.url, input_file.options)

    for output_file in output_files:
        ffmpeg.output(output_file.url, output_file.options)
    
    for option in options:
        ffmpeg.option(option.key, option.value)

    if progress_callback:
        ffmpeg.on("progress", progress_callback)

    logger.debug("input_files=%s", input_files)
    logger.debug("output_files=%s", output_files)
    logger.debug("options=%s", options)

    try:
        await ffmpeg.execute()
    except:
        if ffmpeg._executed:
            ffmpeg.terminate()
            
        raise
