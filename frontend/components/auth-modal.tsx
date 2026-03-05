'use client'

import { useState } from 'react'
import { useAuthStore } from '@/lib/store'
import { LogIn } from 'lucide-react'

export default function AuthModal() {
  const { login, isLoading } = useAuthStore()
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !name) {
      setError('Please fill in all fields')
      return
    }

    try {
      await login(email, name)
    } catch (err) {
      setError('Failed to sign in. Please try again.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-slate-950 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 mb-4 shadow-lg">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            DNEXT Support
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            AI-Powered Customer Assistant
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@example.com"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 focus:border-transparent transition"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Full Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 focus:border-transparent transition"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-semibold hover:shadow-lg hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
          >
            {isLoading ? 'Signing In...' : 'Sign In / Sign Up'}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-6">
          This is a secure AI-powered support chatbot
        </p>
      </div>
    </div>
  )
}
