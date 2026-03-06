'use client'

import { useState, useEffect } from 'react'
import { useAuthStore, useChatStore, type Conversation } from '@/lib/store'
import { Plus, LogOut, MessageSquare, Trash2, ChevronDown, X } from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const conversations = useChatStore((state) => state.conversations)
  const activeConversationId = useChatStore((state) => state.activeConversationId)
  const setActiveConversation = useChatStore((state) => state.setActiveConversation)
  const deleteConversation = useChatStore((state) => state.deleteConversation)
  const addConversation = useChatStore((state) => state.addConversation)

  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    Today: true,
    Yesterday: true,
    'Last 7 days': true,
    'Last 30 days': true,
  })

  const groupedConversations = groupConversations(conversations)

  const handleNewChat = () => {
    const newConv: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      createdAt: new Date(),
      updatedAt: new Date(),
      messages: [],
    }
    addConversation(newConv)
    if (onClose) onClose()
  }

  const handleDeleteConversation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    deleteConversation(id)
  }

  const handleLogout = () => {
    logout()
    if (onClose) onClose()
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-border bg-card transition-transform md:relative md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border p-4">
          <h2 className="font-semibold text-foreground">Conversations</h2>
          <button
            onClick={onClose}
            className="md:hidden p-1 hover:bg-muted rounded"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* New chat button */}
        <button
          onClick={handleNewChat}
          className="m-4 flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-white hover:opacity-90 transition-all"
        >
          <Plus className="h-5 w-5" />
          New Chat
        </button>

        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto">
          {Object.entries(groupedConversations).map(([group, convs]) => (
            <div key={group} className="border-t border-border first:border-t-0">
              <button
                onClick={() =>
                  setExpandedGroups((prev) => ({
                    ...prev,
                    [group]: !prev[group],
                  }))
                }
                className="flex w-full items-center gap-2 px-4 py-3 text-sm font-medium text-muted-foreground hover:bg-muted"
              >
                <ChevronDown
                  className={`h-4 w-4 transition-transform ${
                    expandedGroups[group] ? '' : '-rotate-90'
                  }`}
                />
                {group}
              </button>

              {expandedGroups[group] && (
                <div className="space-y-1 px-2">
                  {convs.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => {
                        setActiveConversation(conv.id)
                        if (onClose) onClose()
                      }}
                      className={`group flex items-center gap-2 rounded px-3 py-2 cursor-pointer transition-all ${
                        activeConversationId === conv.id
                          ? 'bg-primary text-white'
                          : 'hover:bg-muted text-foreground'
                      }`}
                    >
                      <MessageSquare className="h-4 w-4 flex-shrink-0" />
                      <span className="flex-1 truncate text-sm">{conv.title}</span>
                      <button
                        onClick={(e) => handleDeleteConversation(e, conv.id)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 className="h-4 w-4 hover:text-destructive" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* User section */}
        {user && (
          <div className="border-t border-border p-4 space-y-3">
            <div className="text-sm">
              <p className="font-medium text-foreground truncate">{user.name}</p>
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-all"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        )}
      </div>
    </>
  )
}

function groupConversations(
  conversations: Conversation[]
): Record<string, Conversation[]> {
  const grouped: Record<string, Conversation[]> = {
    Today: [],
    Yesterday: [],
    'Last 7 days': [],
    'Last 30 days': [],
    Older: [],
  }

  const now = new Date()
  conversations.forEach((conv) => {
    const date = new Date(conv.createdAt)
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      grouped.Today.push(conv)
    } else if (diffDays === 1) {
      grouped.Yesterday.push(conv)
    } else if (diffDays <= 7) {
      grouped['Last 7 days'].push(conv)
    } else if (diffDays <= 30) {
      grouped['Last 30 days'].push(conv)
    } else {
      grouped.Older.push(conv)
    }
  })

  return Object.fromEntries(
    Object.entries(grouped).filter(([_, convs]) => convs.length > 0)
  )
}
