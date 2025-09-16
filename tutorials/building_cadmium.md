# Building Cadmium From Source Code / Running Cadmium Source Code

## Q&A

### Why build it myself?
* Downloading executable files off the internet is not safe. 
    * Building the executable yourself is much safer as you guarantee the code inside the executable is not malicious.
* No prebuilt executables for your OS.
    * Cadmium is currently only prebuilt for Windows 10/11 64-bit and Linux 64-bit, if you are using another operating system or CPU architecture Cadmium may not function, the only way to get around this is to build Cadmium yourself.

### Is there any difference between building an executable or running the raw source code with the python interpreter?
If storage is low it is recommended to run the raw source code with the python interpreter. If not building the executable will be more convenient as there wont be a need to open a shell and run the program each time you wish to use Cadmium. 

### I don't understand this tutorial...
This tutorial is mainly targeted towards technical individuals that understand technical jargon. If you still wish to build Cadmium yourself you have the following options.

* Asking a technical individual you know to help.
* Consult this [ChatGPT chat](https://chatgpt.com/share/68bed80b-1958-8012-9c44-32852a2565f2) or give this file to a LLM to get a more simplified version. Just please be aware of your **environmental impact** when choosing this option.

## Required Dependencies

### Python
Cadmium is written in python, so you will need to have a python interpreter on your machine. While it is recommended to install a modern python interpreter, Cadmium is at least backwards compatible with `3.10.12`. 

* [Download Page](https://www.python.org/downloads/)
* [Download Guide (Windows 10/11)](https://www.youtube.com/watch?v=3JHlILId9-k)
* [Download Guide (Linux)](https://www.youtube.com/watch?v=3JHlILId9-k)

## Steps

1. Download the latest version of the Cadmium source code from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it.
2. Spawn a shell and cd into the extracted folder.
3. Run the below command to install the required packages.
    * `python -m pip install -r src/requirements.txt` 
4. Run the below command to build Cadmium into an executable.
    * `pyinstaller --onedir --name Cadmium src/main.py`.
5. Done! You may now run the Cadmium executable found inside `Cadmium/dist/Cadmium` or run main.py with `python src/main.py`, the following steps are optional but are worth following for the full experience.
6. Download and install FFmpeg using the following resources.
    * Required to convert files as well as merge files.
    * [Download Page](https://ffmpeg.org/download.html) 
    * [Download Guide (Windows 10)](https://www.youtube.com/watch?v=IECI72XEox0&ab_channel=TroubleChute)
    * [Download Guide (Windows 11)](https://www.youtube.com/watch?v=jZLqNocSQDM)
    * For linux run the following command `sudo apt update && sudo apt install ffmpeg`, please note that this command will not work for all distributions of linux so please research if ffmpeg is available through your distribution's package manager. 
7. Download and install Node.js using the following resources.
    * Helps Cadmium stay hidden from youtube's bot counter measures. While not 100% effective, it can help you get denied less frequently.
    * [Download Page](https://nodejs.org/) 
    * [Download Guide (Windows 10/11)](https://www.youtube.com/watch?v=LwM1dtTcSss)
    * For linux run the following command `sudo apt update && sudo apt install nodejs && sudo apt install npm`, please note that this command will not work for all distributions of linux so please research if nodejs and npm are available through your distribution's package manager. 
