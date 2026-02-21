/**
 * Text input and send button — Material UI version.
 */

import { useState, useCallback, KeyboardEvent } from 'react'
import { Box, TextField, IconButton, Tooltip, CircularProgress } from '@mui/material'
import SendRoundedIcon from '@mui/icons-material/SendRounded'

interface ChatInputProps {
  onSend: (query: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Ask a question about your data…  (Enter to send, Shift+Enter for new line)',
}: ChatInputProps) {
  const [value, setValue] = useState('')

  const handleSubmit = useCallback(() => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }, [value, disabled, onSend])

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSubmit()
      }
    },
    [handleSubmit]
  )

  const canSend = !disabled && value.trim().length > 0

  return (
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
      <TextField
        fullWidth
        multiline
        maxRows={6}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        size="small"
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            bgcolor: 'background.default',
            fontSize: '0.9rem',
          },
        }}
      />
      <Tooltip title={disabled ? 'Waiting for response…' : 'Send (Enter)'}>
        <span>
          <IconButton
            onClick={handleSubmit}
            disabled={!canSend}
            sx={{
              bgcolor: canSend ? 'primary.main' : 'action.disabledBackground',
              color: canSend ? 'white' : 'action.disabled',
              borderRadius: 2,
              p: 1.2,
              flexShrink: 0,
              transition: 'background-color 0.2s',
              '&:hover': { bgcolor: canSend ? 'primary.dark' : undefined },
            }}
          >
            {disabled ? (
              <CircularProgress size={18} color="inherit" />
            ) : (
              <SendRoundedIcon sx={{ fontSize: 18 }} />
            )}
          </IconButton>
        </span>
      </Tooltip>
    </Box>
  )
}
