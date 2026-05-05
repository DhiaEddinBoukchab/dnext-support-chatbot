# Deployment Guide - Phase 1

This document covers deployment options for the DNEXT Support Chatbot V2 Phase 1.

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│       DNEXT Platform (Frontend)         │
│  - User Dashboard                       │
│  - Embedded Chat Widget                 │
└────────────────┬────────────────────────┘
                 │ HTTP/HTTPS
┌────────────────▼────────────────────────┐
│   Reverse Proxy / Load Balancer         │
│  (Nginx, CloudFront, API Gateway)       │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│  Backend API │  │  Frontend CDN  │
│  (FastAPI)   │  │  (React SPA)   │
│              │  │                │
│ Port: 8000   │  │ Port: 3000/80  │
└───────┬──────┘  └────────────────┘
        │
┌───────▼──────────────────┐
│  Data Storage             │
│ - SQLite / PostgreSQL     │
│ - ChromaDB / OpenSearch   │
│ - File Storage            │
└──────────────────────────┘
```

## Deployment Options

### Option 1: Docker Compose (Local/Self-Hosted)

Best for: Development, staging, small deployments

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- Open ports: 8000, 3000

**Steps:**

1. **Prepare Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Build and Run**
```bash
docker-compose build
docker-compose up -d
```

3. **Verify Services**
```bash
# Check status
docker-compose ps

# Check backend health
curl http://localhost:8000/api/health

# Check frontend
open http://localhost:3000
```

4. **View Logs**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

5. **Stop Services**
```bash
docker-compose down
```

### Option 2: Vercel (Frontend) + Self-hosted Backend

Best for: Production frontend with Vercel, custom backend

**Frontend Deployment (Vercel):**

1. **Push to GitHub**
```bash
git add .
git commit -m "Phase 1: Frontend/Backend Decoupling"
git push origin main
```

2. **Deploy Frontend**
- Go to vercel.com
- Import the `/frontend` directory
- Set environment variables:
  - `VITE_API_BASE_URL=https://api.your-domain.com`
- Deploy

3. **Update Backend URL**
```bash
# After backend is deployed, update frontend env var
VITE_API_BASE_URL=https://api.your-domain.com
```

**Backend Deployment (Server/VPS):**

1. **SSH into Server**
```bash
ssh user@your-server.com
```

2. **Clone Repository**
```bash
git clone https://github.com/THRE5H/dnext-support-chatbot.git
cd dnext-support-chatbot/backend
```

3. **Setup Python Environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create .env File**
```bash
cp ../.env.example .env
# Edit with production API keys
```

5. **Run with Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

6. **Setup with Systemd (for persistence)**
```bash
sudo nano /etc/systemd/system/dnext-api.service
```

Add:
```ini
[Unit]
Description=DNEXT Support Chatbot API
After=network.target

[Service]
User=app
WorkingDirectory=/home/app/dnext-support-chatbot/backend
Environment="PATH=/home/app/dnext-support-chatbot/backend/venv/bin"
ExecStart=/home/app/dnext-support-chatbot/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dnext-api
sudo systemctl start dnext-api
sudo systemctl status dnext-api
```

7. **Setup Nginx Reverse Proxy**
```bash
sudo nano /etc/nginx/sites-available/dnext-api
```

Add:
```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
    }

    # SSL (with Let's Encrypt)
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/api.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.your-domain.com/privkey.pem;
}
```

```bash
sudo systemctl reload nginx
```

### Option 3: AWS Deployment (Recommended for Production)

Best for: Enterprise, auto-scaling, managed services

**Architecture:**
- Backend: ECS Fargate + Application Load Balancer
- Frontend: CloudFront + S3
- Database: RDS PostgreSQL
- File Storage: S3

**Backend on AWS ECS:**

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name dnext-api --region us-east-1
```

2. **Build and Push Image**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t dnext-api:latest backend/
docker tag dnext-api:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/dnext-api:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/dnext-api:latest
```

