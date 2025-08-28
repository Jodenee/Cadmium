from typing import TypedDict, Optional

class DownloadLocationOverridesConfiguration(TypedDict):
    use_video_download_location_override: bool
    use_audio_download_location_override: bool
    use_video_only_download_location_override: bool
    use_best_of_both_download_location_override: bool
    use_custom_download_location_override: bool
    video_download_location_override: Optional[str]
    audio_download_location_override: Optional[str]
    video_only_download_location_override: Optional[str]
    best_of_both_download_location_override: Optional[str]
    custom_download_location_override: Optional[str]
