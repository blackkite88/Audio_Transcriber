from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import tempfile
import shutil

app=FastAPI()

app = FastAPI()

# Set your frontend domain here
origins = [
    "https://audio-transcriber-mocha.vercel.app",  # Replace with your actual frontend URL
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Only allow your frontend
    allow_credentials=True,
    allow_methods=["*"],             # Or ["POST"] if you're strict
    allow_headers=["*"],             # Or specific headers like ["Content-Type"]
)
model = WhisperModel("tiny", device="cpu", compute_type="int8")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            with open(tmp.name, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_path = tmp.name

        # Transcribe using faster-whisper
        segments, info = model.transcribe(temp_path, beam_size=1, language="en")

        # Build transcript text from segments
        transcript = "".join([seg.text for seg in segments])

        return {
            "transcript": transcript.strip()
        }

    except Exception as e:
        return {"error": str(e)}