from typing import Type

class ConfigurationFileCorruptError(Exception):
    def __init__(self) -> None:
        super().__init__("Configuration file could not be loaded, try deleting the configuration file and re-running the program.")