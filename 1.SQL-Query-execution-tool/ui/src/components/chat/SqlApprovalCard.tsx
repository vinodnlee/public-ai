/**
 * SQL approval card — shown when stream emits interrupt (HITL).
 * User can Approve, Reject, or Edit the proposed SQL before execution.
 */

import { useState } from 'react'
import { Box, Button, Stack, TextField, Typography } from '@mui/material'
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded'
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import { SqlBlock } from './SqlBlock'

interface SqlApprovalCardProps {
  proposedSql: string
  onApprove: () => void
  onReject: () => void
  onEdit: (editedSql: string) => void
  isLoading?: boolean
}

export function SqlApprovalCard({
  proposedSql,
  onApprove,
  onReject,
  onEdit,
  isLoading = false,
}: SqlApprovalCardProps) {
  const [editMode, setEditMode] = useState(false)
  const [editedSql, setEditedSql] = useState(proposedSql)

  const handleSubmitEdit = () => {
    const trimmed = editedSql.trim()
    if (trimmed) {
      onEdit(trimmed)
      setEditMode(false)
    }
  }

  return (
    <Box
      sx={{
        mt: 1.5,
        p: 2,
        bgcolor: '#f0f9ff',
        border: '1px solid #bae6fd',
        borderRadius: 2,
      }}
    >
      <Typography variant="subtitle2" color="primary.dark" sx={{ fontWeight: 600, mb: 1 }}>
        Approve SQL before execution
      </Typography>
      {!editMode ? (
        <>
          <SqlBlock sql={proposedSql} />
          <Stack direction="row" spacing={1} sx={{ mt: 1.5, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="small"
              startIcon={<CheckCircleOutlineRoundedIcon />}
              onClick={onApprove}
              disabled={isLoading}
            >
              Approve
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<CancelOutlinedIcon />}
              onClick={onReject}
              disabled={isLoading}
            >
              Reject
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<EditOutlinedIcon />}
              onClick={() => setEditMode(true)}
              disabled={isLoading}
            >
              Edit
            </Button>
          </Stack>
        </>
      ) : (
        <>
          <TextField
            fullWidth
            multiline
            minRows={4}
            maxRows={12}
            value={editedSql}
            onChange={(e) => setEditedSql(e.target.value)}
            placeholder="Edit SQL..."
            size="small"
            sx={{
              mt: 1,
              '& .MuiInputBase-root': { fontFamily: 'monospace', fontSize: '0.875rem' },
            }}
          />
          <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
            <Button variant="contained" size="small" onClick={handleSubmitEdit} disabled={isLoading}>
              Submit & run
            </Button>
            <Button variant="outlined" size="small" onClick={() => setEditMode(false)} disabled={isLoading}>
              Cancel
            </Button>
          </Stack>
        </>
      )}
    </Box>
  )
}
