/**
 * Sidebar listing chat sessions; click to switch and continue.
 */

import type { ChatSession } from '../../hooks/useChat'

interface SessionSidebarProps {
  isOpen: boolean
  onClose: () => void
  sessions: ChatSession[]
  currentSessionId: string
  onNewChat: () => void
  onSelectSession: (sessionId: string) => void
}

export function SessionSidebar({
  isOpen,
  onClose,
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
}: SessionSidebarProps) {
  if (!isOpen) return null

  return (
    <div className="w-64 shrink-0 flex flex-col bg-white border-r border-slate-200 shadow-sm">
      <div className="shrink-0 flex items-center justify-between px-3 py-2 border-b border-slate-200 bg-slate-50">
        <h2 className="text-sm font-semibold text-slate-800">Chats</h2>
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-slate-500 hover:bg-slate-200 hover:text-slate-700"
          aria-label="Close sidebar"
        >
          <span className="sr-only">Close</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="p-2 border-b border-slate-200">
        <button
          type="button"
          onClick={() => { onNewChat(); onClose() }}
          className="w-full px-3 py-2 rounded-md text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 text-left"
        >
          + New chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto py-2">
        {sessions.length === 0 ? (
          <p className="px-3 text-sm text-slate-500">No chats yet</p>
        ) : (
          <ul className="space-y-0.5">
            {sessions.map((session) => (
              <li key={session.id}>
                <button
                  type="button"
                  onClick={() => { onSelectSession(session.id); onClose() }}
                  className={`w-full px-3 py-2 text-left text-sm rounded-md truncate ${
                    session.id === currentSessionId
                      ? 'bg-slate-200 text-slate-900 font-medium'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                  title={session.title}
                >
                  {session.title}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
