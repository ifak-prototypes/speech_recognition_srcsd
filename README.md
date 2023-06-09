# Speech Recognition Client/Server and Desktop Application

The software being developed in this project uses OpenAI Whisper technology to input text via speech and use the resulting text in any other application.

Natural language processing often requires a lot of resources. It makes sense to use a graphics card, which greatly speeds up the processing of recorded speech files. Therefore, the processing of speech with this software should be realizable in two ways:

- Local processing: the speech is recorded on the local computer, processed and transferred to local applications.
- Decentralized processing: The speech is recorded locally and processed into a character string on a remote computer (GPU server) and transferred back to the source computer as a character string. There, the text is then transferred to local applications.



## Installation

### Microsoft Windows

The following command must be executed in a terminal window (cmd):

```
    .\bin\prepare.bat
```

### Linux

Run the following command in a shell:

```
    bash ./bin/prepare.sh
```


## Start the application

### Microsoft Windows

Use the following command in a terminal window (cmd):

```
    .\run.bat
```

### Linux

Run the following command in a shell:

```
    bash ./run.sh
```

### Advanced setup options

You may modify the run.bat or respectively the run.sh file when you want to modify the program behavior.
For example when you are on a Linux machine and you definitely don't want to use the GPU, then you
could modify the python program call in run.sh file to

```
    python src/srcsd/tkclient.py --device=cpu
```

There are following options:

- device: one of [cpu, gpu]: defines, on which computing resource is computed. Otherwise a GPU is 
          automatically detected. But when you have a GPU but with not enough memory for your wanted
          model size, then you might use the CPU (which is much slower, but might work). The large
          model needs at least 12GB VRAM in your GPU or by use of CPU in your RAM.
- local: one of [true, false]: defines, whether the client uses local audio data processing or not.
          In later case a remote GPU server can be used.


## Usage

The program contains the following setting options:

- Model: This is a selection of the OpenAI Whisper model. Smaller models are faster but also more imprecise.
- Language: The original language.
- Task: "transcribe" means, that the text is created in the original language. "translate" means, that the text is translated to English.
- Format: "normal" takes the text from the Whisper model as is, while "stripped" means, that leading and trailling whitespaces are omitted. Stripped text is preffered, when working with spread-sheets or presentation programs, while "normal" is including white spaces - so it is preffered for floating text.
- Pause: The processing of speech starts after a little break. This parameter determines the duration length of this break.
- Active: Determines whether audio data should be processed or not.
- Insert via CTRL-V: Defines whether the system automatically puts the recognized text into the system clipboard and the CTRL-V key combination is automatically pressed.

The text input field contains the recognized text.


## Data privacy

### Local data processing

The program stores recorded audio files on the computer into the directory 'audio_data'.
Processed audio data files will be deleted directly after converting them into text.
If the program is killed, there could be residual files in the 'audio_data' directory.
They can be safely deleted manually or they are deleted at the next program start.

### Client/Server based audio data processing

To be done.


## Copyright and License Information

Copyright (c) 2023, Institut für Automation und Kommunikation e.V. (ifak e.V.) and Keanu-Farell Kunzi.
See the LICENSE file for licensing conditions (MIT license).