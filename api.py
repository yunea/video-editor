from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
import subprocess
import whisper
import os
import uuid

app = FastAPI()

INPUT_DIR = "/app/videos/input"
OUTPUT_DIR = "/app/videos/output"
TEMP_DIR = "/app/videos/temp"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "video-editor API is running 🚀"}

@app.post("/edit")
async def edit_video(filename: str = Form(...)):
    input_path = os.path.join(INPUT_DIR, filename)

    if not os.path.isfile(input_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé.")

    output_filename = f"edited_{filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    print(f"Chargement du modèle Whisper...")
    model = whisper.load_model("base")
    print(f"Transcription de {input_path}...")
    result = model.transcribe(input_path, word_timestamps=False)
    segments = result.get("segments", [])
    print("Transcription terminée.")

    # Fusionner les segments trop proches
    merged_segments = []
    gap_threshold = 0.8  # seuil max de silence à combler

    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        if not merged_segments:
            merged_segments.append([start, end])
        else:
            prev_start, prev_end = merged_segments[-1]
            if start - prev_end <= gap_threshold:
                # Fusionner avec le segment précédent
                merged_segments[-1][1] = end
            else:
                # Nouveau segment
                merged_segments.append([start, end])

    # Filtrer les micro-segments trop courts (< 0.2s)
    keep_segments = [(start, end) for start, end in merged_segments if end - start > 0.2]


    if not keep_segments:
        raise HTTPException(status_code=422, detail="Aucun segment parlé détecté.")

    print(f"Extraction de {len(keep_segments)} segments parlés...")

    list_file_path = os.path.join(TEMP_DIR, f"list_{uuid.uuid4().hex}.txt")
    part_files = []

    for i, (start, end) in enumerate(keep_segments):
        part_file = os.path.join(TEMP_DIR, f"part_{i}.mp4")
        cmd = [
          "ffmpeg", "-y",
          "-ss", str(start),
          "-to", str(end),
          "-i", input_path,
          "-c:v", "libx264",
          "-preset", "veryfast",
          "-crf", "23",
          "-c:a", "aac",
          part_file
        ]

        subprocess.run(cmd, check=True)
        part_files.append(part_file)

    # Générer le fichier concat
    with open(list_file_path, "w") as f:
        for part in part_files:
            f.write(f"file '{part}'\n")

    # Fusionner les segments
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        output_path
    ]
    subprocess.run(concat_cmd, check=True)
    print("Vidéo montée sans silences.")

    # Nettoyer les fichiers temporaires
    for part in part_files:
        if os.path.exists(part):
            os.remove(part)

    if os.path.exists(list_file_path):
        os.remove(list_file_path)

    print("Fichiers temporaires nettoyés.")


    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="video/mp4"
    )
