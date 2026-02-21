/**
 * Animated thinking dots — Material UI version.
 */

import { Box } from '@mui/material'

export function ThinkingIndicator() {
  return (
    <Box sx={{ display: 'flex', gap: 0.6, alignItems: 'center' }} aria-label="Thinking">
      {[0, 150, 300].map((delay) => (
        <Box
          key={delay}
          sx={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            bgcolor: 'primary.light',
            opacity: 0.7,
            animation: 'muiThinkBounce 1.4s infinite ease-in-out both',
            animationDelay: `${delay}ms`,
            '@keyframes muiThinkBounce': {
              '0%, 80%, 100%': { transform: 'scale(0)', opacity: 0.2 },
              '40%': { transform: 'scale(1)', opacity: 0.9 },
            },
          }}
        />
      ))}
    </Box>
  )
}
