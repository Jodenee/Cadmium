from typing import TypedDict, Optional

class CustomDownloadLocationConfiguration(TypedDict):
    use_custom_video_download_location: bool
    use_custom_audio_download_location: bool
    use_custom_video_only_download_location: bool
    use_custom_best_of_both_download_location: bool
    custom_video_download_location: Optional[str]
    custom_audio_download_location: Optional[str]
    custom_video_only_download_location: Optional[str]
    custom_best_of_both_download_location: Optional[str]
