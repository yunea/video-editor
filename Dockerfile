FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg git && \
  pip install --no-cache-dir openai-whisper fastapi uvicorn

WORKDIR /app
COPY api.py .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3000"]
