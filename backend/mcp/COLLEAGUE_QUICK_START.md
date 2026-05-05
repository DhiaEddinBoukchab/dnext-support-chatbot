# DNEXT MCP Server - Colleague Quick Start

This guide is for colleagues who want to use the DNEXT chatbot tools remotely.

## What You Need

1. **Server URL**: `http://your-domain:8001`
2. **API Key**: `dnext_xxxxxxxxxxxxx` (provided by admin)

That's it! You can now access three powerful tools:
- Chat with the DNEXT Support Chatbot
- Upload documents (PDF, images)
- Search the knowledge base

---

## Using with Python

### Install Dependencies
```bash
pip install httpx
```

### Example Code
```python
import asyncio
import httpx

async def main():
    # Configuration
    SERVER_URL = "http://your-domain:8001"
    API_KEY = "dnext_xxxxxxxxxxxxx"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Send a message
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/tools/send-message",
            json={"message": "Hello! What is DNEXT?"},
            headers=headers
        )
        result = response.json()
        print(f"Response: {result['response']}")
        
        # Search knowledge base
        response = await client.post(
            f"{SERVER_URL}/tools/search",
            json={"query": "password reset", "limit": 5},
            headers=headers
        )
        results = response.json()
        for item in results['results']:
            print(f"Found: {item['chunk'][:100]}...")

asyncio.run(main())
```

---

## Using with JavaScript/Node.js

### Install Dependencies
```bash
npm install node-fetch
```

### Example Code
```javascript
const API_KEY = "dnext_xxxxxxxxxxxxx"
const SERVER_URL = "http://your-domain:8001"

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
}

// Send message
async function sendMessage(message) {
  const response = await fetch(`${SERVER_URL}/tools/send-message`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      message: message,
      session_id: "my_session"
    })
  })
  
  const result = await response.json()
  console.log("Response:", result.response)
}

// Search knowledge base
async function search(query) {
  const response = await fetch(`${SERVER_URL}/tools/search`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      query: query,
      limit: 5
    })
  })
  
  const results = await response.json()
  results.results.forEach(item => {
    console.log(`Score: ${item.relevance_score}`)
    console.log(`Text: ${item.chunk}`)
  })
}

// Usage
sendMessage("What is DNEXT?")
search("How to configure settings?")
```

---

## Using with cURL

### Send a Message
```bash
curl -X POST http://your-domain:8001/tools/send-message \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is DNEXT?",
    "session_id": "my_session"
  }'
```

### Search Knowledge Base
```bash
curl -X POST http://your-domain:8001/tools/search \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "password reset",
    "limit": 5
  }'
```

### Upload a File
```bash
curl -X POST http://your-domain:8001/tools/upload-file \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
  -F "file=@/path/to/document.pdf" \
  -F "session_id=my_session"
```

---

## Multi-Turn Conversations

Use `session_id` to maintain context across multiple messages:

```python
SESSION_ID = "my_session_123"

# First message
response1 = await client.send_message(
    "What is DNEXT?",
    session_id=SESSION_ID
)

# Second message (chatbot remembers previous context)
response2 = await client.send_message(
    "Tell me more about its features",
    session_id=SESSION_ID
)
```

---

## Common Tasks

### Get Tool Information
```bash
curl -X GET http://your-domain:8001/tools/info \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx"
```

### Check Server Health
```bash
curl http://your-domain:8001/health
```

### Upload Multiple Files
```bash
for file in *.pdf; do
  curl -X POST http://your-domain:8001/tools/upload-file \
    -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
    -F "file=@$file"
done
```

---

## Troubleshooting

### "Invalid API Key"
- Check you're using the exact key provided by admin
- Make sure header format is: `Authorization: Bearer dnext_xxxxxxxxxxxxx`

### "Connection refused"
- Check server URL is correct
- Make sure firewall allows port 8001
- Verify server is running

### "File upload failed"
- Only `.pdf`, `.jpg`, `.jpeg`, `.png` files are supported
- File must be < 10MB
- Use correct form field name: `file`

---

## Need Help?

Contact your DNEXT administrator with:
1. Your API key (first 10 chars + ellipsis: `dnext_xxxxx...`)
2. The exact error message
3. What you were trying to do

