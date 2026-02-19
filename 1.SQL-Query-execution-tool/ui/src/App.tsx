import { useState } from 'react'
import { ChatWindow } from './components/chat/ChatWindow'
import { ChatInput } from './components/chat/ChatInput'
import { SchemaSidebar } from './components/chat/SchemaSidebar'
import { SessionSidebar } from './components/chat/SessionSidebar'
import { LoginForm } from './components/chat/LoginForm'
import { useChat } from './hooks/useChat'
import { getToken, clearToken } from './api/authApi'

function App() {
  const {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
    sendMessage,
    startNewSession,
    switchToSession,
    clearError,
    authRequired,
  } = useChat()
  const [sessionListOpen, setSessionListOpen] = useState(false)
  const [schemaOpen, setSchemaOpen] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const token = getToken()
  const displayLogin = showLogin || (authRequired && !token)

  return (
    <div className="flex flex-col h-screen bg-slate-100">
      <header className="shrink-0 px-4 py-3 bg-white border-b border-slate-200 shadow-sm flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">DeepAgent SQL Chat</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Ask natural language questions — get SQL results
          </p>
        </div>
        <div className="flex items-center gap-2">
          {displayLogin ? (
            <LoginForm
              onSuccess={() => { setShowLogin(false); clearError() }}
              onCancel={() => { setShowLogin(false); clearToken() }}
              errorMessage={authRequired ? 'Please log in.' : undefined}
            />
          ) : (
            <>
              {token && token !== 'disabled' ? (
                <button
                  type="button"
                  onClick={() => { clearToken(); setShowLogin(false) }}
                  className="px-2 py-1 rounded text-slate-500 hover:bg-slate-100 text-sm"
                >
                  Log out
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowLogin(true)}
                  className="px-2 py-1 rounded text-slate-600 hover:bg-slate-100 text-sm"
                >
                  Log in
                </button>
              )}
              <button
                type="button"
                onClick={() => setSessionListOpen((o) => !o)}
                className="shrink-0 px-3 py-1.5 rounded-md text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200"
              >
                Chats
              </button>
              <button
                type="button"
                onClick={startNewSession}
                className="shrink-0 px-3 py-1.5 rounded-md text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200"
              >
                New chat
              </button>
              <button
                type="button"
                onClick={() => setSchemaOpen((o) => !o)}
                className="shrink-0 px-3 py-1.5 rounded-md text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200"
              >
                {schemaOpen ? 'Hide' : 'Show'} schema
              </button>
            </>
          )}
        </div>
      </header>

      <div className="flex-1 flex min-h-0">
        <SessionSidebar
          isOpen={sessionListOpen}
          onClose={() => setSessionListOpen(false)}
          sessions={sessions}
          currentSessionId={currentSessionId}
          onNewChat={startNewSession}
          onSelectSession={switchToSession}
        />
        <SchemaSidebar isOpen={schemaOpen} onClose={() => setSchemaOpen(false)} />
        <main className="flex-1 flex flex-col min-h-0 min-w-0">
          <ChatWindow messages={messages} />
        <div className="shrink-0 p-4 border-t border-slate-200 bg-white">
          {error && (
            <div className="mb-2 flex items-center justify-between rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-red-700 text-sm">
              <span>{error}</span>
              <button
                type="button"
                onClick={clearError}
                className="text-red-600 hover:text-red-800 font-medium"
              >
                Dismiss
              </button>
            </div>
          )}
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
        </main>
      </div>
    </div>
  )
}

export default App
