class InvalidSettingError(BaseException):
    def __init__(self, setting_name: str, context: str) -> None:
        super().__init__(f"Setting ({setting_name}) {context}.")