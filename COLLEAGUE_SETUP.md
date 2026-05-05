# What COLLEAGUES Need to Do (Users)

## Overview
Your colleague set up an MCP server with access to a chatbot. You can use 3 tools:
1. **Send Message** - Chat with the bot
2. **Upload File** - Add documents (PDF, images)
3. **Search KB** - Search the knowledge base

**No setup required!** Just pick your preferred method below.

---

## Before You Start

Ask your colleague for:
```
Server URL: http://....:8001
(Examples: http://192.168.1.100:8001 or http://your-domain.com:8001)
```

---

## Option 1: Python (Easiest & Most Features)

### Requirements
- Python 3.8+
- Internet connection

### Steps

**1. Create a script file** `chatbot_client.py`:

```python
import requests
import sys

class MCPClient:
    def __init__(self, server_url):
        self.url = server_url
    
    def send_message(self, message, session_id=None):
        """Chat with the bot"""
        data = {"message": message}
        if session_id:
            data["session_id"] = session_id
        
        response = requests.post(
            f"{self.url}/tools/send-message",
            json=data
        )
        return response.json()
    
    def search(self, query):
        """Search knowledge base"""
        response = requests.post(
            f"{self.url}/tools/search",
            json={"query": query}
        )
        return response.json()
    
    def upload_file(self, file_path):
        """Upload a PDF or image"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.url}/tools/upload",
                files=files
            )
        return response.json()

# Usage
if __name__ == "__main__":
    # Replace with server URL from colleague
    client = MCPClient("http://192.168.1.100:8001")
    
    # Send a message
    result = client.send_message("What is DNEXT?")
    print("Bot response:", result['response'])
    
    # Search
    results = client.search("help")
    print("Search results:", results)
```

**2. Install requests library**:
```bash
pip install requests
```

**3. Run it**:
```bash
python chatbot_client.py
```

---

## Option 2: Command Line (cURL)

### Requirements
- curl (comes with most systems)
- Command line/terminal

### Steps

**Send a message:**
```bash
curl -X POST http://YOUR-SERVER:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is DNEXT?"}'
```

**Search knowledge base:**
```bash
curl -X POST http://YOUR-SERVER:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "help"}'
```

**Upload a file:**
```bash
curl -X POST http://YOUR-SERVER:8001/tools/upload \
  -F "file=@/path/to/document.pdf"
```

Replace `http://YOUR-SERVER:8001` with the URL your colleague gave you.

---

## Option 3: JavaScript (Browser or Node.js)

### For Node.js:

**1. Create `client.js`:**

```javascript
const axios = require('axios');

const serverURL = 'http://192.168.1.100:8001'; // Ask colleague for this

async function sendMessage(message) {
  try {
    const response = await axios.post(`${serverURL}/tools/send-message`, {
      message: message
    });
    console.log('Response:', response.data.response);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

async function search(query) {
  try {
    const response = await axios.post(`${serverURL}/tools/search`, {
      query: query
    });
    console.log('Results:', response.data.results);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Use it
sendMessage('Hello! Can you help?');
search('documentation');
```

**2. Install axios:**
```bash
npm install axios
```

**3. Run:**
```bash
node client.js
```

### For Browser:

```html
<html>
<body>
  <h1>DNEXT Chatbot</h1>
  <input id="message" placeholder="Type a message...">
  <button onclick="send()">Send</button>
  <div id="response"></div>

  <script>
    const SERVER = 'http://192.168.1.100:8001'; // Ask colleague
    
    async function send() {
      const msg = document.getElementById('message').value;
      const res = await fetch(`${SERVER}/tools/send-message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      document.getElementById('response').innerHTML = data.response;
    }
  </script>
</body>
</html>
```

---

## Option 4: Postman or Insomnia (GUI)

### Steps

1. **Download** Postman or Insomnia (free)
2. **Create new POST request** to:
   ```
   http://YOUR-SERVER:8001/tools/send-message
   ```
3. **Set headers:**
   ```
   Content-Type: application/json
   ```
4. **Set body (JSON):**
   ```json
   {
     "message": "What is DNEXT?"
   }
   ```
5. **Click Send**

Done! You'll see the response.

---

## Common Responses

### Send Message Response:
```json
{
  "response": "DNEXT is a support chatbot...",
  "session_id": "sess_123",
  "chunks_retrieved": 3,
  "response_time_ms": 1200
}
```

### Search Response:
```json
{
  "results": [
    {
      "content": "DNEXT helps with...",
      "score": 0.92,
      "source": "documentation.pdf"
    }
  ],
  "count": 1
}
```

### Upload Response:
```json
{
  "file_name": "document.pdf",
  "chunks_created": 15,
  "status": "success"
}
```

---

## Troubleshooting

### "Connection refused"
- Ask colleague if server is running
- Check the server URL is correct
- Make sure you're on same network (or use domain name)

### "Invalid JSON"
- Check your JSON format (use a JSON validator)
- Make sure all quotes are correct

### "File not found" (upload)
- Check the file path is correct
- Use full path: `/Users/name/Documents/file.pdf`

### "Server error"
- Ask colleague to check backend is running
- Wait a moment and try again
- Check server logs

---

## Tips

1. **Save the server URL** somewhere safe so you don't forget it
2. **Test with a simple message first** to confirm connection works
3. **Use a session_id** if you want multi-turn conversations
4. **Upload PDFs** first, then search them

---

## That's It!

You now have access to:
✅ Chat with DNEXT bot  
✅ Upload documents  
✅ Search knowledge base  

Pick your preferred method above and start using!

Need help? Ask your colleague (the server owner).
