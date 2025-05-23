# api.py
from fastapi import FastAPI, UploadFile, File, Form
import subprocess
import whisper

app = FastAPI()

@app.post("/edit")
async def edit_video(input_path: str = Form(...), output_path: str = Form(...)):
    model = whisper.load_model("base")
    print(f"Transcription de {input_path}...")
    result = model.transcribe(input_path)
    print("Transcription terminée.")

    print(f"Montage vers {output_path}...")
    command = [
        "ffmpeg",
        "-i", input_path,
        "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-35dB",
        "-c:v", "copy",
        output_path
    ]
    subprocess.run(command)
    print("Montage terminé.")

    return {"status": "success", "output": output_path}
