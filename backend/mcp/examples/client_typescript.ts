"""
TypeScript/JavaScript client for DNEXT MCP Server
Works in Node.js and browsers
"""

interface ChatResponse {
  status: 'success' | 'error'
  response: string
  session_id: string
  metadata?: Record<string, unknown>
}

interface SearchResult {
  chunk: string
  source: string
  relevance_score: number
  metadata?: Record<string, unknown>
}

interface SearchResponse {
  status: 'success' | 'error'
  query: string
  results: SearchResult[]
  total_results: number
}

interface FileUploadResponse {
  status: 'success' | 'error'
  file_name: string
  message: string
  details?: Record<string, unknown>
}

export class DNEXTMCPClient {
  private serverUrl: string
  private apiKey: string
  private headers: Record<string, string>

  constructor(serverUrl: string, apiKey: string) {
    this.serverUrl = serverUrl.replace(/\/$/, '')
    this.apiKey = apiKey
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    }
  }

  /**
   * Send a message to the chatbot
   * @param message User message
   * @param sessionId Optional session ID for multi-turn conversations
   */
  async sendMessage(
    message: string,
    sessionId?: string
  ): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.serverUrl}/tools/send-message`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          message,
          session_id: sessionId || 'default'
        })
      })

      if (!response.ok) {
        return {
          status: 'error',
          response: `Server error: ${response.status}`,
          session_id: sessionId || 'default'
        }
      }

      return await response.json()
    } catch (error) {
      return {
        status: 'error',
        response: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        session_id: sessionId || 'default'
      }
    }
  }

  /**
   * Upload a file to the knowledge base
   * @param file File to upload (PDF, JPG, PNG)
   * @param sessionId Optional session ID
   */
  async uploadFile(
    file: File,
    sessionId?: string
  ): Promise<FileUploadResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (sessionId) {
        formData.append('session_id', sessionId)
      }

      const response = await fetch(`${this.serverUrl}/tools/upload-file`, {
        method: 'POST',
        headers: {
          'Authorization': this.headers['Authorization']
        },
        body: formData
      })

      if (!response.ok) {
        return {
          status: 'error',
          file_name: file.name,
          message: `Server error: ${response.status}`
        }
      }

      return await response.json()
    } catch (error) {
      return {
        status: 'error',
        file_name: file.name,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }

  /**
   * Search the knowledge base
   * @param query Search query
   * @param limit Max results (1-20)
   */
  async search(
    query: string,
    limit: number = 5
  ): Promise<SearchResponse> {
    try {
      const response = await fetch(`${this.serverUrl}/tools/search`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          query,
          limit: Math.min(limit, 20)
        })
      })

      if (!response.ok) {
        return {
          status: 'error',
          query,
          results: [],
          total_results: 0
        }
      }

      return await response.json()
    } catch (error) {
      return {
        status: 'error',
        query,
        results: [],
        total_results: 0
      }
    }
  }

  /**
   * Get information about available tools
   */
  async getToolsInfo(): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(`${this.serverUrl}/tools/info`, {
        headers: this.headers
      })

      if (!response.ok) {
        return {}
      }

      return await response.json()
    } catch (error) {
      return {}
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.serverUrl}/health`)
      return response.ok
    } catch {
      return false
    }
  }
}

// Example usage
async function exampleUsage() {
  // Initialize client
  const client = new DNEXTMCPClient(
    'http://localhost:8001',
    'dnext_xxxxx' // Replace with actual API key
  )

  // Example 1: Send message
  console.log('='.repeat(60))
  console.log('Example 1: Sending a message')
  console.log('='.repeat(60))

  const chatResult = await client.sendMessage(
    'What are the main features of DNEXT?',
    'my_session_1'
  )

  console.log(`Status: ${chatResult.status}`)
  console.log(`Response: ${chatResult.response.substring(0, 200)}...`)
  console.log()

  // Example 2: Search knowledge base
  console.log('='.repeat(60))
  console.log('Example 2: Searching knowledge base')
  console.log('='.repeat(60))

  const searchResult = await client.search(
    'How to configure dashboard?',
    3
  )

  console.log(`Status: ${searchResult.status}`)
  console.log(`Found ${searchResult.total_results} results`)

  searchResult.results.forEach((result, i) => {
    console.log(`\nResult ${i + 1}:`)
    console.log(`  Score: ${result.relevance_score.toFixed(2)}`)
    console.log(`  Source: ${result.source}`)
    console.log(`  Text: ${result.chunk.substring(0, 100)}...`)
  })

  console.log()

  // Example 3: File upload (browser)
  console.log('='.repeat(60))
  console.log('Example 3: Upload file (browser only)')
  console.log('='.repeat(60))

  const fileInput = document.getElementById('fileInput') as HTMLInputElement
  if (fileInput && fileInput.files && fileInput.files.length > 0) {
    const file = fileInput.files[0]
    const uploadResult = await client.uploadFile(file, 'my_session_1')
    console.log(`Upload status: ${uploadResult.status}`)
    console.log(`Message: ${uploadResult.message}`)
  }
}

// Export for Node.js/modules
export default DNEXTMCPClient
