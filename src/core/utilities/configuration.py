from pathlib import Path
from typing import Optional
from json import load as json_load, dumps as json_dumps

from ..custom_types import Configuration
from .constants import DEFAULT_CONFIGURATION

# Functions

def create_configuration_file(path: Path, configuration: Optional[Configuration] = DEFAULT_CONFIGURATION) -> None:
    file_content: str = json_dumps(configuration, indent=4)

    with path.open("a") as file:
        file.write(file_content)


def load_configuration(config_file_path: Path) -> Configuration:
    try:
        with config_file_path.open("r") as config_file:
            json_data: Configuration = json_load(config_file)

        return json_data
    except BaseException:
        return DEFAULT_CONFIGURATION
