# -*- coding: utf-8 -*-

"""Graphical User Interface for an OpenAI Whisper speech recognizer.

The program combines a graphical user interface with a voice recorder
and an OpenAI Whisper based transcription / translation engine. All parts
of the program work in a non-blocking manner.
"""

import argparse
import glob
import logging
import io
import pydub
import pyautogui
import pyperclip
import speech_recognition
import os
import os.path
import pykka
import sys
import tkinter
import tkinter.messagebox
import tkinter.ttk
import time
import torch
import whisper

LANGUAGES = [
    "Afrikaans",
    "Albanian",
    "Amharic",
    "Arabic",
    "Armenian",
    "Assamese",
    "Azerbaijani",
    "Bashkir",
    "Basque",
    "Belarusian",
    "Bengali",
    "Bosnian",
    "Breton",
    "Bulgarian",
    "Burmese",
    "Castilian",
    "Catalan",
    "Chinese",
    "Croatian",
    "Czech",
    "Danish",
    "Dutch",
    "English",
    "Estonian",
    "Faroese",
    "Finnish",
    "Flemish",
    "French",
    "Galician",
    "Georgian",
    "German",
    "Greek",
    "Gujarati",
    "Haitian",
    "Haitian Creole",
    "Hausa",
    "Hawaiian",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Indonesian",
    "Italian",
    "Japanese",
    "Javanese",
    "Kannada",
    "Kazakh",
    "Khmer",
    "Korean",
    "Lao",
    "Latin",
    "Latvian",
    "Letzeburgesch",
    "Lingala",
    "Lithuanian",
    "Luxembourgish",
    "Macedonian",
    "Malagasy",
    "Malay",
    "Malayalam",
    "Maltese",
    "Maori",
    "Marathi",
    "Moldavian",
    "Moldovan",
    "Mongolian",
    "Myanmar",
    "Nepali",
    "Norwegian",
    "Nynorsk",
    "Occitan",
    "Panjabi",
    "Pashto",
    "Persian",
    "Polish",
    "Portuguese",
    "Punjabi",
    "Pushto",
    "Romanian",
    "Russian",
    "Sanskrit",
    "Serbian",
    "Shona",
    "Sindhi",
    "Sinhala",
    "Sinhalese",
    "Slovak",
    "Slovenian",
    "Somali",
    "Spanish",
    "Sundanese",
    "Swahili",
    "Swedish",
    "Tagalog",
    "Tajik",
    "Tamil",
    "Tatar",
    "Telugu",
    "Thai",
    "Tibetan",
    "Turkish",
    "Turkmen",
    "Ukrainian",
    "Urdu",
    "Uzbek",
    "Valencian",
    "Vietnamese",
    "Welsh",
    "Yiddish",
    "Yoruba"
]


class WhisperClient(pykka.ThreadingActor):
    """An HTTP/REST client, which delegates translation / transcription tasks toan OpenAI Whisper server."""

    # TODO: This needs to be done

    def __init__(self, app, options: dict) -> None:
        super(pykka.ThreadingActor, self).__init__()
        self.app = app
        self.options = options

    def process_audio(self, options: dict) -> str:
        """Takes a file path to a .wav file and returns the transcribed or translated text."""
        self.options = options


class LocalWhisper(pykka.ThreadingActor):
    """A local instance of OpenAI Whisper for translation and transcription."""

    def __init__(self, app, options: dict) -> None:
        super(pykka.ThreadingActor, self).__init__()
        self.app = app
        self.options = options
        self.model_initialized = False
        self.audio_model = None

    def init_model(self):
        """initialization of the whisper model."""
        model = self.options["model"]
        english = self.options["language"] == "English"
        if model != "large" and english:
            model = model + ".en"
        self.audio_model = whisper.load_model(model)


    def process_audio(self, filepath: str, options: dict) -> str:
        """Takes a file path to a .wav file and returns the transcribed or translated text."""
        old_model = self.options["model"]
        old_language = self.options["language"]
        model = options["model"]
        language = options["language"]

        if old_model != model:
            self.model_initialized = False
        if (old_language == "English" and language != "English") or (old_language != "English" and language == "English"):
            self.model_initialized = False
        if not self.model_initialized:
            self.init_model()

        self.options = options

        # create a text out of the audio file
        result = self.audio_model.transcribe(filepath, language=language, fp16=self.options["use_gpu"], task=self.options["task"])
        text = result["text"]

        # call the gui for viewing or other kind of processing the text
        self.app.process_text(text)

        # remove the audio file
        os.remove(filepath)


