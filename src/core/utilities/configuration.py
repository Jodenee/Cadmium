from pathlib import Path
from typing import Optional
from json import load as json_load, dumps as json_dumps

from ..custom_types import Configuration
from .constants import DEFAULT_CONFIGURATION

# Functions

def create_configuration_file(path: Path, configuration: Optional[Configuration] = DEFAULT_CONFIGURATION) -> None:
    """Create a configuration file.

    Args:
        path: The exact file path where the file will be created,
            including the filename.

        configuration: The contents to write into the file.
    """

    file_content: str = json_dumps(configuration, indent=4)

    with path.open("a") as file:
        file.write(file_content)


def load_configuration(configuration_file_path: Path) -> Configuration:
    """Loads and parses the contents of a configuration file.

    Attempts to load the configurations within the provided file path, 
    if any exception is raised while parsing or if `configuration_file_path` 
    does not lead to a file `DEFAULT_CONFIGURATION` is returned.

    Args:
        configuration_file_path: A `Path` leading to the configuration file.

    Returns:
        The parsed configuration.
    """

    if not configuration_file_path.is_file():
        return DEFAULT_CONFIGURATION

    try:
        with configuration_file_path.open("r") as config_file:
            json_data: Configuration = json_load(config_file)

        return json_data
    except BaseException:
        return DEFAULT_CONFIGURATION
