/**
 * AgentEvent types — match API SSE payload from DeepAgent.
 * See api/src/agent/events.py for backend definition.
 */

export type EventType =
  | 'plan'
  | 'thinking'
  | 'tool_call'
  | 'sql'
  | 'executing'
  | 'result'
  | 'answer'
  | 'error'
  | 'done'
  | 'interrupt'

export interface AgentEvent {
  type: EventType
  content?: string
  tool?: string
  input?: string
  columns?: string[]
  rows?: Record<string, unknown>[]
  row_count?: number
  /** HITL: set when type is 'interrupt' */
  proposed_sql?: string
  nl_query?: string
  thread_id?: string
}

export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  role: MessageRole
  content: string
  events?: AgentEvent[]
}
