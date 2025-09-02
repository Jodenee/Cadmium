class InvalidYoutubeURLError(Exception):
    def __init__(self, given_url: str) -> None:
        super().__init__(f"({given_url}) is not a valid youtube url.")
