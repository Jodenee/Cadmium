class PathDoesNotExistError(Exception):
    def __init__(self, missing_file_path: str) -> None:
        super().__init__(f"A required file/directory was not found! Missing path: ({missing_file_path}).")