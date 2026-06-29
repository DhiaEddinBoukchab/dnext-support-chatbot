FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    API_PORT=8000

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY api ./api
COPY app ./app
COPY src ./src
COPY docs_md ./docs_md
COPY auth_service.py .
COPY config.py .
COPY database.py .
COPY models.py .

RUN mkdir -p /app/runtime_data /app/chroma_db

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT:-8000}"]
