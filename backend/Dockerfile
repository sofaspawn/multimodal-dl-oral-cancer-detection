FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps for opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY scripts ./scripts

# ML weights are baked into the image at build time if present locally.
# If the file doesn't exist, the COPY will be skipped thanks to
# the glob pattern — Docker copies matching files, ignores misses.
COPY app/ml/weights/ ./app/ml/weights/

EXPOSE 8000
CMD ["sh", "-c", "if [ -n \"$MODEL_DOWNLOAD_URL\" ] && [ ! -f /app/app/ml/weights/resnet50_oral_cancer.pth ]; then mkdir -p /app/app/ml/weights && wget -qO /app/app/ml/weights/resnet50_oral_cancer.pth \"$MODEL_DOWNLOAD_URL\"; fi && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