3. **Create ECS Task Definition**
- CPU: 512 (0.5 vCPU)
- Memory: 1024 MB
- Container Port: 8000
- Environment variables from Secrets Manager

4. **Create ECS Service**
- Load Balancer: Application Load Balancer
- Target Group: dnext-api-tg
- Desired Count: 2 (auto-scaling)

**Frontend on AWS S3 + CloudFront:**

1. **Build Frontend**
```bash
cd frontend
npm run build
```

2. **Create S3 Bucket**
```bash
aws s3 mb s3://dnext-chat-widget --region us-east-1
```

3. **Upload Files**
```bash
aws s3 sync dist/ s3://dnext-chat-widget/ --delete
```

4. **Setup CloudFront Distribution**
- Origin: S3 bucket
- Viewer Protocol Policy: Redirect HTTP to HTTPS
- Cache Behavior: Optimal caching
- Custom Domain: chat-widget.your-domain.com

### Option 4: Docker Container on Any Cloud

Generic steps for any cloud provider (DigitalOcean, Linode, Heroku, etc.):

1. **Build Docker Image**
```bash
docker build -t dnext-api:latest backend/
docker build -t dnext-widget:latest frontend/
```

2. **Tag for Registry**
```bash
docker tag dnext-api:latest your-registry/dnext-api:latest
docker push your-registry/dnext-api:latest
```

3. **Deploy Container**
```bash
docker run -d \
  --name dnext-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -v /data:/app/data \
  your-registry/dnext-api:latest
```

## Health Checks & Monitoring

### Backend Health Check
```bash
curl -f http://localhost:8000/api/health || exit 1
```

### Application Monitoring
```bash
# Container logs
docker logs -f dnext-api

# System resources
docker stats dnext-api

# Network connectivity
curl -v http://localhost:8000/api/health
```

### Log Aggregation
Configure centralized logging (ELK, CloudWatch, Datadog):
```bash
# Redirect stdout to syslog
docker run ... --log-driver awslogs --log-opt awslogs-group=/ecs/dnext-api
```

## Production Checklist

Before deploying to production:

- [ ] Environment variables secured in secrets manager
- [ ] CORS origins properly configured
- [ ] SSL/TLS certificates installed (HTTPS)
- [ ] Database backups configured
- [ ] File storage backup strategy
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting setup
- [ ] Error tracking (Sentry, CloudWatch)
- [ ] Log aggregation configured
- [ ] Auto-scaling policies set
- [ ] Health checks configured
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] Team trained on deployment process

## Scaling Considerations

For Phase 1, expected capacity:
- ~100 concurrent users
- ~1000 messages/hour
- ~10GB storage initially

For Phase 2+ scaling:
- Implement message queue (AWS SQS, Celery)
- Add caching layer (Redis, ElastiCache)
- Migrate to PostgreSQL from SQLite
- Implement rate limiting per organization
- Add CDN for static assets
- Implement WebSockets for real-time updates

## Rollback Strategy

If deployment fails:

**Docker Compose:**
```bash
docker-compose down
git checkout previous-version
docker-compose up -d
```

**AWS ECS:**
```bash
# Revert task definition to previous version
aws ecs update-service \
  --cluster dnext-api-cluster \
  --service dnext-api-service \
  --task-definition dnext-api:previous-revision
```

**Manual Server:**
```bash
systemctl stop dnext-api
git checkout previous-version
systemctl start dnext-api
```

## Post-Deployment Verification

After deployment:

1. **Verify API Endpoints**
```bash
curl https://api.your-domain.com/api/health
```

2. **Test Chat Functionality**
```bash
curl -X POST https://api.your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

3. **Check Frontend**
Open https://chat.your-domain.com and test widget

4. **Monitor Logs**
```bash
# CloudWatch
aws logs tail /ecs/dnext-api --follow

# Server logs
tail -f /var/log/dnext-api.log
```

## Support

For deployment issues:
- Review logs for error messages
- Check environment variable configuration
- Verify network/firewall settings
- Contact infrastructure team
