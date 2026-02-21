/**
 * Login dialog — Material UI version.
 */

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Box,
  Typography,
} from '@mui/material'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
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
    <Dialog open onClose={onCancel} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ pb: 0.5, pt: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 2,
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <LockOutlinedIcon sx={{ color: 'white', fontSize: 18 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ lineHeight: 1.2 }}>Sign in</Typography>
            <Typography variant="caption" color="text.secondary">Enter your credentials to continue</Typography>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        <Box
          component="form"
          id="login-form"
          onSubmit={handleSubmit}
          sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
        >
          {error && <Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert>}
          <TextField
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
            fullWidth
            autoFocus
            size="small"
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            fullWidth
            size="small"
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        <Button onClick={onCancel} color="inherit" variant="outlined" size="small">
          Cancel
        </Button>
        <Button
          type="submit"
          form="login-form"
          variant="contained"
          size="small"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={14} color="inherit" /> : null}
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
