#!/bin/bash
# cURL Examples for DNEXT MCP Server (No Authentication)
# Usage: bash curl_examples.sh

BASE_URL="http://localhost:8001"

echo "===== DNEXT MCP Server - cURL Examples ====="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "   Command: curl $BASE_URL/health"
echo "   Response:"
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. Get Tools Info
echo "2. Get Available Tools"
echo "   Command: curl $BASE_URL/tools/info"
echo "   Response:"
curl -s "$BASE_URL/tools/info" | jq .
echo ""

# 3. Send Message
echo "3. Send a Message"
echo "   Command:"
echo '   curl -X POST $BASE_URL/tools/send-message \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"message\": \"What is DNEXT?\"}"'
echo "   Response:"
curl -s -X POST "$BASE_URL/tools/send-message" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is DNEXT?"}' | jq .
echo ""

# 4. Search Knowledge Base
echo "4. Search Knowledge Base"
echo "   Command:"
echo '   curl -X POST $BASE_URL/tools/search \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"query\": \"DNEXT features\", \"limit\": 3}"'
echo "   Response:"
curl -s -X POST "$BASE_URL/tools/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "DNEXT features", "limit": 3}' | jq .
echo ""

# 5. Upload File
echo "5. Upload a File"
echo "   Command (requires a PDF file):"
echo '   curl -X POST $BASE_URL/tools/upload-file \'
echo '     -F "file=@/path/to/document.pdf" \'
echo '     -F "session_id=my-session"'
echo ""
echo "   Example with dummy file:"

# Create a test file if jq is available
if command -v echo &> /dev/null; then
    echo "   (Skipping actual upload - provide your own PDF file)"
fi
echo ""

echo "===== Examples Summary ====="
echo "• No API key required"
echo "• Server URL: $BASE_URL"
echo "• All endpoints return JSON"
echo "• Use 'jq' for pretty JSON output"
echo ""
echo "Tools available:"
echo "  - POST /tools/send-message    : Send message to chatbot"
echo "  - POST /tools/upload-file     : Upload PDF/image"
echo "  - POST /tools/search          : Search knowledge base"
echo "  - GET  /tools/info            : Get tools information"
echo "  - GET  /health                : Health check"
