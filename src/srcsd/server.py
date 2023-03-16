import os
import shutil
from pathlib import Path
import logging
import argparse

import uvicorn
import whisper
from devtools import debug  # only for debug
from fastapi import FastAPI, UploadFile, responses

# init
app = FastAPI()

parser = argparse.ArgumentParser(description="Server for transcribing files using OpenAI Whisper.")
parser.add_argument(
    "--host",
    type=str,
    help="server hostname to connect to if local=false; default is localhost",
    default="localhost"
)
parser.add_argument(
    "--port",
    type=int,
    help="server port to connect to on the host if local=false; default is 8000",
    default=8000
)
args = parser.parse_args()

(host, port) = ("localhost", 8000)
if args.host is not None:
    host = args.host.lower()
if args.port is not None:
    port = args.port

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(THIS_DIR, ".uploads")

# cleanup ./uploads
try:
    shutil.rmtree(STORAGE_DIR)
    logging.info("CleanupInfo: Deleted .uploads")
except FileNotFoundError:
    logging.info(f"CleanupInfo: Skipping cleanup: No such directory: \'{STORAGE_DIR}\'")

# whisper
async def init_model(model: str, language: str):
    """initialization of the whisper model."""
    
    english = language == "en"
    if model != "large" and english:
        model = model + ".en"
    return whisper.load_model(model)   

async def process_audio(filepath: str, model: str, language: str, task: str) -> str:
    """Takes a file path to a .wav file and returns the transcribed or translated text."""

    # init
    audio_model = await init_model(model, language)

    # create a text out of the audio file
    result = audio_model.transcribe(
        filepath,
        language=language,
        task=task
    )

    # cleanup
    os.remove(filepath)
    
    return result["text"]

# root endpoint (redirect => /docs)
@app.get("/")
async def redirect_docs():
    """root endpoint (redirecting to /docs)"""
    return responses.RedirectResponse(url="/docs", status_code=302)

# transcribe endpoint
@app.post("/sr/transcribe")
async def transcribe_file(file: UploadFile, model: str, language: str, task: str):
    """endpoint for transcribing a .wav file"""

    # path
    SAVE_PATH = os.path.join(STORAGE_DIR, str(file.filename))

    # save
    Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    # transcribe
    return {"text": await process_audio(SAVE_PATH, model, language, task)}

# start
uvicorn.run(app=app, host=host, port=port)