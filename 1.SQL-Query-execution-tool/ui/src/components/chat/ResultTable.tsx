/**
 * Scrollable data table for query results with CSV export — Material UI version.
 */

import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  Typography,
  Button,
} from '@mui/material'
import DownloadRoundedIcon from '@mui/icons-material/DownloadRounded'

interface ResultTableProps {
  columns: string[]
  rows: Record<string, unknown>[]
  rowCount: number
}

function escapeCsvCell(value: unknown): string {
  const s = value === null || value === undefined ? '' : String(value)
  if (s.includes('"') || s.includes(',') || s.includes('\n') || s.includes('\r')) {
    return `"${s.replace(/"/g, '""')}"`
  }
  return s
}

function buildCsv(columns: string[], rows: Record<string, unknown>[]): string {
  const header = columns.map(escapeCsvCell).join(',')
  const body = rows.map((row) => columns.map((col) => escapeCsvCell(row[col])).join(','))
  return [header, ...body].join('\r\n')
}

function downloadCsv(columns: string[], rows: Record<string, unknown>[]) {
  const csv = buildCsv(columns, rows)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `query-result-${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export function ResultTable({ columns, rows, rowCount }: ResultTableProps) {
  return (
    <Paper
      elevation={0}
      sx={{ border: '1px solid', borderColor: 'divider', overflow: 'hidden', borderRadius: 2 }}
    >
      <TableContainer sx={{ maxHeight: 320 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell
                  key={col}
                  sx={{
                    fontWeight: 700,
                    fontSize: '0.7rem',
                    bgcolor: '#f8fafc',
                    color: 'text.secondary',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    whiteSpace: 'nowrap',
                    py: 1,
                    borderBottom: '2px solid',
                    borderColor: 'divider',
                  }}
                >
                  {col}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, i) => (
              <TableRow
                key={i}
                hover
                sx={{ '&:last-child td': { borderBottom: 0 } }}
              >
                {columns.map((col) => (
                  <TableCell
                    key={col}
                    sx={{ fontSize: '0.82rem', color: 'text.primary', py: 0.85 }}
                  >
                    {String(row[col] ?? '')}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Footer */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: 1.5,
          py: 0.75,
          borderTop: '1px solid',
          borderColor: 'divider',
          bgcolor: '#f8fafc',
        }}
      >
        <Typography variant="caption" color="text.secondary">
          {rowCount.toLocaleString()} row{rowCount !== 1 ? 's' : ''}
        </Typography>
        <Button
          size="small"
          startIcon={<DownloadRoundedIcon fontSize="small" />}
          onClick={() => downloadCsv(columns, rows)}
          sx={{ color: 'text.secondary', fontSize: '0.75rem', py: 0.25 }}
        >
          Export CSV
        </Button>
      </Box>
    </Paper>
  )
}
      <div className="overflow-x-auto max-h-64 overflow-y-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-100 sticky top-0">
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2 text-left font-medium text-slate-700 border-b border-slate-200"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className="border-b border-slate-100 hover:bg-slate-50"
              >
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2 text-slate-800">
                    {String(row[col] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-2 bg-slate-50 text-slate-600 text-xs border-t border-slate-200 flex items-center justify-between gap-2">
        <span>
          {rowCount} row{rowCount !== 1 ? 's' : ''}
        </span>
        <button
          type="button"
          onClick={() => downloadCsv(columns, rows)}
          className="shrink-0 px-2 py-1 rounded text-slate-600 hover:bg-slate-200 hover:text-slate-800 transition-colors"
        >
          Download CSV
        </button>
      </div>
    </div>
  )
}
