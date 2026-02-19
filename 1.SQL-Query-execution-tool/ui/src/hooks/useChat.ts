/**
 * useChat — manages chat state, sessions, sends messages, consumes SSE stream.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { initiateChat, openEventStream } from '../api/chatApi'
import { clearToken } from '../api/authApi'
import type { AgentEvent } from '../types/agent'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  events?: AgentEvent[]
  isStreaming?: boolean
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
}

function sessionTitle(messages: ChatMessage[]): string {
  const firstUser = messages.find((m) => m.role === 'user')
  if (!firstUser?.content?.trim()) return 'New chat'
  const t = firstUser.content.trim()
  return t.length > 32 ? t.slice(0, 32) + '…' : t
}

export interface UseChatReturn {
  sessions: ChatSession[]
  currentSessionId: string
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  authRequired: boolean
  sendMessage: (query: string) => Promise<void>
  startNewSession: () => void
  switchToSession: (sessionId: string) => void
  clearError: () => void
}

function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function useChat(): UseChatReturn {
  const initialIdRef = useRef<string | null>(null)
  if (initialIdRef.current === null) initialIdRef.current = generateSessionId()
  const initialId = initialIdRef.current

  const [sessions, setSessions] = useState<ChatSession[]>(() => [
    { id: initialId, title: 'New chat', messages: [] },
  ])
  const [currentSessionId, setCurrentSessionId] = useState<string>(initialId)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [authRequired, setAuthRequired] = useState(false)
  const sessionIdRef = useRef<string>(currentSessionId)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    sessionIdRef.current = currentSessionId
  }, [currentSessionId])

  const messages = sessions.find((s) => s.id === currentSessionId)?.messages ?? []

  const clearError = useCallback(() => {
    setError(null)
    setAuthRequired(false)
  }, [])

  const startNewSession = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setError(null)
    setIsLoading(false)
    const newId = generateSessionId()
    setSessions((prev) => [...prev, { id: newId, title: 'New chat', messages: [] }])
    setCurrentSessionId(newId)
  }, [])

  const switchToSession = useCallback((sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setError(null)
    setIsLoading(false)
    setCurrentSessionId(sessionId)
  }, [])

  const updateCurrentSessionMessages = useCallback(
    (updater: (prev: ChatMessage[]) => ChatMessage[]) => {
      setSessions((prev) =>
        prev.map((s) => {
          if (s.id !== currentSessionId) return s
          const next = updater(s.messages)
          return { ...s, messages: next, title: sessionTitle(next) }
        })
      )
    },
    [currentSessionId]
  )

  const sendMessage = useCallback(
    async (query: string) => {
      const trimmed = query.trim()
      if (!trimmed || isLoading) return

      setError(null)
      setIsLoading(true)

      const userMsg: ChatMessage = { role: 'user', content: trimmed }
      updateCurrentSessionMessages((prev) => [...prev, userMsg])
      updateCurrentSessionMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '', events: [], isStreaming: true },
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
            updateCurrentSessionMessages((prev) => {
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
        const msg = err instanceof Error ? err.message : 'Failed to send message'
        if (msg.includes('401') || msg.includes('Unauthorized')) {
          clearToken()
          setAuthRequired(true)
        }
        setError(msg)
        setIsLoading(false)
        updateCurrentSessionMessages((prev) => prev.slice(0, -1))
      }
    },
    [isLoading, updateCurrentSessionMessages]
  )

  return {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
    authRequired,
    sendMessage,
    startNewSession,
    switchToSession,
    clearError,
  }
}