class VoiceRecorder(pykka.ThreadingActor):
    """An indefinite loop of voice recording and speech processing."""
    
    def __init__(self, app, options: dict) -> None:
        super().__init__()
        self.app = app
        self.perform_recording = True

        # later, we want to loop infinitely, but have a look into the message inbox
        # so we need a self reference and a loop is then a function call,
        # which is positioned at the end of the message inbox of the actor
        self.me = self.actor_ref.proxy()

        # create the target directory for audio files
        self.target_dir = os.path.join(os.getcwd(), "audio_data")
        os.makedirs(self.target_dir, exist_ok=True)

        # remove audio files from the audio_data directory
        files = glob.glob(self.target_dir + "/*.wav")
        for f in files:
            os.remove(f)
        self.set_options(options)

        # call the speech recognizer
        if self.options["local"]:
            self.speech_recognizer = LocalWhisper.start(self.app, self.options).proxy()
        else:
            self.speech_recognizer = WhisperClient.start(self.app, self.options).proxy()

    def set_options(self, options: dict) -> None:
        """parameterize the speech recognizer based on new options."""
        self.options = options
        energy = 300
        dynamic_energy = False
        pause = float(self.options["pause"])
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.energy_threshold = energy
        self.recognizer.pause_threshold = pause
        self.recognizer.dynamic_energy_threshold = dynamic_energy
    
    def record(self) -> None:
        """Record human voice and save it into a file."""
        if self.perform_recording:
            with speech_recognition.Microphone(sample_rate=16000) as source:
                audio = self.recognizer.listen(source)
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = pydub.AudioSegment.from_file(data)
                file_name = str(int(time.time())) + ".wav"
                target_file = os.path.join(self.target_dir, file_name)
                audio_clip.export(target_file, format="wav")

            # Here we call the speech recognizer in a fire and forget format.
            # The recognizer will keep care to inform the GUI of the results.
            self.speech_recognizer.process_audio(target_file, self.options)
    
    def record_loop(self) -> None:
        """whenever you finished recording, start a new recording process."""
        self.me.record()
        self.me.record_loop()
    
    def process_text(self) -> None:
        """To be called from the speech recognizer."""
        self.app.process_text(self.options)

    def active(self, value: int) -> None:
        """activation of recording."""
        self.perform_recording = value > 0


def form_field(parent, text):
    """Creates a container with a left-side label with the intention of a right-side component."""
    container = tkinter.Frame(parent, bd=10)
    container.pack(fill="x", expand=False, pady=1, side="top")
    label = tkinter.Label(master=container, text=text)
    label.pack(side="left", padx=5)
    return container


def combobox(parent, text: str, options: list[str], default: int, cmd):
    """Creates a combobox in combination with a label."""
    container = form_field(parent, text)
    combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(container, state="readonly", values=options)
    combo.current(default)
    combo.pack(side="right", padx=5)
    combo.bind('<<ComboboxSelected>>', cmd)
    return combo


def textarea(parent):
    """Creates a scrollable textarea."""
    container = tkinter.Frame(parent, borderwidth=1, relief="sunken")
    text = tkinter.Text(container, width=24, height=13, wrap=tkinter.WORD, borderwidth=0)
    textVsb = tkinter.Scrollbar(container, orient="vertical", command=text.yview)
    textHsb = tkinter.Scrollbar(container, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=textVsb.set, xscrollcommand=textHsb.set)
    text.grid(row=0, column=0, sticky="nsew")
    textVsb.grid(row=0, column=1, sticky="ns")
    textHsb.grid(row=1, column=0, sticky="ew")
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    container.pack(side="top", fill="both", expand=True, padx=5, pady=5)
    return text


def checkbox(parent, text, default: int = 0, command=None):
    """Creates a checkbox in combination with a label."""
    container = form_field(parent, text)
    status = tkinter.IntVar(value=default)
    ckbtn = tkinter.Checkbutton(container, text="", variable=status, command=command)
    ckbtn.pack(side="right", padx=5)
    return status


