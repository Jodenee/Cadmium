class InvalidConfigurationError(BaseException):
    def __init__(self, configuration_name: str, context: str) -> None:
        super().__init__(f"Configuration ({configuration_name}) {context}.")
