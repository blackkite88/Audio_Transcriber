import React, { useState, useRef } from "react";

const Transcriber: React.FC = () => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState<string>("");
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunks = useRef<Blob[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setAudioFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!audioFile) return;

    const formData = new FormData();
    formData.append("file", audioFile);

    try {
      const res = await fetch("https://audio-transcriber-dxni.onrender.com/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setTranscript(data.transcript || "No transcript received.");
    } catch (error) {
      console.error("Error uploading file:", error);
      setTranscript("Error during transcription.");
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      recordedChunks.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) recordedChunks.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(recordedChunks.current, { type: "audio/webm" });
        const file = new File([audioBlob], "recording.webm", { type: "audio/webm" });

        const formData = new FormData();
        formData.append("file", file);

        try {
          const res = await fetch("https://audio-transcriber-dxni.onrender.com/transcribe", {
            method: "POST",
            body: formData,
          });
          const data = await res.json();
          setTranscript(data.transcript || "No transcript received.");
        } catch (err) {
          console.error("Recording transcription failed:", err);
          setTranscript("Recording transcription failed.");
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing mic:", err);
      alert("Microphone access is required to record.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-center">🎧 AI Audio Transcriber</h1>

      <div className="mb-6 text-center">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="px-5 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
          >
            🎙️ Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-5 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
          >
            ⏹ Stop & Transcribe
          </button>
        )}
      </div>

      <div className="mb-6 text-center">
        <input
          type="file"
          accept="audio/*"
          onChange={handleFileChange}
          className="mb-2"
        />
        <br />
        <button
          onClick={handleSubmit}
          className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          Upload & Transcribe
        </button>
      </div>

      {transcript && (
        <div className="mt-4 p-4 rounded border">
          <h2 className="font-semibold mb-2">Transcript:</h2>
          <p className="whitespace-pre-wrap">{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default Transcriber;
