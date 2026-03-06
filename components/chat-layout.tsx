'use client'

import { useState, useEffect } from 'react'
import { useAuthStore, useChatStore } from '@/lib/store'
import Sidebar from './sidebar'
import ChatWindow from './chat-window'
import AuthModal from './auth-modal'

export default function ChatLayout() {
  const user = useAuthStore((state) => state.user)
  const [showAuth, setShowAuth] = useState(!user)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    setShowAuth(!user)
  }, [user])

  if (showAuth) {
    return <AuthModal />
  }

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Chat area */}
      <ChatWindow onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
    </div>
  )
}
