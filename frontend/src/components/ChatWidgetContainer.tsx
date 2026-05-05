/**
 * ChatWidgetContainer - Embeddable container component
 * Can be embedded in other applications
 */

import React from 'react'
import { ChatWidget, ChatWidgetProps } from './ChatWidget'
import '../styles/container.css'

export interface ChatWidgetContainerProps extends ChatWidgetProps {
  title?: string
  position?: 'bottom-right' | 'bottom-left' | 'full-width'
  width?: number | string
  height?: number | string
  isDocked?: boolean
  onClose?: () => void
}

export const ChatWidgetContainer: React.FC<ChatWidgetContainerProps> = ({
  title = 'DNEXT Support',
  position = 'bottom-right',
  width = 400,
  height = 600,
  isDocked = false,
  onClose,
  ...chatProps
}) => {
  const [isMinimized, setIsMinimized] = React.useState(false)

  const containerStyle: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  }

  const containerClassName = `chat-widget-container ${position} ${isMinimized ? 'minimized' : ''} ${isDocked ? 'docked' : ''}`

  return (
    <div className={containerClassName} style={containerStyle}>
      <div className="widget-header">
        <div className="widget-title">{title}</div>
        <div className="widget-controls">
          <button
            className="minimize-btn"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expand' : 'Minimize'}
          >
            {isMinimized ? '▲' : '▼'}
          </button>
          {onClose && (
            <button className="close-btn" onClick={onClose} title="Close">
              ✕
            </button>
          )}
        </div>
      </div>

      {!isMinimized && <ChatWidget {...chatProps} />}
    </div>
  )
}
