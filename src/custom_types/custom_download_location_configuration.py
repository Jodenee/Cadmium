from typing import ReadOnly, TypedDict, Optional

class CustomDownloadLocationConfiguration(TypedDict):
    use_custom_video_download_location: ReadOnly[bool]
    use_custom_audio_download_location: ReadOnly[bool]
    use_custom_video_only_download_location: ReadOnly[bool]
    use_custom_best_of_both_download_location: ReadOnly[bool]
    custom_video_download_location: ReadOnly[Optional[str]]
    custom_audio_download_location: ReadOnly[Optional[str]]
    custom_video_only_download_location: ReadOnly[Optional[str]]
    custom_best_of_both_download_location: ReadOnly[Optional[str]]
