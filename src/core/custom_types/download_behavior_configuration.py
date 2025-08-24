from typing import TypedDict

class DownloadBehaviorConfiguration(TypedDict):
    skip_existing_files: bool

    convert_video_downloads: bool
    convert_video_only_downloads: bool
    convert_audio_only_downloads: bool
    merge_best_of_both_downloads_into_one_file: bool

    convert_video_downloads_to: str
    convert_video_only_downloads_to: str
    convert_audio_only_downloads_to: str
    best_of_both_merged_file_format: str
