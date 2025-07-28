from typing import Type

class SettingCorruptError(Exception):
    def __init__(self, setting_name: str, expected_type: Type, type_returned: Type) -> None:
        super().__init__(f"Setting ({setting_name}) did not return the expected type ({expected_type}) but instead returned ({type_returned}).")