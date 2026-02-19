/**
 * Scrollable data table for query results.
 */

interface ResultTableProps {
  columns: string[]
  rows: Record<string, unknown>[]
  rowCount: number
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
      <div className="px-4 py-2 bg-slate-50 text-slate-600 text-xs border-t border-slate-200">
        {rowCount} row{rowCount !== 1 ? 's' : ''}
      </div>
    </div>
  )
}
