import React, { useState, useCallback } from 'react'
import CodeEditor, { SAMPLE_CODE } from './components/CodeEditor'
import OutputPanel from './components/OutputPanel'
import LanguageSelector from './components/LanguageSelector'
import PhaseViewer from './components/PhaseViewer'

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [sourceCode, setSourceCode] = useState(SAMPLE_CODE)
  const [targetLang, setTargetLang] = useState('cpp')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [phaseOpen, setPhaseOpen] = useState(true)
  const [copied, setCopied] = useState(false)

  const handleTranspile = useCallback(async () => {
    if (!sourceCode.trim()) return
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/transpile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_code: sourceCode,
          source_lang: 'python',
          target_lang: targetLang,
        }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [sourceCode, targetLang])

  const handleCopy = () => {
    if (result?.output_code) {
      navigator.clipboard.writeText(result.output_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleClear = () => {
    setSourceCode('')
    setResult(null)
    setError(null)
  }

  return (
    <div style={styles.root}>
      {/* ── Header ── */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <path d="M4 6l7-3 7 3v10l-7 3-7-3V6z" stroke="var(--accent)" strokeWidth="1.5" fill="none"/>
              <path d="M11 3v16M4 6l7 4 7-4" stroke="var(--accent)" strokeWidth="1.5"/>
            </svg>
            <span style={styles.logoText}>MultiLingual <span style={{ color: 'var(--accent)' }}>Transpiler</span></span>
          </div>
          <div style={styles.pipelinePills}>
            {['Tokenize', 'Parse', 'Analyze', 'IR', 'Codegen'].map((s, i) => (
              <React.Fragment key={s}>
                <span style={styles.phasePill}>{s}</span>
                {i < 4 && <span style={styles.phaseSep}>→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div style={styles.headerRight}>
          <LanguageSelector
            sourceLang="python"
            targetLang={targetLang}
            onTargetChange={setTargetLang}
          />

          <button onClick={handleClear} style={styles.btnSecondary}>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M2 2l9 9M11 2l-9 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Clear
          </button>

          <button
            onClick={handleTranspile}
            disabled={isLoading || !sourceCode.trim()}
            style={{ ...styles.btnPrimary, ...(isLoading ? styles.btnDisabled : {}) }}
          >
            {isLoading ? (
              <>
                <span style={styles.btnSpinner} />
                Running...
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M4 2l8 5-8 5V2z" fill="currentColor"/>
                </svg>
                Transpile
              </>
            )}
          </button>
        </div>
      </header>

      {/* ── Error Banner ── */}
      {error && (
        <div style={styles.errorBanner}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="7" r="6" stroke="var(--red)" strokeWidth="1.5"/>
            <path d="M7 4v4M7 9.5v.5" stroke="var(--red)" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span>{error}</span>
          <button onClick={() => setError(null)} style={styles.dismissBtn}>✕</button>
        </div>
      )}

      {/* ── Semantic Error Banner ── */}
      {result?.semantic_errors?.length > 0 && (
        <div style={styles.warnBanner}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1L13 12H1L7 1z" stroke="var(--yellow)" strokeWidth="1.5" fill="none"/>
            <path d="M7 5v3M7 9.5v.5" stroke="var(--yellow)" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span>{result.semantic_errors.length} semantic warning{result.semantic_errors.length > 1 ? 's' : ''} — code generated with caveats</span>
        </div>
      )}

      {/* ── Main Content ── */}
      <div style={styles.main}>
        {/* Input Panel */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <div style={styles.panelTitle}>
              <span style={{ ...styles.langDot, background: '#3b82f6' }} />
              Python Source
            </div>
            <div style={styles.panelMeta}>
              {sourceCode.split('\n').length} lines
            </div>
          </div>
          <div style={styles.editorArea}>
            <CodeEditor value={sourceCode} onChange={setSourceCode} />
          </div>
        </div>

        {/* Divider */}
        <div style={styles.divider}>
          <div style={styles.dividerLine} />
          <div style={styles.dividerIcon}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={styles.dividerLine} />
        </div>

        {/* Output Panel */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <div style={styles.panelTitle}>
              <span style={{ ...styles.langDot, background: targetLang === 'cpp' ? '#f97316' : '#eab308' }} />
              {targetLang === 'cpp' ? 'C++ Output' : 'JavaScript Output'}
            </div>
            <div style={styles.panelActions}>
              {result?.output_code && (
                <button onClick={handleCopy} style={styles.btnTiny}>
                  {copied ? (
                    <>
                      <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                        <path d="M2 5.5l2.5 2.5 4.5-5" stroke="var(--green)" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                      Copied!
                    </>
                  ) : (
                    <>
                      <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                        <rect x="4" y="1" width="6" height="7" rx="1" stroke="currentColor" strokeWidth="1"/>
                        <rect x="1" y="3" width="6" height="7" rx="1" stroke="currentColor" strokeWidth="1"/>
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
          <div style={styles.editorArea}>
            <OutputPanel
              code={result?.output_code || ''}
              targetLang={targetLang}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>

      {/* ── Phase Viewer ── */}
      <div style={{ ...styles.phasePanel, height: phaseOpen ? '280px' : '36px' }}>
        <div style={styles.phasePanelHeader} onClick={() => setPhaseOpen(v => !v)}>
          <div style={styles.phasePanelTitle}>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <rect x="1" y="1" width="11" height="11" rx="2" stroke="var(--accent)" strokeWidth="1.2"/>
              <path d="M4 4.5h5M4 6.5h3M4 8.5h4" stroke="var(--accent)" strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
            Compiler Phase Inspector
          </div>
          <div style={styles.phaseHeaderRight}>
            {result && (
              <span style={styles.phaseStatBadge}>
                {result.tokens?.length} tokens · {countNodes(result.ast)} AST nodes
              </span>
            )}
            <span style={{ ...styles.chevronIcon, transform: phaseOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}>
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3 4.5l3 3 3-3" stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </span>
          </div>
        </div>
        {phaseOpen && (
          <div style={styles.phaseContent}>
            <PhaseViewer data={result} semanticErrors={result?.semantic_errors} />
          </div>
        )}
      </div>
    </div>
  )
}

function countNodes(obj, count = 0) {
  if (!obj || typeof obj !== 'object') return count
  count++
  for (const v of Object.values(obj)) {
    if (Array.isArray(v)) v.forEach(i => { count = countNodes(i, count) })
    else if (typeof v === 'object') count = countNodes(v, count)
  }
  return count
}

const styles = {
  root: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--bg-base)',
    overflow: 'hidden',
  },

  // Header
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 16px',
    height: '52px',
    background: 'var(--bg-surface)',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
    gap: '16px',
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '20px', minWidth: 0 },
  headerRight: { display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 },
  logo: { display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 },
  logoText: { fontSize: '15px', fontWeight: 700, letterSpacing: '-0.02em', whiteSpace: 'nowrap' },
  pipelinePills: {
    display: 'flex',
    alignItems: 'center',
    gap: '3px',
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '4px 10px',
  },
  phasePill: {
    fontSize: '10px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
    letterSpacing: '0.03em',
    fontWeight: 500,
  },
  phaseSep: { fontSize: '10px', color: 'var(--border-bright)', margin: '0 2px' },

  // Buttons
  btnPrimary: {
    display: 'flex', alignItems: 'center', gap: '6px',
    background: 'var(--accent)',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '0 16px',
    height: '36px',
    fontSize: '13px',
    fontWeight: 600,
    letterSpacing: '0.02em',
    transition: 'all 0.15s',
    boxShadow: '0 0 12px var(--accent-glow)',
  },
  btnDisabled: { opacity: 0.6, cursor: 'not-allowed', boxShadow: 'none' },
  btnSecondary: {
    display: 'flex', alignItems: 'center', gap: '5px',
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '0 12px',
    height: '36px',
    fontSize: '12px',
    fontWeight: 500,
    transition: 'all 0.15s',
  },
  btnTiny: {
    display: 'flex', alignItems: 'center', gap: '4px',
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
    borderRadius: '5px',
    padding: '3px 8px',
    fontSize: '11px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  btnSpinner: {
    width: '11px', height: '11px',
    borderRadius: '50%',
    border: '1.5px solid rgba(255,255,255,0.3)',
    borderTopColor: '#fff',
    animation: 'spin 0.6s linear infinite',
    display: 'inline-block',
  },

  // Banners
  errorBanner: {
    display: 'flex', alignItems: 'center', gap: '8px',
    padding: '8px 16px',
    background: 'var(--red-dim)',
    borderBottom: '1px solid rgba(248,113,113,0.2)',
    fontSize: '12px',
    color: 'var(--red)',
    fontFamily: 'var(--font-mono)',
    flexShrink: 0,
  },
  warnBanner: {
    display: 'flex', alignItems: 'center', gap: '8px',
    padding: '8px 16px',
    background: 'var(--yellow-dim)',
    borderBottom: '1px solid rgba(251,191,36,0.2)',
    fontSize: '12px',
    color: 'var(--yellow)',
    flexShrink: 0,
  },
  dismissBtn: {
    marginLeft: 'auto', color: 'var(--red)', fontSize: '11px',
    cursor: 'pointer', background: 'none', border: 'none',
  },

  // Main editor area
  main: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden',
    minHeight: 0,
  },
  panel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    minWidth: 0,
  },
  panelHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 12px',
    height: '36px',
    background: 'var(--bg-surface)',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  panelTitle: {
    display: 'flex', alignItems: 'center', gap: '7px',
    fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)',
    letterSpacing: '0.02em',
  },
  panelMeta: { fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' },
  panelActions: { display: 'flex', gap: '6px', alignItems: 'center' },
  langDot: { width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0 },
  editorArea: { flex: 1, overflow: 'hidden', minHeight: 0 },

  // Divider
  divider: {
    width: '40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    flexShrink: 0,
    background: 'var(--bg-base)',
  },
  dividerLine: { flex: 1, width: '1px', background: 'var(--border)', maxHeight: '80px' },
  dividerIcon: {
    width: '28px', height: '28px',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: '50%',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0,
  },

  // Phase panel
  phasePanel: {
    flexShrink: 0,
    background: 'var(--bg-surface)',
    borderTop: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    transition: 'height 0.2s ease',
  },
  phasePanelHeader: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 14px',
    height: '36px',
    cursor: 'pointer',
    flexShrink: 0,
    borderBottom: '1px solid var(--border)',
    userSelect: 'none',
  },
  phasePanelTitle: {
    display: 'flex', alignItems: 'center', gap: '7px',
    fontSize: '11px', fontWeight: 600,
    color: 'var(--text-secondary)',
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  phaseHeaderRight: { display: 'flex', alignItems: 'center', gap: '10px' },
  phaseStatBadge: {
    fontSize: '10px', color: 'var(--text-muted)',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '2px 7px',
    fontFamily: 'var(--font-mono)',
  },
  chevronIcon: { transition: 'transform 0.2s ease', display: 'flex', alignItems: 'center' },
  phaseContent: { flex: 1, overflow: 'hidden', minHeight: 0 },
}
