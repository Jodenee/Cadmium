
import logging

from pathlib import Path

from ..utilities.constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class TemporaryFileStorage:
    def __init__(self) -> None:
        self._temporary_files: list[Path] = []


    def register_temporary_file(self, *files: Path) -> None:
        for file in files:
            logger.debug(
                "registered temporary file path=%s", 
                file
            )
            self._temporary_files.append(file)


    def remove_temporary_files(self) -> None:
        logger.info("removing temporary files")

        for temporary_file in self._temporary_files:
            logger.debug(
                "removing temporary file path=%s", 
                temporary_file
            )

            temporary_file.unlink()

        self._temporary_files.clear()

        logger.info("temporary files successfully removed")
