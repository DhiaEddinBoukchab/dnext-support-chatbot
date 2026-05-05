import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChatWidgetContainer } from './components/ChatWidgetContainer'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChatWidgetContainer
      title="DNEXT Support Assistant"
      position="full-width"
      apiUrl={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
    />
  </React.StrictMode>,
)
