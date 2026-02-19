/**
 * Syntax-highlighted SQL code block.
 */

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface SqlBlockProps {
  sql: string
}

export function SqlBlock({ sql }: SqlBlockProps) {
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 bg-slate-900 my-2">
      <SyntaxHighlighter
        language="sql"
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '0.75rem 1rem',
          fontSize: '0.875rem',
          background: 'transparent',
        }}
        showLineNumbers={false}
        PreTag="pre"
        codeTagProps={{ className: 'font-mono' }}
      >
        {sql}
      </SyntaxHighlighter>
    </div>
  )
}
