/**
 * Chat API client — initiates chat and opens SSE stream.
 * Uses relative /api paths (Vite proxy forwards to backend).
 * Sends JWT when present (auth).
 */

import type { AgentEvent } from '../types/agent'
import { getAuthHeaders, withTokenInUrl } from './authApi'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface InitiateChatRequest {
  query: string
  session_id: string
  selected_skills?: string[]
  selected_skill_dirs?: string[]
  selected_mcp_servers?: string[]
}

export interface InitiateChatResponse {
  session_id: string
  stream_url: string
}

export interface RuntimeSelection {
  selected_skills?: string[]
  selected_skill_dirs?: string[]
  selected_mcp_servers?: string[]
}

/**
 * POST /api/chat — start a chat turn, returns stream_url.
 */
export async function initiateChat(
  query: string,
  sessionId: string,
  runtimeSelection?: RuntimeSelection
): Promise<InitiateChatResponse> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
  }
  const body: InitiateChatRequest = {
    query,
    session_id: sessionId,
    ...(runtimeSelection ?? {}),
  }
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Chat init failed: ${res.status} ${text}`)
  }
  return res.json()
}

export type ApproveAction = 'approve' | 'reject' | 'edit'

export interface ApproveResponse {
  stream_url: string
}

/**
 * POST /api/chat/approve — resume after HITL interrupt; returns new stream_url.
 */
export async function approveAndResume(
  sessionId: string,
  threadId: string,
  action: ApproveAction,
  options?: { edited_sql?: string; nl_query?: string; runtimeSelection?: RuntimeSelection }
): Promise<ApproveResponse> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
  }
  const body: Record<string, unknown> = {
    thread_id: threadId,
    session_id: sessionId,
    action,
  }
  if (options?.edited_sql) body.edited_sql = options.edited_sql
  if (options?.nl_query) body.nl_query = options.nl_query
  if (options?.runtimeSelection?.selected_skills) {
    body.selected_skills = options.runtimeSelection.selected_skills
  }
  if (options?.runtimeSelection?.selected_skill_dirs) {
    body.selected_skill_dirs = options.runtimeSelection.selected_skill_dirs
  }
  if (options?.runtimeSelection?.selected_mcp_servers) {
    body.selected_mcp_servers = options.runtimeSelection.selected_mcp_servers
  }
  const res = await fetch(`${API_BASE}/api/chat/approve`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Approve failed: ${res.status} ${text}`)
  }
  return res.json()
}

/**
 * Open EventSource for stream_url and yield AgentEvents.
 * onEvent receives (event, closeStream) — call closeStream() when done (e.g. on type 'done').
 */
export function openEventStream(
  streamUrl: string,
  onEvent: (event: AgentEvent, closeStream: () => void) => void,
  onError?: (err: Event) => void
): EventSource {
  let url = streamUrl.startsWith('http') ? streamUrl : `${API_BASE}${streamUrl}`
  url = withTokenInUrl(url)
  const es = new EventSource(url)
  const closeStream = () => es.close()

  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data) as AgentEvent
      onEvent(data, closeStream)
    } catch (err) {
      console.error('Failed to parse SSE event:', err)
    }
  }

  if (onError) {
    es.onerror = onError
  }

  return es
}
