# DIY Cadmium

## Required Dependencies

### Python
Cadmium is written in python, so you will need to have a python interpreter on your machine. While it is recommended to install a modern python interpreter, Cadmium is at least backwards compatible with `3.12`. 

* [Download Page](https://www.python.org/downloads/)
* [Download Guide (Windows 10/11)](https://www.youtube.com/watch?v=3JHlILId9-k)
* [Download Guide (Linux)](https://www.youtube.com/watch?v=3JHlILId9-k)

## Running Raw Cadmium Source Code

1. Download the latest version of the Cadmium source code from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it.
2. Spawn a shell and cd into `Cadmium`.
3. Run the below command to install the required packages.
    * `python -m pip install -r src/requirements.txt` 
4. All done! You may now run the `main.py` script with the following command 
    * `python src/main.py`. Happy downloading! 

## Building Cadmium From Source Code

1. Download the latest version of the Cadmium source code from [*here*](https://github.com/Jodenee/Cadmium/releases) and extract it.
2. Spawn a shell and cd into `Cadmium`.
3. Run the below command to install the required packages.
    * `python -m pip install -r src/requirements.txt` 
4. Open `src/core/bin/ffmpeg` and ensure an appropriate version exists for your system and keep it in mind for the next step. If there isn't you must either source a trusted binary for your specific system OR use cadmium without it's conversion features.
5. Run the following to start the build process, please replace all `{system_ffmpeg}` placeholders with the name of the folder containing the correct ffmpeg version for your system found in the previous step, if you did not find an ffmpeg binary in the previous step omit the `--add-data` argument.
    * Windows -> ```pyinstaller --onedir --clean --name Cadmium --add-data "src\core\bin\ffmpeg\{system_ffmpeg};core\bin\ffmpeg\{system_ffmpeg}" src\main.py```
    * Other -> ```pyinstaller --onedir --clean --name Cadmium --add-data "src/core/bin/ffmpeg/{system_ffmpeg}:core/bin/ffmpeg/{system_ffmpeg}" src/main.py```
6. Copy the licence file to the built folder
    * Windows -> `copy LICENCE.txt "dist/Cadmium/LICENCE.txt"`
    * Other -> `cp LICENCE.txt "dist/Cadmium/LICENCE.txt"`
7. Run the following command to initialise the required files.
    * Windows -> `.\dist\Cadmium\Cadmium.exe --initialise_only`
    * Other -> `./dist/Cadmium/Cadmium --initialise_only`
8. If in step 4 you could not find a ffmpeg binary for your system but have managed to source one do the following steps to make Cadmium use it.
    * open the `configurations.json` file.
    * set `use_packaged_ffmpeg` to false.
    * set `custom_ffmpeg_executable_path` as the path to your ffmpeg binary.
9. All done! Happy downloading! 

## Q&A

### I don't understand this tutorial... / What did I just read?!
This tutorial is mainly targeted towards advanced users that understand the proper technical jargon and are equipped with the proper know how to carry out the given steps. If you still wish to build Cadmium yourself you have the following options.

* Asking a technical individual you know to help.
* Give this file to a LLM to get a more simplified version. 
    * > Just please be aware of your **environmental impact** and risk of hallucination when choosing this option.

### Why build it myself?
* Downloading executable files off the internet is not safe. 
    * Building the executable yourself is much safer as you guarantee the code inside the executable was not modified with malicious intent.
* No prebuilt executables for your specific system.
    * If you are using an operating system or CPU architecture that is not in the [supported platforms matrix](../README.md#supported-platforms-matrix) then Cadmium may not function as intended, the only way to get around this is to build Cadmium yourself.

### Is there any difference between building an executable or running the raw source code with the python interpreter?
If storage is low it is recommended to run the raw source code with the python interpreter. If not building the executable will be more convenient as there wont be a need to open a shell and run the program each time you wish to use Cadmium. 
