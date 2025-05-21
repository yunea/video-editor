import whisper
import subprocess
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

print(f"Traitement de la vidéo : {input_path}")

model = whisper.load_model("base")
result = model.transcribe(input_path)
print("Transcription terminée.")

# Enlever les silences avec FFmpeg
command = [
    "ffmpeg",
    "-i", input_path,
    "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-35dB",
    "-c:v", "copy",
    output_path
]

print(f"Montage en cours : {output_path}")
subprocess.run(command)
print("Montage terminé.")