class App(tkinter.Tk):
    """Application class for text transcription or translation."""

    def __init__(self, options):
        super().__init__()
        self.options = options
        self.title("Speech Recognition with OpenAI Whisper")
        self.geometry("600x800")

        # construct the elements of the graphic user interface
        frame = tkinter.ttk.LabelFrame(self, text="Parameters")
        frame.pack(padx=15, pady=15, fill="x")
        self.model_cb   = combobox(frame, "Model:", ["tiny", "base", "small", "medium", "large"], 0, self.options_changed)
        self.language_cb   = combobox(frame, "Language:", LANGUAGES, 30, self.options_changed)
        self.task_cb = combobox(frame, "Task:",  ["transcribe", "translate"], 0, self.options_changed)
        self.format_cb     = combobox(frame, "Format:", ["normal", "stripped"], 0, self.options_changed)
        pause_options = [str(float(i/10)) for i in range(5,51)]
        self.pause_cb     = combobox(frame, "Pause [s]:", pause_options, 3, self.options_changed)
        self.active = checkbox(frame, "Active:", default=1, command=self.update_active)
        self.ctrl_c_ctrl_v = checkbox(frame, "Insert via CTRL-V:", default=1, command=self.update_active)
        
        frame2 = tkinter.ttk.LabelFrame(self, text="Text")
        frame2.pack(padx=15, pady=15, fill="both", expand=True)
        self.text_area = textarea(frame2)
        self.update_options()

        # Initialize the voice recorder
        self.recorder = VoiceRecorder.start(self, self.options).proxy()
        self.recorder.set_options(self.options)
        self.recorder.record_loop()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_active(self):
        """toggle the speech processing"""
        self.recorder.active(self.active.get())

    def update_options(self):
        """transform the elements of the graphical user interface into dictionary values."""
        self.options["model"] = self.model_cb.get()
        self.options["language"] = self.language_cb.get()
        self.options["task"] = self.task_cb.get()
        self.options["format"] = self.format_cb.get()
        self.options["pause"] = self.pause_cb.get()

    def options_changed(self, event):
        """React on any change of options."""
        self.update_options()
        self.recorder.set_options(self.options)

    def on_closing(self):
        """Action, which is performed, when the window is closed."""
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            # since several threads are running, we need to use the hard way:
            os.kill(os.getpid(), 9)

    def process_text(self, text: str) -> None:
        # put it on the terminal window
        print(f"TEXT: {text}")

        if self.options["format"] == "stripped":
            text = text.strip()

        # insert text into any application over the clipboard function CTRL-V
        insert = self.ctrl_c_ctrl_v.get() > 0
        if insert:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')  # windows applications
        
        # insert the text into the app-textarea
        self.text_area.insert(tkinter.INSERT, text)


def get_options():
    """Parsing of the command line arguments."""
    options = {}

    parser = argparse.ArgumentParser(description="Graphical User Interface for an OpenAI Whisper speech recognizer.")
    parser.add_argument(
        "--local",
        type=str,
        help="Indicator, whether OpenAI Whisper will be instantiated locally; value is one of [true, false], default = true.",
        default="true",
    )
    parser.add_argument(
        "--device",
        type=str,
        help="Overwrites auto-detection of GPU; possible value is one of [cpu, gpu].",
        #default="cpu",
    )

    args = parser.parse_args()  # will stop the program if model is not defined
    possible_local_values = ["true", "false"]
    if args.local not in possible_local_values:
        default_local_value = parser.get_default("local")
        logging.warning(f"'local' has no valid value. We reset it to '{default_local_value}'. The value should be one of {str(possible_local_values)}.")
        args.local = default_local_value
    options["local"] = args.local.lower() == "true"
        
    if args.device is not None:
        possible_device_values = ["cpu", "gpu"]
        if args.device.lower() not in possible_device_values:
            default_device_value = parser.get_default("device")
            logging.warning(f"'device' has no valid value. We reset it to '{default_device_value}'. The value should be one of {str(possible_device_values)}.")
            args.device = default_device_value
        options["use_gpu"] = args.device.lower() == "gpu"
    else:
        options["use_gpu"] = torch.cuda.is_available()

    return options


if __name__ == "__main__":
    try:
        options = get_options()
        app = App(options)
        app.mainloop()
    except KeyboardInterrupt:
        # since several threads are running, we need to use the hard way:
        os.kill(os.getpid(), 9)

        ## These commands are usually used to stop all actor activities.
        ## However, it didn't succeed here.
        # app.destroy()
        # pykka.ActorRegistry.stop_all()
        # print("All actors stopped")


