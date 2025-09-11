# Configuration
This tutorial will explain the purpose of each configuration.

## Introduction

All Cadmium's configurations are stored inside `configuration.json` found inside the same folder as Cadmium.

When opening `configuration.json` for the first time you will be met with the following.

```json
{
    "download_behavior_configuration": {
        "skip_existing_files": true,
        "convert_video_downloads": false,
        "convert_video_only_downloads": false,
        "convert_audio_only_downloads": false,
        "merge_best_of_both_downloads_into_one_file": false,
        "convert_custom_downloads": false,
        "convert_video_downloads_to": "mp4",
        "convert_video_only_downloads_to": "mp4",
        "convert_audio_only_downloads_to": "mp3",
        "best_of_both_merged_file_format": "mp4",
        "convert_custom_downloads_to": "mp4"
    },
    "quality_of_life_configuration": {
        "download_location_overrides": {
            "use_video_download_location_override": false,
            "use_video_only_download_location_override": false,
            "use_audio_only_download_location_override": false,
            "use_best_of_both_download_location_override": false,
            "use_custom_download_location_override": false,
            "video_download_location_override": "",
            "video_only_download_location_override": "",
            "audio_only_download_location_override": "",
            "best_of_both_download_location_override": "",
            "custom_download_location_override": ""
        },
        "put_playlist_videos_in_folder": true,
        "put_channel_videos_in_folder": true,
        "put_custom_streams_in_folder": true,
        "display_chosen_stream_on_start_of_download": true,
        "clear_temporary_files_before_exiting": false
    },
    "warning_configuration": {
        "silence_existing_temporary_files_warning": false
    },
    "ui_configuration": {
        "custom_download_bar_colour": "",
        "custom_convert_bar_colour": "",
        "custom_clear_directory_bar_colour": ""
    },
    "external_dependency_configuration": {
        "FFmpeg": {
            "try_find_ffmpeg_path_automatically": true,
            "ffmpeg_executable_path": ""
        }
    }
}
```

## Editing `configuration.json`
A short guide for editing Cadmium's configurations. 

## Important
* In the case of a mistake while editing the `configuration.json` file, the `configuration.json` file may be safely deleted, and a new one will be created automatically by Cadmium when run containing the default configurations.

## Booleans
* `true` and `false` can be thought of as `on` and `off` respectfully, so when you wish to enable a configuration you use `true` and to disable a configuration you use `false`.

## Strings
* "" and "mp4" is how text is stored, so `""` is simply a string containing no text and `"mp4"` simply stores the text `mp4`. 

