from typing import ReadOnly, TypedDict

class WarningConfiguration(TypedDict):
    silence_undeleted_temp_file_warning: ReadOnly[bool]
    silence_already_exists_warning: ReadOnly[bool]
