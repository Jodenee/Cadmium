import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    try: 
        from strenum import StrEnum 
    except ImportError as e: 
        print("required package strenum not found, please ensure all the required packages have been installed before running Cadmium.")
        exit(1)

class Colours(StrEnum):
    CADMIUM_RED    = "#E30022"  # Is the ground beneath
    CADMIUM_ORANGE = "#ED872D"  # Everything I see
    CADMIUM_YELLOW = "#FFF600"  # Is the air I breath
