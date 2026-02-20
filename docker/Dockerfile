FROM python:3.11-slim

LABEL maintainer="dnext-support"
LABEL description="Dnext Support Chatbot with RAG"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300

RUN useradd -m -u 1000 appuser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Option 1: Install with increased timeout and retries
# Install large packages first with retry logic
RUN pip install --default-timeout=300 --retries 5 torch>=1.11.0 || \
    pip install --default-timeout=300 --retries 5 torch>=1.11.0 || \
    pip install --default-timeout=300 --retries 5 torch>=1.11.0

# Install remaining dependencies
RUN pip install --default-timeout=300 --retries 5 -r requirements.txt

# Download the sentence transformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

RUN mkdir -p /app/docs_md /app/chroma_db && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

CMD ["python", "app.py"]