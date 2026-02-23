import type { Phase, TaskStatus } from '../data/projectPlan'

const statusConfig: Record<TaskStatus, { label: string; className: string }> = {
  done: { label: 'Done', className: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' },
  partial: { label: 'Partial', className: 'bg-amber-500/20 text-amber-400 border-amber-500/40' },
  todo: { label: 'Todo', className: 'bg-slate-500/20 text-slate-400 border-slate-500/40' },
}

export function PhaseCard({ phase }: { phase: Phase }) {
  const doneCount = phase.tasks.filter((t) => t.status === 'done').length
  const total = phase.tasks.length
  const progressPct = total ? Math.round((doneCount / total) * 100) : 0

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
      <header className="px-5 py-4 border-b border-[var(--border)] flex items-center justify-between gap-4">
        <div>
          <h2 className="font-semibold text-lg text-[var(--text)]">{phase.title}</h2>
          {phase.goal && (
            <p className="text-sm text-[var(--text-muted)] mt-1 max-w-2xl">{phase.goal}</p>
          )}
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="font-mono text-sm text-[var(--text-muted)]">
            {doneCount}/{total}
          </span>
          <div className="w-24 h-2 rounded-full bg-[var(--border)] overflow-hidden">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </header>
      <ul className="divide-y divide-[var(--border)]">
        {phase.tasks.map((task) => {
          const cfg = statusConfig[task.status]
          return (
            <li
              key={task.id}
              className="px-5 py-3 flex items-start gap-4 hover:bg-[var(--surface-hover)] transition-colors"
            >
              <span
                className={`shrink-0 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${cfg.className}`}
              >
                {task.id}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-[var(--text)]">{task.description}</p>
                {task.files && (
                  <p className="font-mono text-xs text-[var(--text-muted)] mt-1 truncate" title={task.files}>
                    {task.files}
                  </p>
                )}
                {task.notes && (
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">{task.notes}</p>
                )}
              </div>
              <span className={`shrink-0 text-xs ${cfg.className}`}>{cfg.label}</span>
            </li>
          )
        })}
      </ul>
      {phase.deliverable && (
        <footer className="px-5 py-3 border-t border-[var(--border)] bg-[var(--surface-hover)]/50">
          <p className="text-sm text-[var(--text-muted)]">
            <span className="font-medium text-[var(--text)]">Deliverable:</span> {phase.deliverable}
          </p>
        </footer>
      )}
    </section>
  )
}
