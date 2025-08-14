from typing import TypedDict

from .quality_of_life_configuration import QualityOfLifeConfiguration
from .warning_configuration import WarningConfiguration
from .download_behavior_configuration import DownloadBehaviorConfiguration

class Configuration(TypedDict):
    download_behavior_configuration: DownloadBehaviorConfiguration
    quality_of_life_configuration: QualityOfLifeConfiguration
    warning_configuration: WarningConfiguration
