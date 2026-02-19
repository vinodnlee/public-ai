/**
 * Sidebar showing database tables and columns (schema browser).
 */

import { useEffect, useState } from 'react'
import {
  fetchTableList,
  fetchTableDetail,
  type TableSummary,
  type TableDetail,
} from '../../api/schemaApi'

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

  if (!isOpen) return null

  return (
    <div className="w-72 shrink-0 flex flex-col bg-white border-r border-slate-200 shadow-sm">
      <div className="shrink-0 flex items-center justify-between px-3 py-2 border-b border-slate-200 bg-slate-50">
        <h2 className="text-sm font-semibold text-slate-800">Schema</h2>
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-slate-500 hover:bg-slate-200 hover:text-slate-700"
          aria-label="Close schema"
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-y-auto min-h-0">
        {loading && (
          <div className="p-3 text-slate-500 text-sm">Loading tables…</div>
        )}
        {error && (
          <div className="p-3 text-red-600 text-sm">{error}</div>
        )}
        {!loading && !error && (
          <div className="flex">
            <ul className="shrink-0 w-32 border-r border-slate-100 py-2">
              {tables.map((t) => (
                <li key={t.name}>
                  <button
                    type="button"
                    onClick={() => handleSelectTable(t.name)}
                    className={`w-full text-left px-3 py-1.5 text-sm truncate block ${
                      selectedTable?.table === t.name
                        ? 'bg-slate-200 font-medium text-slate-800'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                    title={t.description || t.name}
                  >
                    {t.display_name || t.name}
                  </button>
                </li>
              ))}
            </ul>
            <div className="flex-1 py-2 px-3 overflow-y-auto min-w-0">
              {selectedTable ? (
                <>
                  <div className="text-xs text-slate-500 mb-1">
                    {selectedTable.description || selectedTable.table}
                  </div>
                  <ul className="space-y-1">
                    {selectedTable.columns.map((col) => (
                      <li
                        key={col.name}
                        className="text-xs border-b border-slate-100 pb-1 last:border-0"
                      >
                        <span className="font-medium text-slate-800">
                          {col.display_name || col.name}
                        </span>
                        <span className="text-slate-500 ml-1">{col.type}</span>
                        {col.foreign_key && (
                          <span className="text-slate-400 ml-1">
                            → {col.foreign_key.foreign_table}.{col.foreign_key.foreign_column}
                          </span>
                        )}
                        {col.description && (
                          <div className="text-slate-500 mt-0.5 truncate">
                            {col.description}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="text-slate-400 text-sm">Select a table</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
