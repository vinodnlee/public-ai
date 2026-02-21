import { useState } from 'react'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import AddCommentOutlinedIcon from '@mui/icons-material/AddCommentOutlined'
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined'
import LogoutIcon from '@mui/icons-material/Logout'
import LoginIcon from '@mui/icons-material/Login'
import StorageRoundedIcon from '@mui/icons-material/StorageRounded'
import { ChatWindow } from './components/chat/ChatWindow'
import { ChatInput } from './components/chat/ChatInput'
import { SchemaSidebar } from './components/chat/SchemaSidebar'
import { SessionSidebar } from './components/chat/SessionSidebar'
import { LoginForm } from './components/chat/LoginForm'
import { useChat } from './hooks/useChat'
import { getToken, clearToken } from './api/authApi'

const APPBAR_H = 64

function App() {
  const muiTheme = useTheme()
  const isDesktop = useMediaQuery(muiTheme.breakpoints.up('md'))
  const {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
    sendMessage,
    startNewSession,
    switchToSession,
    clearError,
    authRequired,
  } = useChat()

  const [sessionListOpen, setSessionListOpen] = useState(false)
  const [schemaOpen, setSchemaOpen] = useState(false)
  const [loginOpen, setLoginOpen] = useState(false)
  const token = getToken()
  const showLoginForm = loginOpen || (authRequired && !token)

  const handleNewChat = () => {
    startNewSession()
    setSessionListOpen(false)
  }

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>

      {/* ── AppBar ───────────────────────────────────────────────────── */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          bgcolor: '#0f172a',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          zIndex: (t) => t.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ gap: 0.5, minHeight: `${APPBAR_H}px !important` }}>
          <Tooltip title="Conversations">
            <IconButton
              color="inherit"
              onClick={() => setSessionListOpen((o) => !o)}
              sx={{ mr: 0.5, color: sessionListOpen ? 'primary.light' : 'inherit' }}
            >
              <MenuIcon />
            </IconButton>
          </Tooltip>

          <StorageRoundedIcon sx={{ color: '#818cf8', mr: 1, fontSize: 22 }} />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ color: 'white', letterSpacing: '-0.02em', lineHeight: 1.2, fontSize: '1rem' }}>
              DeepAgent SQL Chat
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b', display: { xs: 'none', sm: 'block' } }}>
              Natural language → SQL results
            </Typography>
          </Box>

          <Tooltip title="New chat">
            <IconButton color="inherit" onClick={handleNewChat}>
              <AddCommentOutlinedIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title={schemaOpen ? 'Hide schema' : 'Database schema'}>
            <IconButton
              color="inherit"
              onClick={() => setSchemaOpen((o) => !o)}
              sx={{ color: schemaOpen ? 'primary.light' : 'inherit' }}
            >
              <AccountTreeOutlinedIcon />
            </IconButton>
          </Tooltip>

          {token && token !== 'disabled' ? (
            <Tooltip title="Log out">
              <IconButton color="inherit" onClick={() => { clearToken(); setLoginOpen(false) }}>
                <LogoutIcon />
              </IconButton>
            </Tooltip>
          ) : (
            <Tooltip title="Log in">
              <IconButton color="inherit" onClick={() => setLoginOpen(true)}>
                <LoginIcon />
              </IconButton>
            </Tooltip>
          )}
        </Toolbar>
      </AppBar>

      {/* ── Session Drawer ───────────────────────────────────────────── */}
      <SessionSidebar
        isOpen={sessionListOpen}
        onClose={() => setSessionListOpen(false)}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={(id) => {
          switchToSession(id)
          if (!isDesktop) setSessionListOpen(false)
        }}
      />

      {/* ── Schema Drawer ────────────────────────────────────────────── */}
      <SchemaSidebar isOpen={schemaOpen} onClose={() => setSchemaOpen(false)} />

      {/* ── Main content ─────────────────────────────────────────────── */}
      <Box
        component="main"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          flexGrow: 1,
          height: '100vh',
          pt: `${APPBAR_H}px`,
          overflow: 'hidden',
          bgcolor: 'background.default',
        }}
      >
        <ChatWindow messages={messages} />

        {/* Input bar */}
        <Box
          sx={{
            flexShrink: 0,
            px: 2,
            py: 1.5,
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Box sx={{ maxWidth: 860, mx: 'auto' }}>
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </Box>
        </Box>
      </Box>

      {/* ── Login Dialog ─────────────────────────────────────────────── */}
      {showLoginForm && (
        <LoginForm
          onSuccess={() => { setLoginOpen(false); clearError() }}
          onCancel={() => { setLoginOpen(false); clearToken() }}
          errorMessage={authRequired ? 'Session expired. Please log in.' : undefined}
        />
      )}

      {/* ── Error Snackbar ───────────────────────────────────────────── */}
      <Snackbar
        open={!!error && !authRequired}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        onClose={clearError}
        autoHideDuration={6000}
      >
        <Alert severity="error" onClose={clearError} variant="filled" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default App
