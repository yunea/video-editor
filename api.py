from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
import subprocess
import whisper
import os

app = FastAPI()

INPUT_DIR = "/app/videos/input"
OUTPUT_DIR = "/app/videos/output"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "video-editor API is running 🚀"}

@app.post("/edit")
async def edit_video(filename: str = Form(...)):
    input_path = os.path.join(INPUT_DIR, filename)

    # Vérifie que le fichier existe
    if not os.path.isfile(input_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé.")

    output_filename = f"edited_{filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Transcription avec Whisper (utile pour logs ou analyse)
    model = whisper.load_model("base")
    print(f"Transcription de {input_path}...")
    result = model.transcribe(input_path)
    print("Transcription terminée.")

    # Suppression des silences avec ffmpeg
    print(f"Montage vers {output_path}...")
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-35dB",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(command, check=True)
    print("Montage terminé.")

    # Retourner la vidéo traitée
    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="video/mp4"
    )
