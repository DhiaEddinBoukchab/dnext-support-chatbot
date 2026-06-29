FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    API_PORT=8000

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY api ./api
COPY core ./core
COPY domain ./domain
COPY infrastructure ./infrastructure
COPY rag ./rag
COPY services ./services
COPY docs_md ./docs_md

RUN mkdir -p /app/runtime_data /app/chroma_db

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT:-8000}"]
