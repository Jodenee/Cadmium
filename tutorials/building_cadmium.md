# Building Cadmium From Source Code / Running Cadmium Source Code

## Q&A

### Why build it myself?
* Downloading executable files off the internet is not safe. 
    * Building the executable yourself is much safer as you guarantee the code inside the executable is not malicious.
* No prebuilt executables for your specific system.
    * Cadmium is currently only prebuilt for Windows 10/11 64-bit and Linux 64-bit, if you are using another operating system or CPU architecture Cadmium may not function, the only way to get around this is to build Cadmium yourself.

### Is there any difference between building an executable or running the raw source code with the python interpreter?
If storage is low it is recommended to run the raw source code with the python interpreter. If not building the executable will be more convenient as there wont be a need to open a shell and run the program each time you wish to use Cadmium. 

### I don't understand this tutorial...
This tutorial is mainly targeted towards technical individuals that understand technical jargon. If you still wish to build Cadmium yourself you have the following options.

* Asking a technical individual you know to help.
* Consult this [ChatGPT chat](https://chatgpt.com/share/68bed80b-1958-8012-9c44-32852a2565f2) or give this file to a LLM to get a more simplified version. Just please be aware of your **environmental impact** when choosing this option.

## Required Dependencies

### Python
Cadmium is written in python, so you will need to have a python interpreter on your machine. While it is recommended to install a modern python interpreter, Cadmium is at least backwards compatible with `3.12`. 

* [Download Page](https://www.python.org/downloads/)
* [Download Guide (Windows 10/11)](https://www.youtube.com/watch?v=3JHlILId9-k)
* [Download Guide (Linux)](https://www.youtube.com/watch?v=3JHlILId9-k)

## Steps

1. Download the latest version of the Cadmium source code from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it.
2. Spawn a shell and cd into the extracted folder.
3. Run the below command to install the required packages.
    * `python -m pip install -r src/requirements.txt` 
4. Open `src/core/bin/ffmpeg` and ensure an appropriate version exists for your system and keep it in mind for the next step.
5. Replace all `{system_ffmpeg}` placeholders with the name of the folder found in the previous step and run the below command to build Cadmium into an executable.
    * `pyinstaller --onedir --clean --name Cadmium --add-data "src\core\bin\ffmpeg\{system_ffmpeg}:core\bin\ffmpeg\{system_ffmpeg}" src/main.py`.
6. Done! You may now run the Cadmium executable found inside `Cadmium/dist/Cadmium` or run `main.py` with `python src/main.py`
