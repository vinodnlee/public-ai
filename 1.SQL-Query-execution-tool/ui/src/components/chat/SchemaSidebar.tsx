/**
 * Schema browser sidebar — Material UI Drawer version.
 */

import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  CircularProgress,
  Alert,
  Chip,
  Tooltip,
  Divider,
} from '@mui/material'
import CloseRoundedIcon from '@mui/icons-material/CloseRounded'
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined'
import { useEffect, useState } from 'react'
import {
  fetchTableList,
  fetchTableDetail,
  type TableSummary,
  type TableDetail,
} from '../../api/schemaApi'

const SCHEMA_W = 340

interface SchemaSidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function SchemaSidebar({ isOpen, onClose }: SchemaSidebarProps) {
  const [tables, setTables] = useState<TableSummary[]>([])
  const [selectedTable, setSelectedTable] = useState<TableDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isOpen) return
    setError(null)
    setLoading(true)
    fetchTableList()
      .then(setTables)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load schema'))
      .finally(() => setLoading(false))
  }, [isOpen])

  const handleSelectTable = (name: string) => {
    setError(null)
    setSelectedTable(null)
    fetchTableDetail(name)
      .then(setSelectedTable)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load table'))
  }

  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={onClose}
      PaperProps={{
        sx: { width: SCHEMA_W, display: 'flex', flexDirection: 'column' },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 2,
          py: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: '#f8fafc',
          flexShrink: 0,
        }}
      >
        <AccountTreeOutlinedIcon sx={{ color: 'primary.main', fontSize: 18 }} />
        <Typography variant="subtitle2" sx={{ flex: 1 }}>
          Database Schema
        </Typography>
        <Tooltip title="Close">
          <IconButton size="small" onClick={onClose}>
            <CloseRoundedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Body */}
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 6 }}>
            <CircularProgress size={28} />
          </Box>
        )}
        {error && (
          <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>
        )}
        {!loading && !error && (
          <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
            {/* Table list */}
            <Box
              sx={{
                width: 130,
                flexShrink: 0,
                borderRight: '1px solid',
                borderColor: 'divider',
                overflowY: 'auto',
                bgcolor: '#fafafa',
              }}
            >
              <List dense disablePadding>
                {tables.map((t) => (
                  <ListItemButton
                    key={t.name}
                    selected={selectedTable?.table === t.name}
                    onClick={() => handleSelectTable(t.name)}
                    sx={{
                      py: 0.85,
                      pl: 1.5,
                      '&.Mui-selected': {
                        bgcolor: '#ede9fe',
                        color: '#6d28d9',
                        '&:hover': { bgcolor: '#ede9fe' },
                        borderLeft: '3px solid #6366f1',
                      },
                      borderLeft: '3px solid transparent',
                    }}
                  >
                    <ListItemText
                      primary={t.display_name || t.name}
                      primaryTypographyProps={{
                        fontSize: '0.78rem',
                        fontWeight: selectedTable?.table === t.name ? 600 : 400,
                        noWrap: true,
                      }}
                      title={t.description || t.name}
                    />
                  </ListItemButton>
                ))}
              </List>
            </Box>

            {/* Column detail */}
            <Box sx={{ flex: 1, overflowY: 'auto', p: 1.5 }}>
              {selectedTable ? (
                <>
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      mb: 1.5,
                      color: 'text.secondary',
                      fontStyle: 'italic',
                    }}
                  >
                    {selectedTable.description || selectedTable.table}
                  </Typography>
                  <Divider sx={{ mb: 1.5 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                    {selectedTable.columns.map((col) => (
                      <Box
                        key={col.name}
                        sx={{
                          px: 1.25,
                          py: 0.85,
                          borderRadius: 1.5,
                          border: '1px solid',
                          borderColor: 'divider',
                          bgcolor: '#fafafa',
                          '&:hover': { bgcolor: '#f1f5f9' },
                          transition: 'background-color 0.15s',
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexWrap: 'wrap', mb: col.description || col.foreign_key ? 0.25 : 0 }}>
                          <Typography
                            variant="caption"
                            sx={{ fontWeight: 600, color: 'text.primary', fontFamily: 'monospace', fontSize: '0.78rem' }}
                          >
                            {col.display_name || col.name}
                          </Typography>
                          <Chip
                            label={col.type}
                            size="small"
                            sx={{
                              height: 16,
                              fontSize: '0.62rem',
                              bgcolor: '#ede9fe',
                              color: '#6d28d9',
                              '& .MuiChip-label': { px: 0.75 },
                            }}
                          />
                        </Box>
                        {col.foreign_key && (
                          <Typography
                            variant="caption"
                            sx={{ color: 'primary.main', display: 'block', fontSize: '0.68rem' }}
                          >
                            → {col.foreign_key.foreign_table}.{col.foreign_key.foreign_column}
                          </Typography>
                        )}
                        {col.description && (
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', fontSize: '0.68rem' }}
                          >
                            {col.description}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Box>
                </>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', pt: 4 }}>
                  <Typography variant="body2" color="text.disabled">
                    Select a table
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Box>
    </Drawer>
  )
}
