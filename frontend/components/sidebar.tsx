'use client'

import { useState, useEffect } from 'react'
import { useAuthStore, useChatStore, type Conversation } from '@/lib/store'
import { Plus, LogOut, MessageSquare, Trash2, ChevronDown } from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface SidebarProps {
  onClose?: () => void
}

export default function Sidebar({ onClose }: SidebarProps) {
  const { user, logout } = useAuthStore()
  const { conversations, currentConversation, setCurrentConversation, createConversation, deleteConversation } = useChatStore()
  const [groupedConversations, setGroupedConversations] = useState<Record<string, Conversation[]>>({})
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({ today: true, week: true })

  useEffect(() => {
    const grouped: Record<string, Conversation[]> = {
      today: [],
      week: [],
      month: [],
      older: [],
    }

    const now = new Date()
    conversations.forEach((conv) => {
      const daysDiff = Math.floor((now.getTime() - conv.updatedAt.getTime()) / (1000 * 60 * 60 * 24))
      if (daysDiff === 0) grouped.today.push(conv)
      else if (daysDiff < 7) grouped.week.push(conv)
      else if (daysDiff < 30) grouped.month.push(conv)
      else grouped.older.push(conv)
    })

    setGroupedConversations(grouped)
  }, [conversations])

  const handleNewChat = async () => {
    const conversation = await createConversation('New Chat')
    setCurrentConversation(conversation)
    onClose?.()
  }

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation)
    onClose?.()
  }

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    await deleteConversation(id)
  }

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [group]: !prev[group],
    }))
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-slate-800">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-900 dark:text-white font-medium hover:bg-gray-100 dark:hover:bg-slate-700 transition"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto px-2 py-4 space-y-2">
        {Object.entries(groupedConversations).map(([group, convs]) => {
          if (convs.length === 0) return null

          const labels: Record<string, string> = {
            today: 'Today',
            week: 'Last 7 Days',
            month: 'Last 30 Days',
            older: 'Older',
          }

          return (
            <div key={group}>
              <button
                onClick={() => toggleGroup(group)}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider hover:text-gray-900 dark:hover:text-gray-300 transition"
              >
                <ChevronDown
                  size={14}
                  className={`transition-transform ${expandedGroups[group] ? '' : '-rotate-90'}`}
                />
                {labels[group]}
              </button>

              {expandedGroups[group] && (
                <div className="space-y-1">
                  {convs.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv)}
                      className={`
                        w-full text-left px-3 py-2 rounded-lg text-sm transition group
                        ${currentConversation?.id === conv.id
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100'
                          : 'text-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-slate-800'}
                      `}
                    >
                      <div className="flex items-start gap-2 justify-between">
                        <div className="flex items-start gap-2 flex-1 min-w-0">
                          <MessageSquare size={14} className="flex-shrink-0 mt-1" />
                          <div className="min-w-0 flex-1">
                            <p className="truncate font-medium">{conv.title}</p>
                            <p className="text-xs opacity-70">{formatDate(conv.updatedAt)}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => handleDeleteConversation(e, conv.id)}
                          className="flex-shrink-0 p-1 opacity-0 group-hover:opacity-100 hover:text-red-600 dark:hover:text-red-400 transition"
                          aria-label="Delete conversation"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-slate-800 space-y-3">
        {user && (
          <div className="px-3 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800">
            <p className="text-xs font-semibold text-gray-900 dark:text-white truncate">{user.name}</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 truncate">{user.email}</p>
          </div>
        )}

        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition font-medium text-sm"
        >
          <LogOut size={16} />
          Sign Out
        </button>
      </div>
    </div>
  )
}
