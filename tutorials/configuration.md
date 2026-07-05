# Configuration
This tutorial will explain the purpose of each configuration as well as how to manipulate the configuration file.

## Introduction

All of Cadmium's configurations are stored inside the `configuration.json` file found inside the same folder as Cadmium. For the remainder of this tutorial it shall be referred as the configurations file.

When opening the configurations file for the first time you will be met with the following contents, while it may be a bit overwhelming at first it's quite simple to learn and understand with this tutorial aiding you.

Please remember if at any time a mistake is made while editing the configurations file it can be safely deleted, and a fresh one will be created automatically by just running Cadmium.

```json
{
    "download_behavior_configuration": {
        "skip_existing_files": true,
        "automatically_delete_temporary_files_after_download": true,
        "convert_video_downloads": true,
        "convert_video_only_downloads": true,
        "convert_audio_only_downloads": true,
        "merge_best_of_both_downloads_into_one_file": true,
        "convert_custom_downloads": true,
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
        "display_chosen_stream_on_start_of_download": true
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
        "ffmpeg": {
            "use_ffmpeg": true,
            "use_packaged_ffmpeg": true,
            "use_path_ffmpeg": false,
            "custom_ffmpeg_executable_path": ""
        }
    },
    "logging_configuration": {
        "enabled": true
    }
}
```

## Editing `configuration.json`
A short guide for editing Cadmium's configurations. 

### Enabling and disabling a configuration
* `true` and `false` can be thought of as `on` and `off` respectfully, so when you wish to enable a configuration you write `true` and to disable a configuration you instead write `false`.

### Configurations requiring text input
* The way computers understand text is by wrapping the actual words you wish for it to read in double quotation marks so `"words go here"` is how text is stored, so when a computer sees `"mp4"` it reads the text within the double quotation marks and ends up with `mp4`. 

