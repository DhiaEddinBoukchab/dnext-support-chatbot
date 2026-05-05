/**
 * Type definitions for the chat widget
 */

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  attachments?: Attachment[]
}

export interface Attachment {
  id: string
  name: string
  type: 'image' | 'file'
  url?: string
}

export interface ChatSession {
  session_id: string
  messages: ChatMessage[]
  created_at: Date
  updated_at: Date
}

export interface ChatRequest {
  message: string
  session_id?: string
}

export interface StreamingMessage {
  type: 'response' | 'metadata' | 'error'
  content?: string
  data?: {
    session_id: string
    chunks_retrieved: number
    conversation_type: string
    response_time_ms?: number
  }
}

export interface ChatAPI {
  post(path: string, data: ChatRequest): Promise<ReadableStream<Uint8Array>>
  postWithFiles(path: string, formData: FormData): Promise<ReadableStream<Uint8Array>>
}
