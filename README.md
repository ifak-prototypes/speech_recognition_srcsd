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

## Advanced setup options

You may modify the `run.bat` or respectively the `run.sh` file when you want to modify the program behavior.
For example when you are on a Linux machine and you definitely don't want to use the GPU, then you
could modify the python program call in `run.sh` file to

```
    python src/srcsd/tkclient.py --device=cpu
```

There are following options:

| Setting | Explanation |
|---------|-------------|
| device | one of [`cpu`, `gpu`]: defines, on which computing resource is computed. Otherwise a GPU is |
| local | one of [`true`, `false`]: defines, whether the client uses local audio data processing or not. In latter case a remote GPU server can be used for processing. This will only work if the server is already running.
| host | string representing the hostname to be used for requests, default is `localhost` |
| port | port to use for requests to the host, default is `8000` |


## Start the server

The server is only used, if you start the app with with `local` set to `false`. (see "Advanced setup options")

### Microsoft Windows

Use the following command in a terminal window (cmd):

```
    .\run_server.bat
```

### Linux

Run the following command in a shell:

```
    bash ./run_server.sh
```

## Advanced setup options

You may modify the `run_server.bat` or respectively the `run_server.sh` file when you want to modify the program behavior.
For example when you are on a Linux machine and you want to host the server on port `4000`, you can modify the python program call in `run_server`.sh:

```
    python src/srcsd/server.py --port=4000
```

There are following options:

| Setting | Explanation |
|---------|-------------|
| port | port to listen for requests on, default is `8000`  |


## Usage

The program contains the following setting options:

| Setting  | Usage |
|----------|-------|
| Model | This is a selection of the OpenAI Whisper model. Smaller models are faster but also more imprecise.|
| Language | The original language |
| Task | `transcribe` means, that the text is created in the original language; `translate` means, that the text is translated to English. |
| Format   | `normal` takes the text from the Whisper model as is, while `stripped` means, that leading and trailling whitespaces are omitted. Stripped text is preffered, when working with spread-sheets or presentation programs, while `normal` is including white spaces - so it is preffered for floating text. |
| Pause | The processing of speech starts after a little break. (e.g. pause between 2 sentences) This parameter determines the duration length of this break. |
| Active | Determines whether audio data should be processed or not. |
| Insert via CTR-V | Defines whether the system automatically puts the recognized text into the system clipboard and the CTRL-V key combination is automatically pressed. |

The text input field contains the recognized text.


## Data privacy

### Local data processing

The program stores recorded audio files on the computer into the directory 'audio_data'.
Processed audio data files will be deleted directly after converting them into text.
If the program is killed, there could be residual files in the `audio_data` directory.
They can be safely deleted manually or they are deleted at the next program start.


## Known Issues/Restrictions

* sometimes random outputs when recording (background noise)

### Client/Server based audio data processing

The client stores recorded audio files into the directory `audio_data` and the server stores received audio files into the directory `.uploads`.
Audio data files will be deleted, after they have been transferred/used.
If the program is killed, there could be residual files in those directories.
They can be safely deleted manually or they are deleted at the next program start.


## Copyright and License Information

Copyright (c) 2023, Institut für Automation und Kommunikation e.V. (ifak e.V.) and Keanu-Farell Kunzi.
See the [LICENSE](./LICENSE) file for licensing conditions (MIT license).