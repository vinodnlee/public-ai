import type { ArchitectureRow } from '../data/projectPlan'

const statusBadge: Record<ArchitectureRow['status'], string> = {
  done: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
  partial: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
  todo: 'bg-slate-500/20 text-slate-400 border-slate-500/40',
}

export function ArchitectureTable({ rows }: { rows: ArchitectureRow[] }) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
      <header className="px-5 py-4 border-b border-[var(--border)]">
        <h2 className="font-semibold text-lg text-[var(--text)]">Architecture Overview</h2>
        <p className="text-sm text-[var(--text-muted)] mt-0.5">4 layers — components and status</p>
      </header>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-[var(--border)]">
              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                Layer
              </th>
              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                Components
              </th>
              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)] w-28">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.layer}
                className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--surface-hover)] transition-colors"
              >
                <td className="px-5 py-3 font-medium text-[var(--text)]">{row.layer}</td>
                <td className="px-5 py-3 text-sm text-[var(--text-muted)]">{row.components}</td>
                <td className="px-5 py-3">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border capitalize ${statusBadge[row.status]}`}
                  >
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
