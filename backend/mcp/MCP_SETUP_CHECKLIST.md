# MCP Server Setup Checklist

Use this checklist to set up the MCP server and onboard colleagues.

---

## Phase 1: Server Setup

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] Backend FastAPI server ready on `http://localhost:8000`
- [ ] VSCode or terminal access

### Installation
- [ ] Navigate to `backend/mcp` directory
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify installation: `python -c "import fastapi, httpx, pydantic; print('OK')"`

### Configuration
- [ ] Create `.env` file in `backend/mcp/`:
  ```
  BACKEND_URL=http://localhost:8000
  MCP_PORT=8001
  MCP_KEYS_FILE=./keys.json
  ```
- [ ] Verify backend is running: `curl http://localhost:8000/api/health`

### Server Start
- [ ] Run `python server_secure.py`
- [ ] Check output for: `Application startup complete`
- [ ] Test health endpoint: `curl http://localhost:8001/health`
- [ ] Expected response: `{"status":"ok","service":"dnext-mcp-server","version":"1.0.0"}`

---

## Phase 2: API Key Management

### For Each Colleague

For each colleague who needs access:

**Colleague: _________________**

- [ ] Name/Email: `_________________`
- [ ] Generate key:
  ```bash
  python manage_keys.py generate --name "colleague@email.com" --expires 30
  ```
- [ ] Generated API Key: `_________________`
- [ ] Copy key to secure location (password manager, etc.)
- [ ] Document expiration date: `_________________`
- [ ] Share key with colleague via secure channel (NOT email/chat)
- [ ] Colleague confirms receipt

**Colleague: _________________**

- [ ] Name/Email: `_________________`
- [ ] Generate key:
  ```bash
  python manage_keys.py generate --name "colleague@email.com" --expires 30
  ```
- [ ] Generated API Key: `_________________`
- [ ] Copy key to secure location
- [ ] Document expiration date: `_________________`
- [ ] Share key with colleague
- [ ] Colleague confirms receipt

**Colleague: _________________**

- [ ] Name/Email: `_________________`
- [ ] Generate key:
  ```bash
  python manage_keys.py generate --name "colleague@email.com" --expires 30
  ```
- [ ] Generated API Key: `_________________`
- [ ] Copy key to secure location
- [ ] Document expiration date: `_________________`
- [ ] Share key with colleague
- [ ] Colleague confirms receipt

### Verify Keys Created
- [ ] Run `python manage_keys.py list`
- [ ] Verify all colleagues appear in output
- [ ] Check all keys show `Status: Active`

---

## Phase 3: Testing

### Test with cURL

- [ ] Send test message:
  ```bash
  curl -X POST http://localhost:8001/tools/send-message \
    -H "Authorization: Bearer <YOUR_API_KEY>" \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello! Test message", "session_id": "test"}'
  ```
- [ ] Expected: Status 200 with response text

- [ ] Test search:
  ```bash
  curl -X POST http://localhost:8001/tools/search \
    -H "Authorization: Bearer <YOUR_API_KEY>" \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "limit": 3}'
  ```
- [ ] Expected: Status 200 with search results

- [ ] Test tool info:
  ```bash
  curl -X GET http://localhost:8001/tools/info \
    -H "Authorization: Bearer <YOUR_API_KEY>"
  ```
- [ ] Expected: Status 200 with tool definitions

### Test with Python Client

- [ ] Navigate to `backend/mcp/examples`
- [ ] Update `client_python.py`:
  - [ ] Set `server_url` to your MCP server URL
  - [ ] Set `api_key` to your test key
- [ ] Run `python client_python.py`
- [ ] Check output:
  - [ ] Message sent successfully
  - [ ] Search returns results
  - [ ] Tools info displays

### Test with TypeScript/JavaScript

- [ ] Copy `examples/client_typescript.ts` to your project
- [ ] Update configuration:
  - [ ] Server URL
  - [ ] API key
- [ ] Test in browser console or Node.js:
  ```javascript
  const client = new DNEXTMCPClient('http://localhost:8001', 'dnext_xxx')
  client.sendMessage('Hello!').then(r => console.log(r))
  ```
- [ ] Check response

---

## Phase 4: Documentation

### Prepare for Colleagues

- [ ] Review `COLLEAGUE_QUICK_START.md`
- [ ] Prepare printout or digital copy
- [ ] Create setup instructions document:
  - [ ] Server URL: `_________________`
  - [ ] Example API Key format: `dnext_xxxxxxxxxxxxx`
  - [ ] Python example setup
  - [ ] JavaScript example setup
  - [ ] Contact for issues

### Document API Keys

Create a spreadsheet with:
- [ ] Colleague name
- [ ] Email
- [ ] API Key (first 10 chars only for security)
- [ ] Created date
- [ ] Expiration date
- [ ] Status (Active/Revoked)
- [ ] Usage count (run `list` command periodically)

