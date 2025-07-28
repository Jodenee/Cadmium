class DownloadDirectoryIsAFileError(Exception):
    def __init__(self, given_path: str) -> None:
        super().__init__(f"The download directory ({given_path}) is not a folder!")