/**
 * Bar/line chart for result sets with numeric columns.
 * Renders when we have at least one category-like column and one numeric column.
 */

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Paper, Box, Typography } from '@mui/material'
import BarChartRoundedIcon from '@mui/icons-material/BarChartRounded'

interface ResultChartProps {
  columns: string[]
  rows: Record<string, unknown>[]
}

function isNumericColumn(rows: Record<string, unknown>[], col: string): boolean {
  if (rows.length === 0) return false
  return rows.every((row) => {
    const v = row[col]
    if (v === null || v === undefined) return true
    if (typeof v === 'number' && !Number.isNaN(v)) return true
    if (typeof v === 'string') {
      const n = Number(v)
      return !Number.isNaN(n)
    }
    return false
  })
}

function toNumber(v: unknown): number {
  if (typeof v === 'number') return v
  if (v === null || v === undefined) return 0
  const n = Number(v)
  return Number.isNaN(n) ? 0 : n
}

/** Return category column (first non-numeric or first column) and numeric columns. */
function getChartColumns(
  columns: string[],
  rows: Record<string, unknown>[]
): { categoryCol: string; numericCols: string[] } | null {
  const numericCols = columns.filter((col) => isNumericColumn(rows, col))
  if (numericCols.length === 0) return null
  const categoryCol =
    columns.find((col) => !numericCols.includes(col)) ?? columns[0]
  return { categoryCol, numericCols }
}

const CHART_COLORS = ['#6366f1', '#0ea5e9', '#22c55e', '#f59e0b', '#ef4444']

export function ResultChart({ columns, rows }: ResultChartProps) {
  const chartCols = getChartColumns(columns, rows)
  if (!chartCols || rows.length === 0) return null

  const { categoryCol, numericCols } = chartCols
  const data = rows.map((row) => {
    const point: Record<string, string | number> = {
      [categoryCol]: String(row[categoryCol] ?? ''),
    }
    numericCols.forEach((col) => {
      point[col] = toNumber(row[col])
    })
    return point
  })

  const maxBars = 2
  const barsToShow = numericCols.slice(0, maxBars)

  return (
    <Paper
      elevation={0}
      sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, p: 2, bgcolor: 'background.paper' }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mb: 1.5 }}>
        <BarChartRoundedIcon sx={{ fontSize: 16, color: 'primary.main' }} />
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.68rem' }}>
          Chart
        </Typography>
      </Box>
      <Box sx={{ height: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          {numericCols.length === 1 && rows.length <= 20 ? (
            <BarChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey={categoryCol}
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => (String(v).length > 12 ? `${String(v).slice(0, 10)}…` : v)}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: number) => [value, numericCols[0]]}
                labelFormatter={(label) => `${categoryCol}: ${label}`}
              />
              {barsToShow.map((col, i) => (
                <Bar
                  key={col}
                  dataKey={col}
                  fill={CHART_COLORS[i % CHART_COLORS.length]}
                  name={col}
                  radius={[2, 2, 0, 0]}
                />
              ))}
            </BarChart>
          ) : (
            <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey={categoryCol}
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => (String(v).length > 12 ? `${String(v).slice(0, 10)}…` : v)}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {barsToShow.map((col, i) => (
                <Line
                  key={col}
                  type="monotone"
                  dataKey={col}
                  stroke={CHART_COLORS[i % CHART_COLORS.length]}
                  name={col}
                  dot={{ r: 2 }}
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </Box>
    </Paper>
  )
}
