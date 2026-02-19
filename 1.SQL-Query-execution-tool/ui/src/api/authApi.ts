/**
 * Auth API and token storage. When backend has AUTH_ENABLED=true, use login and send token.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''
const TOKEN_KEY = 'deepagent_jwt'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getAuthHeaders(): Record<string, string> {
  const token = getToken()
  if (!token || token === 'disabled') return {}
  return { Authorization: `Bearer ${token}` }
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password } satisfies LoginRequest),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Login failed: ${res.status}`)
  }
  const data = (await res.json()) as TokenResponse
  setToken(data.access_token)
  return data
}

/** Append token to URL for SSE (EventSource does not support headers). */
export function withTokenInUrl(url: string): string {
  const token = getToken()
  if (!token || token === 'disabled') return url
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}token=${encodeURIComponent(token)}`
}
