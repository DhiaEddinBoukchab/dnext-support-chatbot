'use client'

import { useState, useRef, useEffect } from 'react'
import { useChatStore } from '@/lib/store'
import { Send, Paperclip, Menu } from 'lucide-react'
import MessageBubble from './message-bubble'

interface ChatWindowProps {
  onToggleSidebar: () => void
}

export default function ChatWindow({ onToggleSidebar }: ChatWindowProps) {
  const activeConversationId = useChatStore((state) => state.activeConversationId)
  const conversations = useChatStore((state) => state.conversations)
  const addMessage = useChatStore((state) => state.addMessage)
  const updateConversation = useChatStore((state) => state.updateConversation)

  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId
  )

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [activeConversation?.messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() || !activeConversationId) return

    setIsLoading(true)
    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: message,
      timestamp: new Date(),
    }

    addMessage(activeConversationId, userMessage)
    setMessage('')

    try {
      // Update conversation title if it's new
      if (activeConversation?.messages.length === 0) {
        const title = message.substring(0, 30) + (message.length > 30 ? '...' : '')
        updateConversation(activeConversationId, { title })
      }

      // Call your backend API
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversationId: activeConversationId,
          message: message,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      const assistantMessage = {
        id: Date.now().toString(),
        role: 'assistant' as const,
        content: data.response || 'I apologize, I could not process your request.',
        timestamp: new Date(),
      }

      addMessage(activeConversationId, assistantMessage)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      addMessage(activeConversationId, errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  if (!activeConversationId) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Welcome back!
          </h2>
          <p className="text-muted-foreground">
            Select a conversation or start a new one
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden bg-background">
      {/* Header */}
      <div className="flex items-center gap-4 border-b border-border px-4 py-4 md:px-6">
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-2 hover:bg-muted rounded-lg transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h1 className="flex-1 font-semibold text-foreground truncate">
          {activeConversation?.title}
        </h1>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6 space-y-4">
        {activeConversation?.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">
              Start the conversation...
            </p>
          </div>
        ) : (
          activeConversation?.messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-border bg-background px-4 py-4 md:px-6">
        <form onSubmit={handleSendMessage} className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 rounded-lg border border-input bg-background px-4 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
            <button
              type="button"
              className="rounded-lg border border-input p-2 hover:bg-muted transition-colors disabled:opacity-50"
              disabled={isLoading}
            >
              <Paperclip className="h-5 w-5 text-muted-foreground" />
            </button>
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="rounded-lg bg-gradient-to-r from-primary to-secondary p-2 text-white hover:opacity-90 disabled:opacity-50 transition-all"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
