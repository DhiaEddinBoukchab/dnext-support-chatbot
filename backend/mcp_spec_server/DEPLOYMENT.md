# MCP Server Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- DNEXT backend running on `http://localhost:8000`

### Setup

```bash
cd backend/mcp_spec_server
pip install -r requirements.txt
```

### Run

```bash
python http_server.py
```

Server runs on `http://localhost:8001`

---

## Docker Deployment

### Build Image

```bash
cd backend/mcp_spec_server
docker build -t dnext-mcp-server:latest .
```

### Run Container

```bash
docker run -p 8001:8001 \
  -e BACKEND_URL=http://backend:8000 \
  --name dnext-mcp \
  dnext-mcp-server:latest
```

### With Docker Compose

Add to `docker-compose.yml`:

```yaml
mcp:
  build:
    context: ./backend/mcp_spec_server
  ports:
    - "8001:8001"
  environment:
    - BACKEND_URL=http://backend:8000
  depends_on:
    - backend
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

Then run:

```bash
docker-compose up -d mcp
```

---

## VPS/Server Deployment

### 1. Clone Repository

```bash
git clone <repo-url>
cd dnext-support-chatbot
```

### 2. Install Dependencies

```bash
cd backend/mcp_spec_server
pip install -r requirements.txt
```

### 3. Create .env

```bash
cat > .env << EOF
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
BACKEND_URL=http://localhost:8000
EOF
```

### 4. Create Systemd Service

Create `/etc/systemd/system/dnext-mcp.service`:

```ini
[Unit]
Description=DNEXT MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dnext-support-chatbot/backend/mcp_spec_server
ExecStart=/usr/bin/python3 http_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable dnext-mcp
sudo systemctl start dnext-mcp
sudo systemctl status dnext-mcp
```

### 6. Configure Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.dnext.com;

    location /mcp {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streaming support
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /health {
        proxy_pass http://localhost:8001/health;
    }
}
```

Reload nginx:

```bash
sudo systemctl reload nginx
```

### 7. SSL/HTTPS (Optional but Recommended)

Using Let's Encrypt with Certbot:

```bash
sudo certbot --nginx -d api.dnext.com
```

---

## AWS Deployment

### ECS/Fargate

1. **Create ECR Repository**:
   ```bash
   aws ecr create-repository --repository-name dnext-mcp-server
   ```

2. **Build and Push**:
   ```bash
   docker build -t dnext-mcp-server:latest .
   docker tag dnext-mcp-server:latest <account-id>.dkr.ecr.<region>.amazonaws.com/dnext-mcp-server:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/dnext-mcp-server:latest
   ```

3. **Create ECS Task Definition**:
   ```json
   {
     "family": "dnext-mcp-server",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "containerDefinitions": [
       {
         "name": "dnext-mcp",
         "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/dnext-mcp-server:latest",
         "portMappings": [{"containerPort": 8001, "protocol": "tcp"}],
         "environment": [
           {"name": "BACKEND_URL", "value": "http://backend:8000"}
         ]
       }
     ]
   }
   ```

4. **Create Service** and configure Load Balancer

---

## Monitoring

### Check Health

```bash
curl http://<server>:8001/health
```

Expected response:
```json
{"status":"ok","service":"dnext-mcp-server"}
```

### View Logs (Systemd)

```bash
sudo journalctl -u dnext-mcp -f
```

### View Logs (Docker)

```bash
docker logs -f dnext-mcp
```

### Monitor Tool Calls

The server logs every tool call with `[MCP HTTP] tool called: ...`

---

## Performance Tuning

### Uvicorn Workers

For high load, increase worker count in `http_server.py`:

```python
uvicorn.run(
    app,
    host=MCP_SERVER_HOST,
    port=MCP_SERVER_PORT,
    workers=4,  # Increase based on CPU cores
)
```

### Timeouts

Adjust in `config.py`:

```python
RESPONSE_TIMEOUT = 60  # seconds
```

### Load Balancing

For multiple instances, use:
- Nginx load balancer
- AWS ELB/ALB
- HAProxy

---

## Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8001

# Check backend connectivity
curl http://localhost:8000/api/health
```

### Slow Responses
- Check backend response time
- Monitor CPU/memory usage
- Check network latency to backend

### Connection Errors
- Verify firewall rules allow port 8001
- Check `BACKEND_URL` is correct
- Verify backend is running

---

## Rollback

### Systemd
```bash
sudo systemctl stop dnext-mcp
sudo systemctl start dnext-mcp
```

### Docker
```bash
docker stop dnext-mcp
docker rm dnext-mcp
docker run ...  # With previous image tag
```

---

## Updates

### Systemd
```bash
cd /var/www/dnext-support-chatbot
git pull origin main
sudo systemctl restart dnext-mcp
```

### Docker
```bash
git pull origin main
docker build -t dnext-mcp-server:v2 .
docker stop dnext-mcp
docker rm dnext-mcp
docker run -p 8001:8001 ... dnext-mcp-server:v2
```
