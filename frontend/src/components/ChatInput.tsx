/**
 * ChatInput - Message input component with file upload
 */

import React, { useRef, useState } from 'react'

export interface ChatInputProps {
  onSendMessage: (content: string, files?: File[]) => void
  isLoading: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
}) => {
  const [message, setMessage] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSendClick = () => {
    if (!message.trim() && selectedFiles.length === 0) {
      return
    }
    onSendMessage(message, selectedFiles.length > 0 ? selectedFiles : undefined)
    setMessage('')
    setSelectedFiles([])
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault()
      handleSendClick()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files))
    }
  }

  return (
    <div className="chat-input-container">
      {selectedFiles.length > 0 && (
        <div className="selected-files">
          {selectedFiles.map((file) => (
            <div key={file.name} className="file-tag">
              <span className="file-icon">📎</span>
              <span className="file-name">{file.name}</span>
              <button
                className="file-remove"
                onClick={() =>
                  setSelectedFiles(selectedFiles.filter((f) => f !== file))
                }
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="chat-input-form">
        <textarea
          className="chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Shift+Enter for new line)"
          disabled={isLoading}
          rows={1}
        />

        <div className="input-controls">
          <button
            className="file-upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            title="Upload files (images, PDFs)"
          >
            📎
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          <button
            className="send-btn"
            onClick={handleSendClick}
            disabled={isLoading || (!message.trim() && selectedFiles.length === 0)}
          >
            {isLoading ? '⏳' : '→'}
          </button>
        </div>
      </div>
    </div>
  )
}
