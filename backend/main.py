from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import tempfile
import shutil
import time
import os

app = FastAPI()

# Allow frontend access (customize for your domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()  # Load variables from .env

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
HEADERS = {
    "authorization": ASSEMBLYAI_API_KEY,
    "content-type": "application/json"
}


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            with open(tmp.name, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_path = tmp.name

        # Step 2: Upload to AssemblyAI
        with open(temp_path, "rb") as audio_file:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers={"authorization": ASSEMBLYAI_API_KEY},
                files={"file": audio_file}
            )
            upload_response.raise_for_status()
            audio_url = upload_response.json()["upload_url"]

        # Step 3: Request transcription
        transcript_request = {
            "audio_url": audio_url,
            "language_code": "en_us",
            "auto_chapters": False
        }

        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json=transcript_request,
            headers=HEADERS
        )
        transcript_response.raise_for_status()
        transcript_id = transcript_response.json()["id"]

        # Step 4: Poll until transcription is done
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        while True:
            polling_response = requests.get(polling_url, headers=HEADERS)
            polling_response.raise_for_status()
            status = polling_response.json()["status"]

            if status == "completed":
                return {
                    "transcript": polling_response.json()["text"],
                }
            elif status == "error":
                return {"error": polling_response.json()["error"]}

            time.sleep(3)  # Wait 3 seconds before polling again

    except Exception as e:
        return {"error": str(e)}
