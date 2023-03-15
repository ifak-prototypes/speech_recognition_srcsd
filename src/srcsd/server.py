import json
import os
from pathlib import Path

import uvicorn
import whisper
from devtools import debug  # only for debug
from fastapi import FastAPI, UploadFile, responses

# init
app = FastAPI()
(host, port) = ("localhost", 8000)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(THIS_DIR, ".uploads")
options = {
    "model": "tiny",
    "language": "en",
    "english": True,
    "task": "transcribe"
}
debug(options)
print(options)


# whisper
def init_model(options: dict):
    """initialization of the whisper model."""
    
    model = options["model"]
    english = options["language"] == "en"
    if model != "large" and english:
        model = model + ".en" # TODO
    return whisper.load_model(model)   

def process_audio(filepath: str, options: dict) -> str:
    """Takes a file path to a .wav file and returns the transcribed or translated text."""
    
    # init
    audio_model = init_model(options)
    language = options["language"]

    # create a text out of the audio file
    result = audio_model.transcribe(
        filepath,
        language=options["language"],
        task=options["task"]
    )

    # cleanup
    os.remove(filepath)
    
    return result["text"]

# root endpoint (redirect => /docs)
@app.get("/")
def redirect_docs():
    """root endpoint (redirecting to /docs)"""
    return responses.RedirectResponse(url="/docs", status_code=302)

# transcribe endpoint
@app.post("/sr/transcribe")
async def transcribe_file(file: UploadFile, options_str: str):
    """endpoint for transcribing a .wav file"""

    options = json.loads(options_str)

    # path
    SAVE_PATH = os.path.join(STORAGE_DIR, str(file.filename))

    # save
    Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    # transcribe
    return process_audio(SAVE_PATH, options)

# upload endpoint
@app.post("/test/upload")
async def upload_file(file: UploadFile):
    """endpoint for uploading files"""

    # path
    SAVE_PATH = os.path.join(STORAGE_DIR, str(file.filename))

    # type check
    if not file.content_type.startswith('audio/wav'):
        return {"error": "File must be in WAV format."}

    # save
    Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    # confirm
    return {
        "filename": file.filename,
        "saved_to": SAVE_PATH
    }

# download endpoint
@app.post("/test/download")
async def download_file(filename: str):
    """endpoint for downloading files"""

    # path
    SAVE_PATH = os.path.join(STORAGE_DIR, filename)

    # return download
    return responses.FileResponse(path=SAVE_PATH, filename=filename)

# start
uvicorn.run(app=app, host=host, port=port)