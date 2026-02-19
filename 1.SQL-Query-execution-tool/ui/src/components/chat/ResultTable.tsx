/**
 * Scrollable data table for query results with CSV export.
 */

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
  const body = rows.map((row) =>
    columns.map((col) => escapeCsvCell(row[col])).join(',')
  )
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
    <div className="my-2 rounded-lg border border-slate-200 overflow-hidden">
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
