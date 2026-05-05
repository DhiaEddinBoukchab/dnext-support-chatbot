# Integration & Testing Guide - Phase 1

This document covers testing and integration validation for Phase 1 of the DNEXT Support Chatbot V2.

## Quick Test

### 1. Start Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","message":"DNEXT Support Chatbot API is running"}
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The widget will be available at `http://localhost:3000` (dev) or `http://localhost:5173` (Vite)

### 4. Test Chat Integration

Open `http://localhost:3000` and send a message. You should see:
- Message appears in the chat
- Loading state shows while streaming
- Response chunks arrive in real-time
- Full response displays when complete

## Automated Testing

### Backend Unit Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Files:**
- `tests/test_health.py` - Health check endpoint tests
- `tests/test_chat.py` - Chat endpoint integration tests

### Frontend Component Tests

```bash
cd frontend

# Run tests with Vitest
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Manual Integration Testing

### Scenario 1: Basic Text Chat

1. **Setup**: Start both backend and frontend
2. **Action**: Send message "What is DNEXT?"
3. **Expected**: 
   - Message appears in user chat bubble
   - Loading animation plays
   - Response streams in and completes
   - Session ID persists

**CURL equivalent:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is DNEXT?",
    "session_id": "test_session_123"
  }' | jq .
```

### Scenario 2: Multi-turn Conversation

1. **Setup**: Clear any previous session
2. **Action 1**: Send "Hello"
3. **Action 2**: Send "Tell me about features" (should reference previous context)
4. **Expected**:
   - Messages are numbered consecutively
   - Session ID remains the same
   - Context flows between messages
   - Conversation history preserved

### Scenario 3: File Upload (with Images)

1. **Setup**: Start both services
2. **Action**: 
   - Click attachment button
   - Select an image file
   - Add message: "Analyze this image"
   - Send
3. **Expected**:
   - File tag appears in input
   - File is processed
   - Response includes image analysis
   - File is saved to `data/uploads/`

**CURL equivalent:**
```bash
curl -X POST http://localhost:8000/api/chat/with-files \
  -F "message=Analyze this image" \
  -F "session_id=test_session_456" \
  -F "files=@/path/to/image.jpg"
```

### Scenario 4: Error Handling

**Test case 1: Empty message**
1. Action: Send empty message
2. Expected: Error message appears in frontend

**Test case 2: Backend down**
1. Action: Stop backend, try sending message
2. Expected: Connection error shown gracefully

**Test case 3: Invalid session**
1. Action: GET `/api/sessions/invalid_id`
2. Expected: 404 response

## Docker Integration Testing

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down
```

**Services running:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### Test with Docker

```bash
# Run backend tests in container
docker-compose exec backend pytest tests/ -v

# Check backend health
docker-compose exec backend curl http://localhost:8000/api/health

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Performance Testing

### Load Testing with curl

```bash
# Sequential requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"Test message '$i'"}' \
    -w "\nTime: %{time_total}s\n"
done

# Parallel requests with gnu-parallel
seq 1 20 | parallel -j 5 \
  'curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"Test {}\"}"'
```

### Browser DevTools Testing

1. Open `http://localhost:3000`
2. Open DevTools Network tab
3. Send a message
4. Observe:
   - Request to `/api/chat`
   - Response type: `text/event-stream`
   - Streaming data arriving
   - Response headers (Cache-Control, X-Accel-Buffering)

## Checklist for Integration Verification

### Backend
- [ ] Health check responds with status 200
- [ ] Chat endpoint accepts POST requests
- [ ] SSE streaming works and returns proper format
- [ ] Session IDs are tracked correctly
- [ ] File uploads are processed (with backend image processing configured)
- [ ] Error responses are properly formatted
- [ ] CORS headers are present in responses
- [ ] API documentation is available at `/docs`

### Frontend
- [ ] Chat widget renders without errors
- [ ] Messages display correctly
- [ ] Input field works and sends messages
- [ ] File upload button is functional
- [ ] Streaming responses display in real-time
- [ ] Loading state shows during response
- [ ] Error messages display properly
- [ ] Responsive design works on mobile

### Integration
- [ ] Frontend connects to backend successfully
- [ ] Messages sent from frontend reach backend
- [ ] Responses stream back to frontend correctly
- [ ] Session IDs persist across messages
- [ ] File uploads work end-to-end
- [ ] Clear session button resets conversation
- [ ] No console errors in browser DevTools

## Common Issues & Solutions

### Issue: CORS Error
**Symptom**: "Access to XMLHttpRequest blocked by CORS policy"
**Solution**: 
1. Verify backend CORS_ORIGINS includes frontend URL
2. Check frontend VITE_API_BASE_URL matches backend URL
3. Restart backend with proper CORS settings

### Issue: Connection Refused
**Symptom**: "Failed to fetch" when sending message
**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check port 8000 is not in use
3. Verify firewall settings

### Issue: SSE Not Streaming
**Symptom**: Messages don't stream in, appear all at once
**Solution**:
1. Check browser DevTools Network tab for SSE response type
2. Verify Content-Type header is `text/event-stream`
3. Check that response body contains `data: ` lines

### Issue: File Upload Not Working
**Symptom**: File doesn't upload or get processed
**Solution**:
1. Verify GROQ_API_KEY is set for image processing
2. Check supported file types (jpg, png, gif, webp, pdf)
3. Verify file size is reasonable
4. Check backend logs for processing errors

## Next Steps

After successful integration testing:
1. Deploy to staging environment
2. Run production smoke tests
3. Validate with real data
4. Set up monitoring and logging
5. Document any custom configurations

## Support

For testing issues or questions:
- Check backend logs: `tail -f /tmp/backend.log`
- Check browser console: F12 → Console tab
- Review PHASE_1_SETUP.md for configuration
