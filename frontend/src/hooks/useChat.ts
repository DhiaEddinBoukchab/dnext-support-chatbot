/**
 * useChat Hook - Manage chat state and streaming
 */

import { useState, useCallback, useRef } from 'react'
import { ChatMessage, ChatSession } from '../types'
import { apiClient } from '../api/client'

export interface UseChatOptions {
  sessionId?: string
  onStreamMessage?: (message: string) => void
  onMetadata?: (metadata: any) => void
}

export interface UseChatReturn {
  messages: ChatMessage[]
  sessionId: string
  isLoading: boolean
  error: string | null
  sendMessage: (message: string, files?: File[]) => Promise<void>
  clearSession: () => void
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessionId, setSessionId] = useState(options.sessionId || generateSessionId())
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(
    async (message: string, files?: File[]) => {
      if (!message.trim() && (!files || files.length === 0)) {
        setError('Please enter a message or select a file')
        return
      }

      // Add user message to state
      const userMessageId = generateMessageId()
      const userMessage: ChatMessage = {
        id: userMessageId,
        role: 'user',
        content: message || `[${files?.length || 0} file(s) uploaded]`,
        timestamp: new Date(),
        attachments: files?.map((f) => ({
          id: generateMessageId(),
          name: f.name,
          type: (f.type.startsWith('image') ? 'image' : 'file') as 'image' | 'file',
        })),
      }
      setMessages((prev) => [...prev, userMessage])

      setIsLoading(true)
      setError(null)

      try {
        // Stream response from API
        let assistantContent = ''
        const assistantMessageId = generateMessageId()
        let isFirstChunk = true

        if (files && files.length > 0) {
          // Use file upload endpoint
          for await (const chunk of apiClient.streamChatWithFiles(message, files, sessionId)) {
            if (chunk.type === 'response' && chunk.content) {
              assistantContent += chunk.content
              if (isFirstChunk) {
                isFirstChunk = false
                setMessages((prev) => [
                  ...prev,
                  {
                    id: assistantMessageId,
                    role: 'assistant',
                    content: assistantContent,
                    timestamp: new Date(),
                  },
                ])
              } else {
                setMessages((prev) => {
                  const updated = [...prev]
                  const lastMessage = updated[updated.length - 1]
                  if (lastMessage.id === assistantMessageId) {
                    lastMessage.content = assistantContent
                  }
                  return updated
                })
              }
              options.onStreamMessage?.(assistantContent)
            } else if (chunk.type === 'metadata' && chunk.data) {
              options.onMetadata?.(chunk.data)
            } else if (chunk.type === 'error') {
              setError(chunk.content || 'An error occurred')
            }
          }
        } else {
          // Use text-only endpoint
          for await (const chunk of apiClient.streamChat({ message, session_id: sessionId })) {
            if (chunk.type === 'response' && chunk.content) {
              assistantContent += chunk.content
              if (isFirstChunk) {
                isFirstChunk = false
                setMessages((prev) => [
                  ...prev,
                  {
                    id: assistantMessageId,
                    role: 'assistant',
                    content: assistantContent,
                    timestamp: new Date(),
                  },
                ])
              } else {
                setMessages((prev) => {
                  const updated = [...prev]
                  const lastMessage = updated[updated.length - 1]
                  if (lastMessage.id === assistantMessageId) {
                    lastMessage.content = assistantContent
                  }
                  return updated
                })
              }
              options.onStreamMessage?.(assistantContent)
            } else if (chunk.type === 'metadata' && chunk.data) {
              options.onMetadata?.(chunk.data)
            } else if (chunk.type === 'error') {
              setError(chunk.content || 'An error occurred')
            }
          }
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error'
        setError(errorMessage)
        console.error('[v0] Error sending message:', err)
      } finally {
        setIsLoading(false)
      }
    },
    [sessionId, options]
  )

  const clearSession = useCallback(() => {
    setMessages([])
    setSessionId(generateSessionId())
    setError(null)
  }, [])

  return {
    messages,
    sessionId,
    isLoading,
    error,
    sendMessage,
    clearSession,
  }
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
