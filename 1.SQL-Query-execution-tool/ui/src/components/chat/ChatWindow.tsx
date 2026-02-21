/**
 * Scrollable message list — Material UI version.
 */

import { useEffect, useRef } from 'react'
import { Box, Typography, Stack } from '@mui/material'
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined'
import type { ChatMessage } from '../../hooks/useChat'
import { AssistantMessage } from './AssistantMessage'

interface ChatWindowProps {
  messages: ChatMessage[]
}

export function ChatWindow({ messages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <Box sx={{ flex: 1, overflowY: 'auto', p: { xs: 2, md: 3 }, display: 'flex', flexDirection: 'column' }}>
      {messages.length === 0 ? (
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
            color: 'text.secondary',
            textAlign: 'center',
            p: 4,
          }}
        >
          <QuestionAnswerOutlinedIcon sx={{ fontSize: 60, opacity: 0.2, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 400, color: 'text.secondary' }}>
            Ask a question about your data
          </Typography>
          <Typography variant="body2" color="text.disabled">
            e.g. &quot;How many employees are in each department?&quot;
          </Typography>
        </Box>
      ) : (
        <Stack spacing={2.5} sx={{ maxWidth: 860, width: '100%', mx: 'auto' }}>
          {messages.map((msg, i) => (
            <Box
              key={i}
              sx={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}
            >
              {msg.role === 'user' ? (
                <Box
                  sx={{
                    maxWidth: '72%',
                    bgcolor: 'primary.main',
                    color: 'primary.contrastText',
                    borderRadius: '18px 18px 4px 18px',
                    px: 2.5,
                    py: 1.5,
                    boxShadow: '0 1px 4px rgba(99,102,241,0.25)',
                  }}
                >
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.65 }}>
                    {msg.content}
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ maxWidth: '85%', width: '100%' }}>
                  <AssistantMessage message={msg} />
                </Box>
              )}
            </Box>
          ))}
          <div ref={bottomRef} />
        </Stack>
      )}
    </Box>
  )
}
