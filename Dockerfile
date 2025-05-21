# Dockerfile
FROM python:3.10-slim

# Installer FFmpeg et Whisper
RUN apt-get update && apt-get install -y ffmpeg git && \
  pip install --no-cache-dir openai-whisper

WORKDIR /app
COPY edit_video.py .

ENTRYPOINT ["python", "edit_video.py"]
