'use client'

import { type Message } from '@/lib/store'
import { formatTime } from '@/lib/utils'

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`
          max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg
          ${isUser
            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-br-none'
            : 'bg-gray-100 dark:bg-slate-800 text-gray-900 dark:text-gray-100 rounded-bl-none'
          }
          animate-fade-in
        `}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </p>
        <p className={`text-xs mt-1.5 ${isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}`}>
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
