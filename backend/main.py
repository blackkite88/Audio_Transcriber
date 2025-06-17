from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import tempfile
import shutil

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://audio-transcriber-mocha.vercel.app/", "http://localhost:3000"],  # frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model = WhisperModel("base", device="CUDA", compute_type="float16")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            with open(tmp.name, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_path = tmp.name

        # Transcribe using faster-whisper
        segments, info = model.transcribe(temp_path, beam_size=5)

        # Build transcript text from segments
        transcript = "".join([seg.text for seg in segments])

        return {
            "transcript": transcript.strip()
        }

    except Exception as e:
        return {"error": str(e)}