# DNEXT Support Chatbot - Complete Deployment Guide

This guide covers setting up and deploying both the React frontend and Python backend.

## Prerequisites

- Node.js 18+
- Python 3.8+
- npm, pnpm, or yarn
- Git
- Docker (optional, for containerized deployment)

## Local Development Setup

### Step 1: Clone and Navigate

```bash
cd /path/to/dnext-support-chatbot
```

### Step 2: Setup Python Backend

```bash
# Create Python environment
python -m venv venv

# Activate environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install flask flask-cors python-dotenv

# Create backend/.env with configuration
cat > backend/.env << EOF
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///chatbot.db
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=./chroma_db
MAX_FILE_SIZE=10485760
JWT_SECRET=dev-secret-key-change-in-production
SESSION_TIMEOUT=86400
API_TIMEOUT=30
EOF
```

### Step 3: Setup React Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_THEME=system
EOF

cd ..
```

### Step 4: Start Services

**Terminal 1 - Python Backend:**

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python backend/api_server.py
# Output: Running on http://127.0.0.1:8000
```

**Terminal 2 - React Frontend:**

```bash
cd frontend
npm run dev
# Output: ▲ Next.js 16.0.0
#         - Local:        http://localhost:3000
```

### Step 5: Test

1. Open http://localhost:3000 in browser
2. Sign in with any email and name
3. Send a test message
4. Verify response appears

## Production Deployment

### Option 1: Vercel (Recommended for Frontend)

#### Frontend Deployment

1. **Push to GitHub**:

```bash
git add .
git commit -m "Modern UI redesign"
git push origin main
```

2. **Deploy to Vercel**:

```bash
cd frontend
npm i -g vercel
vercel deploy --prod
```

3. **Configure Environment Variables** in Vercel Dashboard:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_DEFAULT_THEME=system
```

#### Backend Deployment (Railway, Render, or Heroku)

**Using Railway** (easiest):

1. Go to https://railway.app
2. Create new project
3. Connect GitHub repository
4. Select the root directory
5. Add environment variables:

```env
BACKEND_PORT=8000
FRONTEND_URL=https://your-frontend.vercel.app
DATABASE_URL=postgresql://user:pass@host/db
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=./chroma_db
MAX_FILE_SIZE=10485760
JWT_SECRET=<generate-strong-secret>
SESSION_TIMEOUT=86400
API_TIMEOUT=30
```

6. Deploy with: `pip install gunicorn`
7. Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.api_server:app`

### Option 2: Docker Deployment

#### Create Docker Compose File

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - BACKEND_PORT=8000
      - FRONTEND_URL=http://localhost:3000
      - DATABASE_URL=postgresql://user:password@db:5432/chatbot
      - RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
      - VECTOR_DB_PATH=/app/chroma_db
      - JWT_SECRET=your-secret-key
    depends_on:
      - db
    volumes:
      - ./chroma_db:/app/chroma_db
    networks:
      - chatbot-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - chatbot-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=chatbot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - chatbot-network

volumes:
  postgres_data:

networks:
  chatbot-network:
    driver: bridge
```

#### Backend Dockerfile

```dockerfile
# Dockerfile.backend
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn flask flask-cors python-dotenv

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "backend.api_server:app"]
```

#### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

#### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 3: AWS Deployment

#### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 dnext-chatbot

# Create environment
eb create dnext-prod

# Deploy
git push

# Monitor
eb logs
eb status
```

#### Using AWS App Runner

```bash
# Push to ECR
aws ecr create-repository --repository-name dnext-backend
docker tag dnext-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/dnext-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/dnext-backend:latest

# Create App Runner service via AWS Console
# Select ECR source and configure
```

### Option 4: Traditional Server (VPS/Dedicated)

#### Setup Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nodejs npm postgresql

# Clone repository
git clone https://github.com/your-org/dnext-support-chatbot.git
cd dnext-support-chatbot

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup frontend
cd frontend
npm install
npm run build
cd ..
```

#### Systemd Service Files

**Backend Service** (`/etc/systemd/system/dnext-backend.service`):

```ini
[Unit]
Description=DNEXT Chatbot Backend
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/dnext-support-chatbot
Environment="PATH=/home/user/dnext-support-chatbot/venv/bin"
ExecStart=/home/user/dnext-support-chatbot/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    backend.api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/dnext-frontend.service`):

```ini
[Unit]
Description=DNEXT Chatbot Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/dnext-support-chatbot/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_API_URL=https://api.yourdomain.com"

[Install]
WantedBy=multi-user.target
```

#### Enable Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable dnext-backend dnext-frontend
sudo systemctl start dnext-backend dnext-frontend
sudo systemctl status dnext-backend dnext-frontend
```

#### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/dnext
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/dnext /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Performance Optimization

### Frontend Optimization

```typescript
// Use dynamic imports for large components
import dynamic from 'next/dynamic'
const HeavyComponent = dynamic(() => import('./HeavyComponent'))

// Optimize images
import Image from 'next/image'
<Image src="/image.png" alt="desc" width={400} height={300} />

// Use React.memo for expensive components
export default React.memo(MyComponent)
```

### Backend Optimization

```python
# Enable caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/data')
@cache.cached(timeout=300)
def get_data():
    return {'data': 'cached'}

# Use connection pooling
from sqlalchemy.pool import QueuePool
```

## Monitoring & Logging

### Application Logging

```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Error Tracking

```bash
# Install Sentry
pip install sentry-sdk

# Initialize in backend
import sentry_sdk
sentry_sdk.init("https://key@sentry.io/project")
```

### Health Checks

```python
@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}, 200
```

## Database Migrations

```bash
# Using Alembic
pip install alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

## Security Checklist

- [ ] Use HTTPS/TLS for all connections
- [ ] Set strong JWT secret key
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Validate all user inputs
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Setup monitoring and alerts
- [ ] Regular security audits
- [ ] Keep dependencies updated

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

### CORS Errors

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Database Connection Issues

```bash
# Test connection
psql postgresql://user:pass@host:5432/dbname

# Check logs
journalctl -u dnext-backend -n 100
```

## Rollback Procedure

```bash
# Revert to previous version
git revert HEAD
git push

# Rebuild and redeploy
vercel deploy --prod  # Frontend
eb deploy  # Backend (if using EB)
```

## Support & Resources

- **Documentation**: See `frontend/README.md` and `INTEGRATION_GUIDE.md`
- **Issues**: GitHub Issues
- **Monitoring**: Application logs and error tracking

---

Last Updated: 2026-03-05