* It is **VERY IMPORTANT** to note that when inputting a file path on Windows such as `C:\my_folder\downloads` you will need to replace the backslashes `\` with a double backslash `\\`, the result should look similar to this `C:\\my_folder\\downloads`, the reason for this need is quite complex and wont be explained here but for those who are curious here is a [source](https://stackoverflow.com/a/59391584).

## Configuration Guide
A comprehensive guide detailing each configuration in detail.

### Navigation
* [Download Behavior Configuration](#download-behavior-configuration)
* [Quality Of Life Configuration](#quality-of-life-configuration)
* [Warning Configuration](#warning-configuration)
* [UI Configuration](#ui-configuration)
* [External Dependency Configuration](#external-dependency-configuration)
* [Logging Configuration](#logging-configuration)

### Download Behavior Configuration

| Setting                                               | Default | Description                                                                                                                 |
|-------------------------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------|
| `skip_existing_files`                                 | `true`  | Cadmium will not re-download a video that already exists in the target folder.                                              |
| `automatically_delete_temporary_files_after_download` | `true`  | If enabled, Cadmium will be allowed to automatically remove temporary files produced by itself and frees up storage.        |
| `convert_video_downloads`                             | `true`  | Whether to convert "video" downloads automatically.                                                                         |
| `convert_video_only_downloads`                        | `true`  | Whether to convert "video only" downloads automatically.                                                                    |
| `convert_audio_only_downloads`                        | `true`  | Whether to convert "audio only" downloads automatically.                                                                    |
| `merge_best_of_both_downloads_into_one_file`          | `true`  | Whether to merge "best of both" downloads into one file resulting in a video with the best possible video and audio.        |
| `convert_custom_downloads`                            | `true`  | Whether to convert "custom" downloads automatically.                                                                        |
| `convert_video_downloads_to`                          | `"mp4"` | If `convert_video_downloads` is enabled, "video" downloads will be converted to the specified file format.                  |
| `convert_video_only_downloads_to`                     | `"mp4"` | If `convert_video_only_downloads` is enabled, "video only" downloads will be converted to the specified file format.        |
| `convert_audio_only_downloads_to`                     | `"mp3"` | If `convert_audio_only_downloads` is enabled, "audio only" downloads will be converted to the specified file format.        |
| `best_of_both_merged_file_format`                     | `"mp4"` | If `merge_best_of_both_downloads_into_one_file` is enabled, merged files will be created with the specified file format.    |
| `convert_custom_downloads_to`                         | `"mp4"` | If `convert_custom_downloads` is enabled, "custom" downloads will be converted to the specified file format.                |

### Quality Of Life Configuration

| Setting                                       | Default | Description                                                                                                                           |
|-----------------------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------|
| `use_video_download_location_override`        | `false` | Whether to put "video" downloads inside the folder specified in `video_download_location_override`.                                   |
| `use_video_only_download_location_override`   | `false` | Whether to put "video only" downloads inside the folder specified in `video_only_download_location_override`.                         |
| `use_audio_only_download_location_override`   | `false` | Whether to put "video only" downloads inside the folder specified in `audio_only_download_location_override`.                         |
| `use_best_of_both_download_location_override` | `false` | Whether to put "best of both" downloads inside the folder specified in `best_of_both_download_location_override`.                     |
| `use_custom_download_location_override`       | `false` | Whether to put "custom" downloads inside the folder specified in `custom_download_location_override`.                                 |
| `video_download_location_override`            | `""`    | If `use_video_download_location_override` is enabled, "video" downloads will be put inside the path specified here..                  |
| `video_only_download_location_override`       | `""`    | If `use_video_only_download_location_override` is enabled, "video only" downloads will be put inside the path specified here..        |
| `audio_only_download_location_override`       | `""`    | If `use_audio_only_download_location_override` is enabled, "audio only" downloads will be put inside the path specified here..        |
| `best_of_both_download_location_override`     | `""`    | If `use_best_of_both_download_location_override` is enabled, "best of both" downloads will be put inside the path specified here.     |
| `custom_download_location_override`           | `""`    | If `use_custom_download_location_override` is enabled, "custom" downloads will be put inside the path specified here.                 |
| `put_playlist_videos_in_folder`               | `true`  | If enabled, when downloading playlists a folder will be made to contain the playlist's videos.                                        |
| `put_channel_videos_in_folder`                | `true`  | If enabled, when downloading channels a folder will be made to contain the channel's videos.                                          |
| `put_custom_streams_in_folder`                | `true`  | If enabled, when downloading custom streams a folder will be made to contain the video's streams.                                     |
| `display_chosen_stream_on_start_of_download`  | `true`  | If enabled, a message will be displayed showcasing information about the stream chosen such as file type, resolution fps and bitrate. |

### Warning Configuration

| Setting                                      | Default | Description                                                                                                                                                                 |
|----------------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `silence_existing_temporary_files_warning`   | `false` |  If enabled, Cadmium will not display warnings if temporary files exist. Enable `automatically_delete_temporary_files_after_download` for automatic removal of these files. |

### UI Configuration

| Setting                             | Default | Description                                                                                                                                                  |
|-------------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `custom_download_bar_colour`        | `""`    | Used to change the colour of the download progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names.         | 
| `custom_convert_bar_colour`         | `""`    | Used to change the colour of the video conversion progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names. |
| `custom_clear_directory_bar_colour` | `""`    | Used to change the colour of the folder clear progress bar, only accepts [hex colours](https://htmlcolorcodes.com/color-picker/) or common colour names.     |

### External Dependency Configuration

### FFmpeg

| Setting                              | Default | Description                                                                                                  |
|--------------------------------------|---------|--------------------------------------------------------------------------------------------------------------|
| `use_ffmpeg`                         | `true`  | If enabled, Cadmium will be allowed to search for FFmpeg locally to convert files.                           |
| `use_packaged_ffmpeg`                | `true`  | If enabled, Cadmium will be allowed to use the packaged FFmpeg executable files.                             |
| `use_path_ffmpeg`                    | `false` | If enabled, Cadmium will be allowed to search the PATH environment variable for a useable ffmpeg executable. |
| `custom_ffmpeg_executable_path`      | `""`    | An absolute path leading to an FFmpeg executable directly.                                                   |

### Logging Configuration

| Setting   | Default | Description                                                                                                                                         |
|-----------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `enabled` | `true`  | If enabled, Cadmium will log debugging information locally on your computer in case a bug occurs you will need to submit these logs with the issue. |

If you are still not sure how a particular configuration works feel free to [ask here!](https://github.com/Jodenee/Cadmium/discussions/new?category=q-a)