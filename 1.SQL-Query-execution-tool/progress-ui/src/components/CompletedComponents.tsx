import type { ComponentStatus } from '../data/projectPlan'

export function CompletedComponents({ components }: { components: ComponentStatus[] }) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
      <header className="px-5 py-4 border-b border-[var(--border)]">
        <h2 className="font-semibold text-lg text-[var(--text)]">Completed Components</h2>
        <p className="text-sm text-[var(--text-muted)] mt-0.5">Current status — implemented pieces</p>
      </header>
      <ul className="divide-y divide-[var(--border)] max-h-72 overflow-y-auto">
        {components.map((c) => (
          <li
            key={c.path}
            className="px-5 py-3 hover:bg-[var(--surface-hover)] transition-colors flex items-start gap-3"
          >
            <span className="shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs">
              ✓
            </span>
            <div className="min-w-0 flex-1">
              <p className="font-medium text-[var(--text)]">{c.component}</p>
              <p className="font-mono text-xs text-[var(--text-muted)]">{c.path}</p>
              {c.notes && (
                <p className="text-xs text-[var(--text-muted)] mt-0.5">{c.notes}</p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
