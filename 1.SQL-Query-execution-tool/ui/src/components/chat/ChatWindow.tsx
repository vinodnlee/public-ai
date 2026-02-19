/**
 * Scrollable message list.
 */

import type { ChatMessage } from '../../hooks/useChat'
import { AssistantMessage } from './AssistantMessage'

interface ChatWindowProps {
  messages: ChatMessage[]
}

export function ChatWindow({ messages }: ChatWindowProps) {
  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-slate-500">
          <p className="text-lg">Ask a natural language question about your data.</p>
          <p className="text-sm mt-1">e.g. &quot;How many employees are in each department?&quot;</p>
        </div>
      ) : (
        messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-slate-800 text-white'
                  : 'bg-white border border-slate-200 shadow-sm'
              }`}
            >
              {msg.role === 'user' ? (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              ) : (
                <AssistantMessage message={msg} />
              )}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
