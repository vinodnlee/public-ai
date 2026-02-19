/**
 * Inline login form for JWT. Shown when auth is required (401) or user clicks Login.
 */

import { useState } from 'react'
import { login } from '../../api/authApi'

interface LoginFormProps {
  onSuccess: () => void
  onCancel: () => void
  errorMessage?: string
}

export function LoginForm({ onSuccess, onCancel, errorMessage }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(errorMessage ?? null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(username, password)
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-2 p-3 rounded-lg bg-slate-100 border border-slate-200"
    >
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="px-3 py-2 rounded border border-slate-300 text-sm"
        autoComplete="username"
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="px-3 py-2 rounded border border-slate-300 text-sm"
        autoComplete="current-password"
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="px-3 py-1.5 rounded bg-slate-800 text-white text-sm font-medium disabled:opacity-50"
        >
          {loading ? '…' : 'Log in'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 rounded border border-slate-300 text-slate-700 text-sm"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
