/**
 * Renders assistant message with all AgentEvent types.
 */

import type { AgentEvent } from '../../types/agent'
import type { ChatMessage } from '../../hooks/useChat'
import { ThinkingIndicator } from './ThinkingIndicator'
import { SqlBlock } from './SqlBlock'
import { ResultTable } from './ResultTable'

interface AssistantMessageProps {
  message: ChatMessage
}

export function AssistantMessage({ message }: AssistantMessageProps) {
  const { content, events = [], isStreaming } = message

  return (
    <div className="space-y-2">
      {events.map((event, i) => (
        <EventBlock key={i} event={event} />
      ))}
      {content && (
        <div className="prose prose-slate max-w-none text-slate-700">
          <p className="whitespace-pre-wrap">
            {content}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-0.5 bg-slate-500 animate-pulse align-middle" />
            )}
          </p>
        </div>
      )}
      {!content && events.length === 0 && isStreaming && (
        <ThinkingIndicator />
      )}
    </div>
  )
}

function EventBlock({ event }: { event: AgentEvent }) {
  switch (event.type) {
    case 'thinking':
      return (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <ThinkingIndicator />
          <span>{event.content}</span>
        </div>
      )
    case 'sql':
      return event.content ? <SqlBlock sql={event.content} /> : null
    case 'executing':
      return (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <span className="animate-pulse">●</span>
          <span>{event.content}</span>
        </div>
      )
    case 'result':
      return event.columns && event.rows ? (
        <ResultTable
          columns={event.columns}
          rows={event.rows}
          rowCount={event.row_count ?? event.rows.length}
        />
      ) : null
    case 'error':
      return (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-red-700 text-sm">
          {event.content}
        </div>
      )
    case 'tool_call':
      return null
    case 'token':
    case 'done':
      return null
    default:
      return null
  }
}
