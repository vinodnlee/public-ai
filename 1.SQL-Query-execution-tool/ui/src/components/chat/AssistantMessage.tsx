/**
 * Renders assistant message with all AgentEvent types — Material UI version.
 */

import { Box, Paper, Typography, Chip, Stack } from '@mui/material'
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded'
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded'
import type { AgentEvent } from '../../types/agent'
import type { ChatMessage } from '../../hooks/useChat'
import { ThinkingIndicator } from './ThinkingIndicator'
import { SqlBlock } from './SqlBlock'
import { ResultTable } from './ResultTable'
import { ResultChart } from './ResultChart'

const THINKING_PAST: Record<string, string> = {
  'Analyzing your question...': 'Analyzed question',
  'Generating SQL query...': 'Generated SQL',
  'Executing SQL on database...': 'Executed query',
}

function thinkingLabel(content: string | undefined, isDone: boolean): string {
  if (!content) return ''
  return isDone && content in THINKING_PAST ? THINKING_PAST[content] : content
}

function lastResultIdx(events: AgentEvent[]): number {
  let idx = -1
  events.forEach((e, i) => { if (e.type === 'result') idx = i })
  return idx
}

interface AssistantMessageProps {
  message: ChatMessage
}

export function AssistantMessage({ message }: AssistantMessageProps) {
  const { content, events = [], isStreaming } = message
  const lastResult = lastResultIdx(events)

  return (
    <Paper
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: '4px 16px 16px 16px',
        p: 2,
        bgcolor: 'background.paper',
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      }}
    >
      <Stack spacing={1.5}>
        {events.map((event, i) => (
          <EventBlock
            key={i}
            event={event}
            isComplete={!isStreaming}
            showResult={event.type !== 'result' || i === lastResult}
          />
        ))}

        {content && (
          <Typography
            variant="body1"
            sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.75, color: 'text.primary' }}
          >
            {content}
            {isStreaming && (
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: 2,
                  height: '1em',
                  ml: 0.5,
                  bgcolor: 'primary.main',
                  verticalAlign: 'text-bottom',
                  animation: 'cursorBlink 1s step-end infinite',
                  '@keyframes cursorBlink': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0 },
                  },
                }}
              />
            )}
          </Typography>
        )}

        {!content && events.length === 0 && isStreaming && <ThinkingIndicator />}
      </Stack>
    </Paper>
  )
}

function EventBlock({
  event,
  isComplete,
  showResult,
}: {
  event: AgentEvent
  isComplete: boolean
  showResult: boolean
}) {
  switch (event.type) {
    case 'thinking':
      return isComplete ? (
        <Chip
          icon={<CheckCircleOutlineRoundedIcon />}
          label={thinkingLabel(event.content ?? undefined, true)}
          size="small"
          variant="outlined"
          sx={{
            alignSelf: 'flex-start',
            height: 24,
            borderColor: 'divider',
            color: 'text.secondary',
            fontSize: '0.75rem',
            '& .MuiChip-icon': { color: 'success.main', fontSize: 14 },
          }}
        />
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ThinkingIndicator />
          <Typography variant="caption" color="text.secondary">
            {thinkingLabel(event.content ?? undefined, false)}
          </Typography>
        </Box>
      )

    case 'sql':
      return event.content ? <SqlBlock sql={event.content} /> : null

    case 'executing':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              animation: 'execPulse 1.5s ease-in-out infinite',
              '@keyframes execPulse': {
                '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                '50%': { opacity: 0.3, transform: 'scale(0.85)' },
              },
            }}
          />
          <Typography variant="caption" color="text.secondary">
            {event.content}
          </Typography>
        </Box>
      )

    case 'result':
      if (!showResult) return null
      return event.columns && event.rows ? (
        <Stack spacing={1.5}>
          <ResultChart columns={event.columns} rows={event.rows} />
          <ResultTable
            columns={event.columns}
            rows={event.rows}
            rowCount={event.row_count ?? event.rows.length}
          />
        </Stack>
      ) : null

    case 'error':
      return (
        <Box
          sx={{
            display: 'flex',
            gap: 1,
            alignItems: 'flex-start',
            bgcolor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: 1.5,
            p: 1.5,
          }}
        >
          <ErrorOutlineRoundedIcon sx={{ color: 'error.main', fontSize: 18, mt: 0.1, flexShrink: 0 }} />
          <Typography variant="body2" color="error.main">
            {event.content}
          </Typography>
        </Box>
      )

    default:
      return null
  }
}
  }
}
