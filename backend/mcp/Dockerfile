FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for API keys
RUN mkdir -p /app/keys

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Set environment variables
ENV BACKEND_URL=http://backend:8000
ENV MCP_PORT=8001
ENV MCP_KEYS_FILE=/app/keys/keys.json

# Run server
CMD ["python", "server_secure.py"]
