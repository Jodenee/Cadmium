from typing import TypedDict

from .custom_download_location_configuration import CustomDownloadLocationConfiguration

class QualityOfLifeConfiguration(TypedDict):
    custom_download_locations: CustomDownloadLocationConfiguration
    put_playlist_videos_in_folder: bool
    display_chosen_stream_on_start_of_download: bool
    clear_temporary_files_before_exiting: bool
