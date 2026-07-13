
import logging

from pathlib import Path

from ..utilities.constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class TemporaryFileStorage:
    """A class that manages the registration and removal of temporary files."""

    def __init__(self) -> None:
        self._temporary_files: list[Path] = []


    def register_temporary_file(self, *files: Path) -> None:
        """Registers the given path(s) as temporary files that'll be removed when using the `remove_temporary_files` method.

        Args:
            *files: One or more `Path` instances leading to a file.
        """
        for file in files:
            logger.debug(
                "registered temporary file path=%s", 
                file
            )
            self._temporary_files.append(file)


    def remove_temporary_files(self) -> None:
        """Removes all temporary files registered using the `register_temporary_file` method."""

        logger.info("removing temporary files")

        for temporary_file in self._temporary_files:
            logger.debug(
                "removing temporary file path=%s", 
                temporary_file
            )

            temporary_file.unlink()

        self._temporary_files.clear()

        logger.info("temporary files successfully removed")


    @property
    def has_files(self) -> bool:
        return any(self._temporary_files)
