import argparse
import logging
import os
import pathlib
import shutil

import fastapi
import uvicorn
import whisper
from devtools import debug  # only for debug

# init
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(THIS_DIR, ".uploads")

app = fastapi.FastAPI()

parser = argparse.ArgumentParser(description="Server for transcribing files using OpenAI Whisper.")
parser.add_argument(
    "--port",
    type=int,
    help="server port to connect to on the host if local=false; default is 8000",
    default=8000
)
args = parser.parse_args()

port = 8000
if args.port is not None:
    port = args.port

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
    return fastapi.responses.RedirectResponse(url="/docs", status_code=302)

# transcribe endpoint
@app.post("/sr/transcribe")
async def transcribe_file(file: fastapi.UploadFile, model: str, language: str, task: str):
    """endpoint for transcribing a .wav file"""

    # path
    save_path= os.path.join(STORAGE_DIR, str(file.filename))

    # save
    pathlib.Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    # transcribe
    return {"text": await process_audio(save_path, model, language, task)}

# start
uvicorn.run(app=app, host="0.0.0.0", port=port)