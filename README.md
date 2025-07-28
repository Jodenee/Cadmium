# Cadmium

Cadmium is a python command line application made to download youtube videos conveniently without the risk of malware.

## Dependencies

### Python (Required)
Since Cadmium is written in python you will require a python interpreter on your machine. 

* [Download Page](https://www.python.org/downloads/)

### FFmpeg (Required)
Required to convert files to mp4 and mp3 as well as merge files.

* [Download Page](https://ffmpeg.org/download.html) 
* [Download Guide (Windows)](https://www.youtube.com/watch?v=IECI72XEox0&ab_channel=TroubleChute)
* [Download Guide (Linux)](https://www.youtube.com/watch?v=gyf-AekgQL0)

### Node.js (Optional)
Occasionally, YouTube may identify Cadmium as a bot. To reduce the likelihood of detection, the program can use Node.js to automatically generate PO tokens. While this can help you remain undetected, it is not guarantee.

* [Download Page](https://nodejs.org/) 

## Download Instructions

1. Download the latest release of Cadmium from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it.
2. Open Command Prompt and cd into the extracted folder.
3. Run `python -m pip install -r requirements.txt` to install all required python libraries 
4. Lastly run the program using the following command `python path_to_main_here/main.py`
