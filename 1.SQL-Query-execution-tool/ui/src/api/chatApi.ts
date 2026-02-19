/**
 * Chat API client — initiates chat and opens SSE stream.
 * Uses relative /api paths (Vite proxy forwards to backend).
 */

import type { AgentEvent } from '../types/agent'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface InitiateChatRequest {
  query: string
  session_id: string
}

export interface InitiateChatResponse {
  session_id: string
  stream_url: string
}

/**
 * POST /api/chat — start a chat turn, returns stream_url.
 */
export async function initiateChat(
  query: string,
  sessionId: string
): Promise<InitiateChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId } satisfies InitiateChatRequest),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Chat init failed: ${res.status} ${text}`)
  }
  return res.json()
}

/**
 * Open EventSource for stream_url and yield AgentEvents.
 * Caller must close the EventSource when done.
 */
export function openEventStream(
  streamUrl: string,
  onEvent: (event: AgentEvent) => void,
  onError?: (err: Event) => void
): EventSource {
  const url = streamUrl.startsWith('http') ? streamUrl : `${API_BASE}${streamUrl}`
  const es = new EventSource(url)

  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data) as AgentEvent
      onEvent(data)
    } catch (err) {
      console.error('Failed to parse SSE event:', err)
    }
  }

  if (onError) {
    es.onerror = onError
  }

  return es
}
