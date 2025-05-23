FROM python:3.10-slim

# Installer FFmpeg et Git
RUN apt-get update && apt-get install -y ffmpeg git

# Copier les fichiers avant d’installer les dépendances
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY api.py .

# Lancer l'API FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3000"]
