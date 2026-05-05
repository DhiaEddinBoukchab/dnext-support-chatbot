/**
 * API Client for communicating with the DNEXT backend
 */

import { ChatRequest, StreamingMessage } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export class ChatAPIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Send a chat message and stream the response
   */
  async *streamChat(request: ChatRequest) {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Handle Server-Sent Events stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i]
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6)) as StreamingMessage
              yield data
            } catch (e) {
              console.error('[v0] Failed to parse SSE message:', e)
            }
          }
        }

        buffer = lines[lines.length - 1]
      }

      // Process any remaining buffer
      if (buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.substring(6)) as StreamingMessage
          yield data
        } catch (e) {
          console.error('[v0] Failed to parse final SSE message:', e)
        }
      }
    } catch (error) {
      console.error('[v0] Error in streamChat:', error)
      yield {
        type: 'error',
        content: error instanceof Error ? error.message : 'Unknown error',
      } as StreamingMessage
    }
  }

  /**
   * Send a chat message with file attachments
   */
  async *streamChatWithFiles(
    message: string,
    files: File[],
    sessionId?: string
  ) {
    try {
      const formData = new FormData()
      formData.append('message', message)
      if (sessionId) {
        formData.append('session_id', sessionId)
      }
      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await fetch(`${this.baseUrl}/api/chat/with-files`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Handle Server-Sent Events stream (same as above)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i]
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6)) as StreamingMessage
              yield data
            } catch (e) {
              console.error('[v0] Failed to parse SSE message:', e)
            }
          }
        }

        buffer = lines[lines.length - 1]
      }

      // Process any remaining buffer
      if (buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.substring(6)) as StreamingMessage
          yield data
        } catch (e) {
          console.error('[v0] Failed to parse final SSE message:', e)
        }
      }
    } catch (error) {
      console.error('[v0] Error in streamChatWithFiles:', error)
      yield {
        type: 'error',
        content: error instanceof Error ? error.message : 'Unknown error',
      } as StreamingMessage
    }
  }
}

export const apiClient = new ChatAPIClient()
