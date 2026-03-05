'use client'

import { useState, useEffect } from 'react'
import { useAuthStore, useChatStore } from '@/lib/store'
import Sidebar from './sidebar'
import ChatWindow from './chat-window'
import AuthModal from './auth-modal'
import { Menu, X } from 'lucide-react'

export default function ChatLayout() {
  const { isAuthenticated } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024)
      if (window.innerWidth < 1024) {
        setSidebarOpen(false)
      } else {
        setSidebarOpen(true)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  if (!isAuthenticated) {
    return <AuthModal />
  }

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950 overflow-hidden">
      {/* Mobile menu button */}
      {isMobile && (
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-4 left-4 z-40 p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg lg:hidden"
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      )}

      {/* Sidebar */}
      {sidebarOpen && (
        <aside
          className={`
            fixed inset-y-0 left-0 w-64 bg-gray-50 dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800
            transform transition-transform duration-300 ease-out
            lg:static lg:translate-x-0 z-30
            ${isMobile ? 'translate-x-0' : ''}
          `}
        >
          <Sidebar onClose={() => isMobile && setSidebarOpen(false)} />
        </aside>
      )}

      {/* Mobile overlay */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main chat window */}
      <main className="flex-1 flex flex-col bg-white dark:bg-slate-950">
        <ChatWindow />
      </main>
    </div>
  )
}
