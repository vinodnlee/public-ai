import type { ProgressLogEntry } from '../data/projectPlan'

export function ProgressLogTable({
  entries,
  title,
}: {
  entries: ProgressLogEntry[]
  title: string
}) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
      <header className="px-5 py-4 border-b border-[var(--border)]">
        <h2 className="font-semibold text-lg text-[var(--text)]">{title}</h2>
      </header>
      <div className="overflow-x-auto max-h-64 overflow-y-auto">
        <table className="w-full text-left">
          <thead className="sticky top-0 bg-[var(--surface)] z-10">
            <tr className="border-b border-[var(--border)]">
              <th className="px-5 py-2 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)] w-28">
                Date
              </th>
              <th className="px-5 py-2 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                Task
              </th>
              <th className="px-5 py-2 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)] w-24">
                Commit
              </th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, i) => (
              <tr
                key={`${entry.date}-${entry.commit}-${i}`}
                className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--surface-hover)] transition-colors"
              >
                <td className="px-5 py-2 font-mono text-sm text-[var(--text-muted)]">
                  {entry.date}
                </td>
                <td className="px-5 py-2 text-sm text-[var(--text)]">{entry.task}</td>
                <td className="px-5 py-2 font-mono text-xs text-emerald-400">{entry.commit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
