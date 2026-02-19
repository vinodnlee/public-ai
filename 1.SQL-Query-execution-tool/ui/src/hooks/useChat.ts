/**
 * useChat — manages chat state, sends messages, consumes SSE stream.
 */

import { useCallback, useRef, useState } from 'react'
import { initiateChat, openEventStream } from '../api/chatApi'
import type { AgentEvent } from '../types/agent'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  events?: AgentEvent[]
  isStreaming?: boolean
}

export interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendMessage: (query: string) => Promise<void>
  clearError: () => void
}

function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sessionIdRef = useRef<string>(generateSessionId())
  const eventSourceRef = useRef<EventSource | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const sendMessage = useCallback(async (query: string) => {
    const trimmed = query.trim()
    if (!trimmed || isLoading) return

    setError(null)
    setIsLoading(true)

    // Append user message
    const userMsg: ChatMessage = { role: 'user', content: trimmed }
    setMessages((prev) => [...prev, userMsg])

    // Placeholder for assistant — we'll stream into it
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: '',
        events: [],
        isStreaming: true,
      },
    ])

    try {
      const { stream_url } = await initiateChat(trimmed, sessionIdRef.current)
      const events: AgentEvent[] = []
      let textContent = ''

      const es = openEventStream(
        stream_url,
        (event, closeStream) => {
          events.push(event)
          if (event.type === 'token' && event.content) {
            textContent += event.content
          }
          if (event.type === 'done') {
            closeStream()
            eventSourceRef.current = null
            setIsLoading(false)
          }
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (last?.role === 'assistant') {
              next[next.length - 1] = {
                ...last,
                content: textContent,
                events: [...events],
                isStreaming: event.type !== 'done',
              }
            }
            return next
          })
        },
        () => {
          eventSourceRef.current = null
          setIsLoading(false)
        }
      )
      eventSourceRef.current = es
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
      setIsLoading(false)
      setMessages((prev) => prev.slice(0, -1))
    }
  }, [isLoading, messages.length])

  return { messages, isLoading, error, sendMessage, clearError }
}
