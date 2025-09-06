import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    try: 
        from strenum import StrEnum 
    except ImportError as e: 
        print("required package strenum not found, please ensure all the required packages have been installed before running Cadmium.")
        exit(1)

class MainMenuOption(StrEnum):
    DOWNLOAD_VIDEOS    = "download videos"
    EDIT_CONFIGURATION = "edit configuration"
    EXIT_PROGRAM       = "exit program"