* It is **VERY IMPORTANT** to note that when pasting a file path on Windows such as `C:\my_folder\downloads` you will need to replace the backslashes `\` with a double backslash `\\`, the result should look similar to this `C:\\my_folder\\downloads`, the reason for this need is quite complex and wont be explained here but for those who are curious here is a [source](https://stackoverflow.com/a/59391584).

## Configuration Guide

### Navigation Links
* [Download Behavior Configuration](#download-behavior-configuration)
* [Quality Of Life Configuration](#quality-of-life-configuration)
* [Warning Configuration](#warning-configuration)
* [UI Configuration](#ui-configuration)
* [External Dependency Configuration](#external-dependency-configuration)

### Download Behavior Configuration

| Setting                                      | Default | Description                                                                                                              | Required Dependencies |
|----------------------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `skip_existing_files`                        | `true`  | Cadmium won’t re-download a video that already exists in the target folder.                                              | `None`                |
| `convert_video_downloads`                    | `false` | Whether to convert "video" downloads automatically.                                                                      | `FFmpeg`              |
| `convert_video_only_downloads`               | `false` | Whether to convert "video only" downloads automatically.                                                                 | `FFmpeg`              |
| `convert_audio_only_downloads`               | `false` | Whether to convert "audio only" downloads automatically.                                                                 | `FFmpeg`              |
| `merge_best_of_both_downloads_into_one_file` | `false` | Whether to merge "best of both" downloads into one file resulting in a video with the best possible video and audio.     | `FFmpeg`              |
| `convert_custom_downloads`                   | `false` | Whether to convert "custom" downloads automatically.                                                                     | `FFmpeg`              |
| `convert_video_downloads_to`                 | `"mp4"` | If `convert_video_downloads` is enabled, "video" downloads will be converted to the specified file format.               | `FFmpeg`              |
| `convert_video_only_downloads_to`            | `"mp4"` | If `convert_video_only_downloads` is enabled, "video only" downloads will be converted to the specified file format.     | `FFmpeg`              |
| `convert_audio_only_downloads_to`            | `"mp3"` | If `convert_audio_only_downloads` is enabled, "audio only" downloads will be converted to the specified file format.     | `FFmpeg`              |
| `best_of_both_merged_file_format`            | `"mp4"` | If `merge_best_of_both_downloads_into_one_file` is enabled, merged files will be created with the specified file format. | `FFmpeg`              |
| `convert_custom_downloads_to`                | `"mp4"` | If `convert_custom_downloads` is enabled, "custom" downloads will be converted to the specified file format.             | `FFmpeg`              |

### Quality Of Life Configuration

| Setting                                       | Default | Description                                                                                                                           | Required Dependencies |
|-----------------------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `use_video_download_location_override`        | `false` | Whether to put "video" downloads inside the folder specified in `video_download_location_override`.                                   | `None`                |
| `use_video_only_download_location_override`   | `false` | Whether to put "video only" downloads inside the folder specified in `video_only_download_location_override`.                         | `None`                |
| `use_audio_only_download_location_override`   | `false` | Whether to put "video only" downloads inside the folder specified in `audio_only_download_location_override`.                         | `None`                |
| `use_best_of_both_download_location_override` | `false` | Whether to put "best of both" downloads inside the folder specified in `best_of_both_download_location_override`.                     | `None`                |
| `use_custom_download_location_override`       | `false` | Whether to put "custom" downloads inside the folder specified in `custom_download_location_override`.                                 | `None`                |
| `video_download_location_override`            | `""`    | If `use_video_download_location_override` is enabled, "video" downloads will be put inside the specified folder here.                 | `None`                |
| `video_only_download_location_override`       | `""`    | If `use_video_only_download_location_override` is enabled, "video only" downloads will be put inside the specified folder here.       | `None`                |
| `audio_only_download_location_override`       | `""`    | If `use_audio_only_download_location_override` is enabled, "audio only" downloads will be put inside the specified folder here.       | `None`                |
| `best_of_both_download_location_override`     | `""`    | If `use_best_of_both_download_location_override` is enabled, "best of both" downloads will be put inside the specified folder here.   | `None`                |
| `custom_download_location_override`           | `""`    | If `use_custom_download_location_override` is enabled, "custom" downloads will be put inside the specified folder here.               | `None`                |
| `put_playlist_videos_in_folder`               | `true`  | If enabled, when downloading playlists a folder will be made to contain the playlist's videos.                                        | `None`                |
| `put_channel_videos_in_folder`                | `true`  | If enabled, when downloading channels a folder will be made to contain the channel's videos.                                          | `None`                |
| `put_custom_streams_in_folder`                | `true`  | If enabled, when downloading custom streams a folder will be made to contain the video's streams.                                     | `None`                |
| `display_chosen_stream_on_start_of_download`  | `true`  | If enabled, a message will be displayed showcasing information about the stream chosen such as file type, resolution fps and bitrate. | `None`                |
| `clear_temporary_files_before_exiting`        | `false` | If enabled, when choosing "exit program" in the main menu all temporary files will be safely removed.                                 | `None`                |

### Warning Configuration

| Setting                                      | Default | Description                                                                                                                                                                     | Required Dependencies |
|----------------------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `silence_existing_temporary_files_warning`   | `false` | Whether to display a warning at the start of the download process if temporary files exist. Enable `clear_temporary_files_before_exiting` for automatic removal of these files. | `None`                |

### UI Configuration

| Setting                             | Default | Description                                                                                                                                                  | Required Dependencies |
|-------------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `custom_download_bar_colour`        | `""`    | Used to change the colour of the download progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names.         | `None`                | 
| `custom_convert_bar_colour`         | `""`    | Used to change the colour of the video conversion progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names. | `None`                |
| `custom_clear_directory_bar_colour` | `""`    | Used to change the colour of the folder clear progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names.     | `None`                |

### External Dependency Configuration

| Setting                              | Default | Description                                                                                                                                         | Required Dependencies |
|--------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `try_find_ffmpeg_path_automatically` | `true`  | If enabled, Cadmium will attempt to locate an ffmpeg executable automatically. Does not search if `ffmpeg_executable_path` is given. (Checks $PATH) | `None`                |
| `ffmpeg_executable_path`             | `""`    | An absolute path leading to an FFmpeg executable, Cadmium will prefer `ffmpeg_executable_path` if `try_find_ffmpeg_path_automatically` is enabled.  | `None`                |

If you are still not sure how a particular configuration works feel free to create an issue and await an answer.