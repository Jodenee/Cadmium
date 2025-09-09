# Cadmium
Cadmium is a python command line application made to conveniently download youtube videos without the risk of malware.

## Features

* ✨ **High quality downloads**
    * Cadmium can download 4k (2160p) video.
* 🛡️ **Safe**
    * Cadmium's source code and dependencies are fully open source.
* ✔️ **Simple to use**
    * Cadmium has a very simple user interface.
* 🔄 **Automatic File Conversion**
    * Cadmium can convert your youtube videos to any video or audio formats supported by FFmpeg ex. (mp4, wav, avi, mkv)
* ⚙️ **Customizable**
    * Cadmium has many configurations you can use to make your experience better.

## Supported Platforms

| Operating System | Supported |
|------------------|-----------|
| Windows 10/11    | ✅        |
| Linux            | ✅        |
| macOS            | N/A       |

Cadmium is primarily developed on Windows, but tested on a Linux Mint virtual machine. Cadmium is not tested on macOS due to requiring apple hardware to run macOS.

## Download Instructions (prebuilt executable)
This section will help instruct you through the download process, please note that this is for the prebuilt executable file. If you wish to build or run the source code please follow this  instead. 

1. Download the latest version of Cadmium from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it, please ensure you download the correct version for your os.
2. Open the folder and run Cadmium.exe
3. Done! The following steps are optional but are worth following for the full experience.
4. Download and install FFmpeg using the following resources.
    * Required to convert files as well as merge files.
    * [Download Page](https://ffmpeg.org/download.html) 
    * [Download Guide (Windows 10)](https://www.youtube.com/watch?v=IECI72XEox0&ab_channel=TroubleChute)
    * [Download Guide (Windows 11)](https://www.youtube.com/watch?v=jZLqNocSQDM)
    * For linux run the following command `sudo apt update && sudo apt install ffmpeg`, please note that this command will not work for all distributions of linux so please research if ffmpeg is available for install through your distribution's package manager. 
5. Download and install Node.js using the following resources.
    * Helps Cadmium stay hidden from youtube's bot counter measures. While not 100% effective, it can help you get denied less frequently.
    * [Download Page](https://nodejs.org/) 
    * [Download Guide (Windows 10/11)](https://www.youtube.com/watch?v=LwM1dtTcSss)
    * For linux run the following command `sudo apt update && sudo apt install nodejs && sudo apt install npm`, please note that this command will not work for all distributions of linux so please research if nodejs and npm are available through your distribution's package manager. 

## Download Instructions (Building from source/Running source code)
To learn how to build Cadmium from it's source code please look at this [tutorial](tutorials/building_cadmium.md), it covers building Cadmium from source and running the source code manually with Python.

## Tutorials

* [How to use Cadmium](./tutorials/using_cadmium.md)
* [Understanding the Configuration File](./tutorials/configuration.md)
* [Building Cadmium](./tutorials/building_cadmium.md)

## Acknowledgements
Huge thanks to all the open source libraries and projects that helped make Cadmium possible!

* The maintainers of the [**python**](https://www.python.org/) programming language. [❤️ (Support the project here)](https://www.python.org/psf/donations/)
* The maintainers of the [**ffmpeg**](https://github.com/aisk/pick) project. [❤️ (Support the project here)](https://ffmpeg.org/donations.html)
* The maintainers of the [**node**](https://github.com/nodejs/node) project. [❤️ (Support the project here)](https://github.com/sponsors/nodejs)
* The maintainers of the [**pytubefix**](https://github.com/JuanBindez/pytubefix) python package. [❤️ (Support the project here)](https://github.com/sponsors/JuanBindez)
* The maintainers of the [**python-ffmpeg**](https://github.com/jonghwanhyeon/python-ffmpeg) python package. [❤️ (Support the project here)](https://github.com/jonghwanhyeon/python-ffmpeg)
* The maintainers of the [**tqdm**](https://github.com/tqdm/tqdm) python package. [❤️ (Support the project here)](https://github.com/sponsors/tqdm)
* The maintainers of the [**pick**](https://github.com/aisk/pick) python package. [❤️ (Support the project here)](https://github.com/aisk/pick)
* The maintainers of the [**pyinstaller**](https://github.com/pyinstaller/pyinstaller) python package. [❤️ (Support the project here)](https://github.com/sponsors/Legorooj)
* Name inspired by the wonderful song [Cadmium Colors](https://www.youtube.com/watch?v=1U6qefKcOrg). [❤️ (Support the artist here)](https://jamiepaige.bandcamp.com/jamies-page)
