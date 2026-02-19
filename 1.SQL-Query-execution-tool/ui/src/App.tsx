import { ChatWindow } from './components/chat/ChatWindow'
import { ChatInput } from './components/chat/ChatInput'
import { useChat } from './hooks/useChat'

function App() {
  const { messages, isLoading, error, sendMessage, clearError } = useChat()

  return (
    <div className="flex flex-col h-screen bg-slate-100">
      <header className="shrink-0 px-4 py-3 bg-white border-b border-slate-200 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-800">DeepAgent SQL Chat</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Ask natural language questions — get SQL results
        </p>
      </header>

      <main className="flex-1 flex flex-col min-h-0">
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
  )
}

export default App
