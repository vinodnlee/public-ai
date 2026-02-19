/**
 * Renders assistant message with all AgentEvent types.
 */

import type { AgentEvent } from '../../types/agent'
import type { ChatMessage } from '../../hooks/useChat'
import { ThinkingIndicator } from './ThinkingIndicator'
import { SqlBlock } from './SqlBlock'
import { ResultTable } from './ResultTable'
import { ResultChart } from './ResultChart'

const THINKING_PAST_TENSE: Record<string, string> = {
  'Analyzing your question...': 'Analyzed your question.',
  'Generating SQL query...': 'Generated SQL query.',
  'Executing SQL on database...': 'Executed SQL on database.',
}

function thinkingLabel(content: string | undefined, isComplete: boolean): string {
  if (!content) return ''
  if (isComplete && content in THINKING_PAST_TENSE) return THINKING_PAST_TENSE[content]
  return content
}

interface AssistantMessageProps {
  message: ChatMessage
}

/** Index of the last 'result' event; only that one is rendered to avoid duplicate charts. */
function lastResultEventIndex(events: AgentEvent[]): number {
  let idx = -1
  events.forEach((e, i) => { if (e.type === 'result') idx = i })
  return idx
}

export function AssistantMessage({ message }: AssistantMessageProps) {
  const { content, events = [], isStreaming } = message
  const lastResultIdx = lastResultEventIndex(events)

  return (
    <div className="space-y-2">
      {events.map((event, i) => (
        <EventBlock
          key={i}
          event={event}
          isComplete={!isStreaming}
          showResult={event.type !== 'result' || i === lastResultIdx}
        />
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

function EventBlock({
  event,
  isComplete,
  showResult,
}: {
  event: AgentEvent
  isComplete: boolean
  showResult: boolean
}) {
  switch (event.type) {
    case 'thinking':
      return (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          {isComplete ? (
            <span className="h-2 w-2 rounded-full bg-slate-400 shrink-0" aria-hidden />
          ) : (
            <ThinkingIndicator />
          )}
          <span>{thinkingLabel(event.content ?? undefined, isComplete)}</span>
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
      if (!showResult) return null
      return event.columns && event.rows ? (
        <div className="space-y-2">
          <ResultChart columns={event.columns} rows={event.rows} />
          <ResultTable
            columns={event.columns}
            rows={event.rows}
            rowCount={event.row_count ?? event.rows.length}
          />
        </div>
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
