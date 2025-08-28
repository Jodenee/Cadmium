from typing import TypedDict

from .download_location_overrides_configuration import DownloadLocationOverridesConfiguration

class QualityOfLifeConfiguration(TypedDict):
    download_location_overrides: DownloadLocationOverridesConfiguration
    put_playlist_videos_in_folder: bool
    display_chosen_stream_on_start_of_download: bool
    clear_temporary_files_before_exiting: bool
