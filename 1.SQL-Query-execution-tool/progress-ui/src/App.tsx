import { useState } from 'react'
import {
  partIPhases,
  partIIPhases,
  architectureRows,
  completedComponents,
  progressLogPartI,
  progressLogPartII,
} from './data/projectPlan'
import { PhaseCard } from './components/PhaseCard'
import { ArchitectureTable } from './components/ArchitectureTable'
import { ProgressLogTable } from './components/ProgressLogTable'
import { CompletedComponents } from './components/CompletedComponents'

type Tab = 'overview' | 'part1' | 'part2' | 'log'

function countDone(phases: typeof partIPhases) {
  return phases.reduce((acc, p) => acc + p.tasks.filter((t) => t.status === 'done').length, 0)
}

function countTotal(phases: typeof partIPhases) {
  return phases.reduce((acc, p) => acc + p.tasks.length, 0)
}

const part1Done = countDone(partIPhases)
const part1Total = countTotal(partIPhases)
const part2Done = countDone(partIIPhases)
const part2Total = countTotal(partIIPhases)
const totalDone = part1Done + part2Done
const totalTasks = part1Total + part2Total
const overallPct = totalTasks ? Math.round((totalDone / totalTasks) * 100) : 0

export default function App() {
  const [tab, setTab] = useState<Tab>('overview')

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'part1', label: 'Part I (Phases 1–4)' },
    { id: 'part2', label: 'Part II (A–D)' },
    { id: 'log', label: 'Progress Log' },
  ]

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <header className="sticky top-0 z-20 border-b border-[var(--border)] bg-[var(--bg)]/95 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-semibold text-[var(--text)]">
            DeepAgent SQL Chat — Project Progress
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">
            Task progress dashboard from PROJECT_PLAN.md
          </p>
          <div className="flex items-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 rounded-full bg-[var(--border)] overflow-hidden">
                <div
                  className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                  style={{ width: `${overallPct}%` }}
                />
              </div>
              <span className="font-mono text-sm text-[var(--text-muted)]">
                {totalDone}/{totalTasks} ({overallPct}%)
              </span>
            </div>
            <nav className="flex gap-1">
              {tabs.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    tab === t.id
                      ? 'bg-[var(--surface)] text-[var(--text)] border border-[var(--border)]'
                      : 'text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)]'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {tab === 'overview' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
                <h3 className="text-sm font-medium text-[var(--text-muted)]">Part I (Phases 1–4)</h3>
                <p className="mt-1 text-2xl font-semibold text-[var(--text)]">
                  {part1Done} / {part1Total} tasks
                </p>
                <div className="mt-2 h-2 rounded-full bg-[var(--border)] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${part1Total ? (part1Done / part1Total) * 100 : 0}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
                <h3 className="text-sm font-medium text-[var(--text-muted)]">Part II (Phases A–D)</h3>
                <p className="mt-1 text-2xl font-semibold text-[var(--text)]">
                  {part2Done} / {part2Total} tasks
                </p>
                <div className="mt-2 h-2 rounded-full bg-[var(--border)] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${part2Total ? (part2Done / part2Total) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
            <ArchitectureTable rows={architectureRows} />
            <CompletedComponents components={completedComponents} />
          </>
        )}

        {tab === 'part1' && (
          <div className="space-y-6">
            {partIPhases.map((phase) => (
              <PhaseCard key={phase.id} phase={phase} />
            ))}
          </div>
        )}

        {tab === 'part2' && (
          <div className="space-y-6">
            {partIIPhases.map((phase) => (
              <PhaseCard key={phase.id} phase={phase} />
            ))}
          </div>
        )}

        {tab === 'log' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProgressLogTable entries={progressLogPartI} title="Progress Log — Part I" />
            <ProgressLogTable entries={progressLogPartII} title="Progress Log — Part II" />
          </div>
        )}
      </main>
    </div>
  )
}
