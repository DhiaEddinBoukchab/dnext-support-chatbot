'use client'

import { type Message } from '@/lib/store'
import { formatTime } from '@/lib/utils'

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-gradient-to-r from-primary to-secondary text-white'
            : 'bg-muted text-foreground border border-border'
        }`}
      >
        <p className="text-sm leading-relaxed break-words">{message.content}</p>
        <p className={`text-xs mt-1 ${isUser ? 'text-white/70' : 'text-muted-foreground'}`}>
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
