import React from 'react'
import Editor from '@monaco-editor/react'

export default function OutputPanel({ code, targetLang, isLoading }) {
  const monacoLang = targetLang === 'cpp' ? 'cpp' : 'javascript'

  if (isLoading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinnerWrap}>
          <div style={styles.spinner} />
          <div style={styles.spinnerRing} />
        </div>
        <div style={styles.loadingText}>Transpiling</div>
        <div style={styles.loadingSteps}>
          {['Tokenizing', 'Parsing AST', 'Semantic Analysis', 'Generating IR', 'Code Generation'].map((step, i) => (
            <div key={step} style={{ ...styles.step, animationDelay: `${i * 0.15}s` }}>{step}</div>
          ))}
        </div>
      </div>
    )
  }

  if (!code) {
    return (
      <div style={styles.empty}>
        <div style={styles.emptyIcon}>
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <rect x="8" y="6" width="24" height="28" rx="3" stroke="var(--border-bright)" strokeWidth="1.5"/>
            <path d="M14 14h12M14 19h8M14 24h10" stroke="var(--border-bright)" strokeWidth="1.5" strokeLinecap="round"/>
            <circle cx="29" cy="29" r="7" fill="var(--bg-panel)" stroke="var(--accent)" strokeWidth="1.5"/>
            <path d="M26.5 29h5M29 26.5v5" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
        <p style={styles.emptyTitle}>No output yet</p>
        <p style={styles.emptyHint}>Write Python code on the left and click <strong>Transpile</strong></p>
      </div>
    )
  }

  return (
    <div style={styles.editorWrap}>
      <Editor
        height="100%"
        language={monacoLang}
        value={code}
        theme="transpiler-output"
        options={{
          readOnly: true,
          fontSize: 13,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontLigatures: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          renderLineHighlight: 'gutter',
          padding: { top: 16, bottom: 16 },
          overviewRulerBorder: false,
          overviewRulerLanes: 0,
          scrollbar: { verticalScrollbarSize: 6, horizontalScrollbarSize: 6 },
          wordWrap: 'on',
          domReadOnly: true,
          contextmenu: false,
        }}
        beforeMount={monaco => {
          monaco.editor.defineTheme('transpiler-output', {
            base: 'vs-dark',
            inherit: true,
            rules: [
              { token: 'keyword', foreground: '22d3ee', fontStyle: 'bold' },
              { token: 'string', foreground: '4ade80' },
              { token: 'number', foreground: 'fb923c' },
              { token: 'comment', foreground: '4a4d62', fontStyle: 'italic' },
            ],
            colors: {
              'editor.background': '#0f1018',
              'editor.foreground': '#c8cad8',
              'editor.lineHighlightBackground': '#151620',
              'editor.selectionBackground': '#22d3ee20',
              'editorCursor.foreground': '#22d3ee',
              'editorLineNumber.foreground': '#22263a',
              'editorLineNumber.activeForeground': '#22d3ee',
            },
          })
        }}
        onMount={(editor, monaco) => {
          monaco.editor.setTheme('transpiler-output')
        }}
      />
    </div>
  )
}

const pulse = `
@keyframes pulse { 0%,100%{opacity:0.3} 50%{opacity:1} }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeSlideIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 0.6; transform: translateX(0); } }
`

if (typeof document !== 'undefined') {
  const s = document.createElement('style')
  s.textContent = pulse
  document.head.appendChild(s)
}

const styles = {
  editorWrap: { height: '100%', width: '100%', overflow: 'hidden' },
  loading: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '16px',
    background: '#0f1018',
  },
  spinnerWrap: { position: 'relative', width: '48px', height: '48px' },
  spinner: {
    position: 'absolute',
    inset: '4px',
    borderRadius: '50%',
    border: '2px solid transparent',
    borderTopColor: 'var(--cyan)',
    animation: 'spin 0.8s linear infinite',
  },
  spinnerRing: {
    position: 'absolute',
    inset: '0',
    borderRadius: '50%',
    border: '1px solid var(--border)',
  },
  loadingText: {
    color: 'var(--cyan)',
    fontFamily: 'var(--font-mono)',
    fontSize: '13px',
    fontWeight: 500,
    letterSpacing: '0.15em',
    textTransform: 'uppercase',
  },
  loadingSteps: { display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center' },
  step: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
    animation: 'fadeSlideIn 0.5s ease forwards',
    opacity: 0,
  },
  empty: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    background: '#0f1018',
  },
  emptyIcon: { opacity: 0.4, marginBottom: '4px' },
  emptyTitle: { color: 'var(--text-secondary)', fontSize: '14px', fontWeight: 500 },
  emptyHint: { color: 'var(--text-muted)', fontSize: '12px', textAlign: 'center', maxWidth: '240px', lineHeight: 1.6 },
}
