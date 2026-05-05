/**
 * ChatWidget - Main chat interface component
 */

import React, { useRef, useEffect, useState } from 'react'
import { useChat } from '../hooks/useChat'
import { ChatMessage as ChatMessageType } from '../types'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import '../styles/widget.css'

export interface ChatWidgetProps {
  sessionId?: string
  apiUrl?: string
  onLoadingChange?: (isLoading: boolean) => void
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  sessionId,
  apiUrl,
  onLoadingChange,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, isLoading, error, sendMessage, clearSession } = useChat({
    sessionId,
  })

  useEffect(() => {
    onLoadingChange?.(isLoading)
  }, [isLoading, onLoadingChange])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = (content: string, files?: File[]) => {
    sendMessage(content, files)
  }

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <h2>DNEXT Support Assistant</h2>
        <button
          className="clear-btn"
          onClick={clearSession}
          title="Clear conversation"
        >
          ↻
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>Welcome to DNEXT Support!</p>
            <p>Ask me anything about your dashboard or features.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))
        )}
        {isLoading && (
          <div className="chat-message assistant-message loading">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <p>{error}</p>
        </div>
      )}

      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  )
}
