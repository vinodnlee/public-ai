/**
 * Schema browser API — list tables and get table details.
 * Sends JWT when present (auth).
 */

import { getAuthHeaders } from './authApi'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface TableSummary {
  name: string
  display_name: string
  description: string
  has_semantic: boolean
}

export interface ColumnInfo {
  name: string
  type: string
  nullable: string
  default: unknown
  display_name: string
  description: string
  is_sensitive: boolean
  example_values: string[]
  foreign_key?: { column: string; foreign_table: string; foreign_column: string }
}

export interface TableDetail {
  table: string
  display_name: string
  description: string
  columns: ColumnInfo[]
  common_queries: string[]
  joins: string[]
}

export async function fetchTableList(): Promise<TableSummary[]> {
  const res = await fetch(`${API_BASE}/api/schema`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`Schema list failed: ${res.status}`)
  return res.json()
}

export async function fetchTableDetail(tableName: string): Promise<TableDetail> {
  const res = await fetch(
    `${API_BASE}/api/schema/${encodeURIComponent(tableName)}`,
    { headers: getAuthHeaders() }
  )
  if (!res.ok) throw new Error(`Schema table failed: ${res.status}`)
  return res.json()
}