---

## Phase 5: Deployment

### For Local/Development Only
- [ ] No additional steps
- [ ] Server accessible on `http://localhost:8001`

### For Production (VPS/Server)

- [ ] Server IP/Domain: `_________________`
- [ ] Install Python 3.8+
- [ ] Clone repository
- [ ] Install dependencies: `pip install -r backend/mcp/requirements.txt`
- [ ] Create `.env` file with production URLs
- [ ] Update `BACKEND_URL` to production backend
- [ ] Generate API keys
- [ ] Configure firewall:
  - [ ] Allow port 8001 (or behind reverse proxy)
  - [ ] Restrict to needed sources
- [ ] Set up reverse proxy (nginx):
  ```nginx
  location /mcp/ {
    proxy_pass http://localhost:8001/;
    proxy_set_header Authorization $http_authorization;
  }
  ```
- [ ] Test from external network
- [ ] Set up monitoring/alerts

### For Docker Deployment

- [ ] Build image: `docker build -f backend/mcp/Dockerfile -t dnext-mcp:latest .`
- [ ] Test locally:
  ```bash
  docker run -p 8001:8001 \
    -e BACKEND_URL=http://host.docker.internal:8000 \
    dnext-mcp:latest
  ```
- [ ] Verify: `curl http://localhost:8001/health`
- [ ] Push to registry (if needed)
- [ ] Deploy to production environment
- [ ] Create volume for API keys persistence
- [ ] Set up health checks
- [ ] Configure auto-restart policy

---

## Phase 6: Ongoing Maintenance

### Daily
- [ ] Monitor server health: `curl http://localhost:8001/health`
- [ ] Check logs for errors
- [ ] Verify backend connectivity

### Weekly
- [ ] Run `python manage_keys.py list`
- [ ] Check for unused keys
- [ ] Review usage patterns

### Monthly
- [ ] Review API key expiration dates
- [ ] Regenerate expiring keys
- [ ] Revoke inactive keys
- [ ] Update colleague access list

### As Needed
- [ ] New colleague: Generate new key
- [ ] Revoke access: `python manage_keys.py revoke --key "dnext_xxx"`
- [ ] Troubleshoot: Check logs, test endpoints
- [ ] Update: Pull latest code, restart server

---

## Troubleshooting Matrix

| Problem | Cause | Solution |
|---------|-------|----------|
| Connection refused | Server not running | Run `python server_secure.py` |
| Backend error | Backend down | Check `http://localhost:8000/api/health` |
| Invalid API key | Wrong key format | Verify format: `dnext_xxxxx` |
| Expired key | Key expired | Generate new key |
| File upload fails | Wrong file type | Use .pdf, .jpg, .jpeg, .png only |
| CORS error | Browser blocking | Use reverse proxy with CORS headers |

---

## Security Checklist

- [ ] API keys stored securely (not in code, not in chat)
- [ ] `.env` file added to `.gitignore`
- [ ] `keys.json` file has restricted permissions (600)
- [ ] Production server uses HTTPS
- [ ] Firewall restricts access to needed sources only
- [ ] Keys rotated regularly
- [ ] Unused keys revoked
- [ ] Logs monitored for suspicious activity
- [ ] Backup procedure for `keys.json` file

---

## Rollout Plan

### Week 1: Setup & Testing
- [ ] Complete Phase 1-3 above
- [ ] Test all endpoints
- [ ] Verify client libraries work

### Week 2: Soft Launch
- [ ] Select 2-3 trusted colleagues
- [ ] Generate their API keys
- [ ] Share COLLEAGUE_QUICK_START.md
- [ ] Support their setup
- [ ] Gather feedback

### Week 3: Full Rollout
- [ ] Generate keys for all colleagues
- [ ] Send setup instructions
- [ ] Hold optional training session
- [ ] Monitor usage and issues
- [ ] Document common questions

### Week 4: Stabilization
- [ ] All colleagues using MCP server
- [ ] Document common patterns
- [ ] Optimize based on usage
- [ ] Plan Phase 2 enhancements

---

## Sign-Off

- [ ] Server setup complete: Date `_________` By `__________________`
- [ ] All tests passed: Date `_________` By `__________________`
- [ ] Documentation reviewed: Date `_________` By `__________________`
- [ ] Team trained: Date `_________` By `__________________`
- [ ] Production deployed: Date `_________` By `__________________`

---

## Notes & Issues

```
Issue: ___________________________
Solution: _________________________
Date: ____________

Issue: ___________________________
Solution: _________________________
Date: ____________

Issue: ___________________________
Solution: _________________________
Date: ____________
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Next Review**: [Date]
