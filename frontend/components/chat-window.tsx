'use client'

import { useState, useRef, useEffect } from 'react'
import { useChatStore } from '@/lib/store'
import { Send, Paperclip, Settings } from 'lucide-react'
import MessageBubble from './message-bubble'

export default function ChatWindow() {
  const { currentConversation, messages, isLoading, addMessage, setIsLoading } = useChatStore()
  const [input, setInput] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() && files.length === 0) return

    // Add user message
    const userMessage = {
      id: Math.random().toString(36).substr(2, 9),
      conversationId: currentConversation?.id || '',
      role: 'user' as const,
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput('')
    setFiles([])
    setIsLoading(true)

    try {
      // Call backend API to get response
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversationId: currentConversation?.id,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        const botMessage = {
          id: Math.random().toString(36).substr(2, 9),
          conversationId: currentConversation?.id || '',
          role: 'assistant' as const,
          content: data.response,
          timestamp: new Date(),
        }
        addMessage(botMessage)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  if (!currentConversation) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="mb-4 p-4 rounded-2xl bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30">
          <svg className="w-12 h-12 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m0 0h6" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Start a new conversation</h2>
        <p className="text-gray-600 dark:text-gray-400">Select or create a chat from the sidebar to begin</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex-shrink-0 px-6 py-4 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-950">
        <div>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">{currentConversation.title}</h1>
          <p className="text-xs text-gray-600 dark:text-gray-400">AI-Powered Support Assistant</p>
        </div>
        <button className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition">
          <Settings size={20} className="text-gray-600 dark:text-gray-400" />
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <p className="text-center text-gray-600 dark:text-gray-400">
              No messages yet. Start the conversation!
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <div className="flex gap-1">
              <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-pulse" />
              <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-pulse delay-100" />
              <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-pulse delay-200" />
            </div>
            <span className="text-sm">Assistant is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 px-6 py-4 border-t border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950">
        {files.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {files.map((file) => (
              <div
                key={file.name}
                className="px-3 py-2 rounded-lg bg-gray-100 dark:bg-slate-800 text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2"
              >
                <Paperclip size={14} />
                {file.name}
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleSendMessage} className="flex gap-3">
          <label className="flex items-center justify-center p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg cursor-pointer transition">
            <Paperclip size={20} className="text-gray-600 dark:text-gray-400" />
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              aria-label="Attach files"
            />
          </label>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 focus:border-transparent transition disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={isLoading || (!input.trim() && files.length === 0)}
            className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 text-white hover:shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition"
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </form>

        <p className="text-xs text-gray-600 dark:text-gray-400 text-center mt-2">
          Press Enter to send • Attach files for document analysis
        </p>
      </div>
    </div>
  )
}
