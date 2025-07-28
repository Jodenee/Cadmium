class InvalidYoutubeURLError(Exception):
    def __init__(self, given_url: str) -> None:
        super().__init__(f"URL: ({given_url}) is not a valid youtube url.")