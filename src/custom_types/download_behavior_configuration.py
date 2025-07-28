from typing import ReadOnly, TypedDict

class DownloadBehaviorConfiguration(TypedDict):
    skip_existing_files: ReadOnly[bool]
