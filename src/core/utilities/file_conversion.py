import logging

from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress
from .constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

async def convert_file(
    ffmpeg_executable_path: Union[str, Path], 
    input_file_paths: List[str | Path], 
    output_file_paths: List[str | Path],
    options: List[str],
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

    for input_file in input_file_paths:
        ffmpeg.input(input_file)

    for output_file in output_file_paths:
        ffmpeg.output(output_file)
    
    for option in options:
        ffmpeg.option(option)

    if progress_callback:
        ffmpeg.on("progress", progress_callback)

    logger.debug("input_file_paths=%s", input_file_paths)
    logger.debug("output_file_paths=%s", output_file_paths)
    logger.debug("options=%s", options)

    try:
        await ffmpeg.execute()
    except:
        if ffmpeg._executed:
            ffmpeg.terminate()
            
        raise
