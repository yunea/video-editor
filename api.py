from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import whisper
import os
import uuid

app = FastAPI()

# Répertoire pour stocker temporairement les vidéos
UPLOAD_DIR = "/app/videos/input"
OUTPUT_DIR = "/app/videos/output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "video-editor API is running 🚀"}

@app.post("/edit")
async def edit_video(file: UploadFile = File(...)):
    # Générer un nom de fichier unique
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, f"edited_{filename}")

    # Sauvegarder la vidéo uploadée
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Transcrire avec Whisper (optionnel pour debug ou future analyse)
    model = whisper.load_model("base")
    print(f"Transcription de {input_path}...")
    result = model.transcribe(input_path)
    print("Transcription terminée.")

    # Supprimer les silences avec ffmpeg
    print(f"Montage vers {output_path}...")
    command = [
        "ffmpeg",
        "-y",  # Forcer l'écrasement s'il existe déjà
        "-i", input_path,
        "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-35dB",
        "-c:v", "libx264",         # Réencoder la vidéo
        "-preset", "veryfast",     # Vitesse d'encodage
        "-crf", "23",              # Qualité vidéo
        "-c:a", "aac",             # Encodage audio
        output_path
    ]
    subprocess.run(command, check=True)
    print("Montage terminé.")

    # Retourner la vidéo éditée en tant que fichier à télécharger
    return FileResponse(
        path=output_path,
        filename=os.path.basename(output_path),
        media_type="video/mp4"
    )
