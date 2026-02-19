/**
 * Animated bounce dots for "thinking" state.
 */

export function ThinkingIndicator() {
  return (
    <div className="flex gap-1" aria-label="Thinking">
      <span
        className="h-2 w-2 rounded-full bg-slate-400 animate-bounce"
        style={{ animationDelay: '0ms' }}
      />
      <span
        className="h-2 w-2 rounded-full bg-slate-400 animate-bounce"
        style={{ animationDelay: '150ms' }}
      />
      <span
        className="h-2 w-2 rounded-full bg-slate-400 animate-bounce"
        style={{ animationDelay: '300ms' }}
      />
    </div>
  )
}
