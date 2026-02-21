/**
 * Dark sidebar listing all chat sessions — Material UI Drawer version.
 */

import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Button,
  Tooltip,
} from '@mui/material'
import CloseRoundedIcon from '@mui/icons-material/CloseRounded'
import AddRoundedIcon from '@mui/icons-material/AddRounded'
import ChatBubbleOutlineRoundedIcon from '@mui/icons-material/ChatBubbleOutlineRounded'
import type { ChatSession } from '../../hooks/useChat'

const DARK_BG = '#0f172a'
const DARK_HOVER = '#1e293b'
const DARK_SELECTED = '#334155'
const DARK_BORDER = 'rgba(255,255,255,0.08)'
const SESSION_W = 260

interface SessionSidebarProps {
  isOpen: boolean
  onClose: () => void
  sessions: ChatSession[]
  currentSessionId: string
  onNewChat: () => void
  onSelectSession: (sessionId: string) => void
}

export function SessionSidebar({
  isOpen,
  onClose,
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
}: SessionSidebarProps) {
  return (
    <Drawer
      anchor="left"
      open={isOpen}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: SESSION_W,
          bgcolor: DARK_BG,
          color: '#e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          border: 'none',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 2,
          py: 1.5,
          borderBottom: `1px solid ${DARK_BORDER}`,
          flexShrink: 0,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
          <ChatBubbleOutlineRoundedIcon sx={{ color: '#6366f1', fontSize: 16 }} />
          <Typography
            variant="caption"
            sx={{
              color: '#94a3b8',
              fontSize: '0.7rem',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              fontWeight: 600,
            }}
          >
            Conversations
          </Typography>
        </Box>
        <Tooltip title="Close">
          <IconButton size="small" onClick={onClose} sx={{ color: '#475569', '&:hover': { color: '#94a3b8' } }}>
            <CloseRoundedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* New chat */}
      <Box sx={{ px: 1.5, py: 1.5, borderBottom: `1px solid ${DARK_BORDER}`, flexShrink: 0 }}>
        <Button
          fullWidth
          startIcon={<AddRoundedIcon />}
          onClick={onNewChat}
          size="small"
          variant="outlined"
          sx={{
            borderColor: DARK_BORDER,
            color: '#cbd5e1',
            borderRadius: 2,
            py: 0.75,
            '&:hover': { bgcolor: DARK_HOVER, borderColor: '#475569' },
          }}
        >
          New chat
        </Button>
      </Box>

      {/* Session list */}
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        {sessions.length === 0 ? (
          <Typography variant="body2" sx={{ p: 2.5, color: '#475569', textAlign: 'center' }}>
            No conversations yet
          </Typography>
        ) : (
          <List dense disablePadding>
            {sessions.map((session) => {
              const isActive = session.id === currentSessionId
              return (
                <ListItemButton
                  key={session.id}
                  selected={isActive}
                  onClick={() => onSelectSession(session.id)}
                  sx={{
                    px: 2,
                    py: 1,
                    color: isActive ? '#f1f5f9' : '#94a3b8',
                    borderLeft: isActive ? '3px solid #6366f1' : '3px solid transparent',
                    '&.Mui-selected': {
                      bgcolor: DARK_SELECTED,
                      color: '#f1f5f9',
                      '&:hover': { bgcolor: DARK_SELECTED },
                    },
                    '&:hover': { bgcolor: DARK_HOVER, color: '#e2e8f0' },
                    transition: 'all 0.15s ease',
                  }}
                >
                  <ListItemText
                    primary={session.title}
                    secondary={`${session.messages.length} message${session.messages.length !== 1 ? 's' : ''}`}
                    primaryTypographyProps={{
                      fontSize: '0.84rem',
                      fontWeight: isActive ? 600 : 400,
                      noWrap: true,
                    }}
                    secondaryTypographyProps={{
                      fontSize: '0.71rem',
                      color: '#475569',
                    }}
                  />
                </ListItemButton>
              )
            })}
          </List>
        )}
      </Box>
    </Drawer>
  )
}
            {/* Header */}
            <div className="shrink-0 flex items-center justify-between px-3 py-2 border-b border-slate-200 bg-slate-50">
                <h2 className="text-sm font-semibold text-slate-800">Chats</h2>
                <button
                    type="button"
                    onClick={onClose}
                    className="p-1 rounded text-slate-500 hover:bg-slate-200 hover:text-slate-700"
                    aria-label="Close session list"
                >
                    ✕
                </button>
            </div>

            {/* New chat button */}
            <div className="shrink-0 px-3 py-2 border-b border-slate-100">
                <button
                    type="button"
                    onClick={() => { onNewChat(); onClose() }}
                    className="w-full px-3 py-1.5 rounded-md text-sm font-medium text-white bg-slate-700 hover:bg-slate-800 transition-colors"
                >
                    + New chat
                </button>
            </div>

            {/* Session list */}
            <div className="flex-1 overflow-y-auto min-h-0">
                {sessions.length === 0 ? (
                    <p className="p-3 text-sm text-slate-400">No sessions yet.</p>
                ) : (
                    <ul>
                        {sessions.map((session) => {
                            const isActive = session.id === currentSessionId
                            return (
                                <li key={session.id}>
                                    <button
                                        type="button"
                                        onClick={() => { onSelectSession(session.id); onClose() }}
                                        className={`w-full text-left px-3 py-2.5 text-sm border-b border-slate-100 transition-colors ${isActive
                                                ? 'bg-slate-100 text-slate-900 font-medium'
                                                : 'text-slate-700 hover:bg-slate-50'
                                            }`}
                                    >
                                        <span className="block truncate">{session.title}</span>
                                        <span className="block text-xs text-slate-400 mt-0.5">
                                            {session.messages.length} message{session.messages.length !== 1 ? 's' : ''}
                                        </span>
                                    </button>
                                </li>
                            )
                        })}
                    </ul>
                )}
            </div>
        </div>
    )
}
