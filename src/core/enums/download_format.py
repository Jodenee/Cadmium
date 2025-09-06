import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    try: 
        from strenum import StrEnum 
    except ImportError as e: 
        print("required package strenum not found, please ensure all the required packages have been installed before running Cadmium.")
        exit(1)

class DownloadFormat(StrEnum):
    VIDEO        = "video"
    VIDEO_ONLY   = "video only"
    AUDIO_ONLY   = "audio only"
    BEST_OF_BOTH = "best of both"
    CUSTOM       = "custom"
