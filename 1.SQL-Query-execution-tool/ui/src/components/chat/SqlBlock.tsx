/**
 * Syntax-highlighted SQL code block — Material UI version.
 */

import { useState } from 'react'
import { Paper, Box, Typography, IconButton, Tooltip } from '@mui/material'
import ContentCopyRoundedIcon from '@mui/icons-material/ContentCopyRounded'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface SqlBlockProps {
  sql: string
}

export function SqlBlock({ sql }: SqlBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Paper
      elevation={0}
      sx={{
        my: 1,
        overflow: 'hidden',
        border: '1px solid rgba(255,255,255,0.06)',
        bgcolor: '#1e293b',
        borderRadius: 2,
      }}
    >
      {/* Header bar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 1.5,
          py: 0.5,
          bgcolor: '#0f172a',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <Typography
          variant="caption"
          sx={{ color: '#64748b', fontFamily: 'monospace', letterSpacing: '0.06em', fontSize: '0.7rem' }}
        >
          SQL
        </Typography>
        <Tooltip title={copied ? 'Copied!' : 'Copy SQL'}>
          <IconButton size="small" onClick={handleCopy} sx={{ color: copied ? '#4ade80' : '#64748b', p: 0.5 }}>
            {copied ? <CheckRoundedIcon sx={{ fontSize: 14 }} /> : <ContentCopyRoundedIcon sx={{ fontSize: 14 }} />}
          </IconButton>
        </Tooltip>
      </Box>

      <SyntaxHighlighter
        language="sql"
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '0.75rem 1rem',
          fontSize: '0.85rem',
          background: 'transparent',
          lineHeight: 1.6,
        }}
        showLineNumbers={false}
        PreTag="pre"
        codeTagProps={{ className: 'font-mono' }}
      >
        {sql}
      </SyntaxHighlighter>
    </Paper>
  )
}
