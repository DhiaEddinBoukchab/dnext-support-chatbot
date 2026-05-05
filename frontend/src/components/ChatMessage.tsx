/**
 * ChatMessage - Individual message component
 */

import React from 'react'
import { ChatMessage as ChatMessageType } from '../types'

export interface ChatMessageProps {
  message: ChatMessageType
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const messageClass = isUser ? 'user-message' : 'assistant-message'

  return (
    <div className={`chat-message ${messageClass}`}>
      <div className="message-content">
        {message.attachments && message.attachments.length > 0 && (
          <div className="attachments">
            {message.attachments.map((attachment) => (
              <div key={attachment.id} className="attachment">
                {attachment.type === 'image' ? (
                  <>
                    <span className="attachment-icon">🖼️</span>
                    <span className="attachment-name">{attachment.name}</span>
                  </>
                ) : (
                  <>
                    <span className="attachment-icon">📎</span>
                    <span className="attachment-name">{attachment.name}</span>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
        <p>{message.content}</p>
      </div>
      <span className="message-time">
        {message.timestamp.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>
    </div>
  )
}
