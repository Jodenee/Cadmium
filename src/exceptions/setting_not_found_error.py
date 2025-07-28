class SettingNotFoundError(BaseException):
    def __init__(self, setting_name: str) -> None:
        super().__init__(f"Setting ({setting_name}) was not found.")