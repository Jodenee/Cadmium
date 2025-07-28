from typing import ReadOnly, TypedDict

from custom_types import CustomDownloadLocationConfiguration

class QualityOfLifeConfiguration(TypedDict):
    custom_download_locations: ReadOnly[CustomDownloadLocationConfiguration]
    put_playlist_videos_in_folder: ReadOnly[bool]
    convert_video_only_downloads_to_mp4: ReadOnly[bool]
    convert_audio_only_downloads_to_mp3: ReadOnly[bool]
    combine_best_of_both_downloads_into_one_file: ReadOnly[bool]
    display_chosen_stream_on_start_of_download: ReadOnly[bool]
