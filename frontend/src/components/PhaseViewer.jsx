import React, { useState } from 'react'

const PHASES = [
  { id: 'tokens', label: 'Tokens', icon: '①', desc: 'Lexical Analysis', color: '#7c6af7' },
  { id: 'ast',    label: 'AST',    icon: '②', desc: 'Syntax Analysis',  color: '#22d3ee' },
  { id: 'semantic', label: 'Semantic', icon: '③', desc: 'Semantic Analysis', color: '#4ade80' },
  { id: 'ir',     label: 'IR',     icon: '④', desc: 'Intermediate Repr', color: '#fb923c' },
]

export default function PhaseViewer({ data, semanticErrors }) {
  const [activePhase, setActivePhase] = useState('tokens')

  if (!data) {
    return (
      <div style={styles.empty}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Run transpiler to see compiler phases</span>
      </div>
    )
  }

  const renderContent = () => {
    switch (activePhase) {
      case 'tokens': return <TokenView tokens={data.tokens} />
      case 'ast':    return <JsonTree data={data.ast} />
      case 'semantic': return <SemanticView errors={data.semantic_errors} symbols={data.symbol_table} fns={data.functions} />
      case 'ir':     return <JsonTree data={data.ir} />
      default: return null
    }
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.tabs}>
        {PHASES.map(phase => (
          <button
            key={phase.id}
            onClick={() => setActivePhase(phase.id)}
            style={{
              ...styles.tab,
              ...(activePhase === phase.id ? { ...styles.tabActive, borderColor: phase.color, color: phase.color } : {})
            }}
          >
            <span style={styles.tabIcon}>{phase.icon}</span>
            <span>{phase.label}</span>
            {phase.id === 'semantic' && semanticErrors?.length > 0 && (
              <span style={styles.errorBadge}>{semanticErrors.length}</span>
            )}
          </button>
        ))}
      </div>
      <div style={styles.content}>
        {renderContent()}
      </div>
    </div>
  )
}

function TokenView({ tokens }) {
  const typeColors = {
    KEYWORD: '#7c6af7', IDENTIFIER: '#e8eaf0', NUMBER: '#fb923c', FLOAT: '#fb923c',
    STRING: '#4ade80', EQUALS: '#22d3ee', PLUS: '#22d3ee', MINUS: '#22d3ee',
    STAR: '#22d3ee', SLASH: '#22d3ee', NEWLINE: '#2a2d3e', LPAREN: '#fbbf24',
    RPAREN: '#fbbf24', COLON: '#8b8fa8', COMMA: '#8b8fa8',
  }

  return (
    <div style={styles.tokenGrid}>
      <div style={styles.tokenHeader}>
        <span style={styles.col}>TYPE</span>
        <span style={styles.col}>VALUE</span>
        <span style={styles.colSmall}>LINE</span>
        <span style={styles.colSmall}>COL</span>
      </div>
      <div style={styles.tokenRows}>
        {tokens.map((t, i) => (
          <div key={i} style={styles.tokenRow}>
            <span style={{ ...styles.col, color: typeColors[t.type] || '#8b8fa8', fontWeight: 500 }}>
              {t.type}
            </span>
            <span style={{ ...styles.col, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
              {t.value === '\\n' ? <span style={{ color: 'var(--text-muted)' }}>↵</span> : t.value}
            </span>
            <span style={{ ...styles.colSmall, color: 'var(--text-muted)' }}>{t.line}</span>
            <span style={{ ...styles.colSmall, color: 'var(--text-muted)' }}>{t.col}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SemanticView({ errors, symbols, fns }) {
  return (
    <div style={styles.semWrap}>
      <div style={styles.semSection}>
        <div style={styles.semTitle}>
          <span style={{ color: errors.length > 0 ? 'var(--red)' : 'var(--green)' }}>
            {errors.length > 0 ? '✗' : '✓'}
          </span>
          {' '}Errors ({errors.length})
        </div>
        {errors.length === 0
          ? <div style={styles.successMsg}>No semantic errors found</div>
          : errors.map((e, i) => (
              <div key={i} style={styles.errorItem}>
                <span style={styles.errorDot}>●</span> {e.error}
              </div>
            ))
        }
      </div>

      <div style={styles.semSection}>
        <div style={styles.semTitle}>Symbol Table ({symbols?.length || 0})</div>
        <div style={styles.tagCloud}>
          {(symbols || []).map(s => (
            <span key={s} style={styles.tag}>{s}</span>
          ))}
        </div>
      </div>

      <div style={styles.semSection}>
        <div style={styles.semTitle}>Functions</div>
        {Object.keys(fns || {}).length === 0
          ? <div style={styles.muted}>No user-defined functions</div>
          : Object.entries(fns).map(([name, arity]) => (
              <div key={name} style={styles.fnItem}>
                <span style={styles.fnName}>{name}</span>
                <span style={styles.fnArity}>{arity} param{arity !== 1 ? 's' : ''}</span>
              </div>
            ))
        }
      </div>
    </div>
  )
}

function JsonTree({ data }) {
  return (
    <div style={styles.jsonWrap}>
      <pre style={styles.json}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}

const styles = {
  wrapper: { height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  empty: {
    height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  tabs: {
    display: 'flex',
    gap: '2px',
    padding: '8px 12px 0',
    background: 'var(--bg-surface)',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  tab: {
    display: 'flex', alignItems: 'center', gap: '5px',
    padding: '6px 12px',
    borderRadius: '6px 6px 0 0',
    fontSize: '12px',
    color: 'var(--text-muted)',
    background: 'transparent',
    border: '1px solid transparent',
    borderBottom: 'none',
    fontFamily: 'var(--font-ui)',
    fontWeight: 500,
    transition: 'all 0.15s',
    cursor: 'pointer',
    position: 'relative',
    bottom: '-1px',
  },
  tabActive: {
    background: 'var(--bg-panel)',
    borderColor: 'var(--border)',
    borderBottomColor: 'var(--bg-panel)',
  },
  tabIcon: { fontSize: '10px', opacity: 0.7 },
  errorBadge: {
    background: 'var(--red)',
    color: '#000',
    borderRadius: '9999px',
    fontSize: '9px',
    fontWeight: 700,
    padding: '0 5px',
    lineHeight: '14px',
  },
  content: { flex: 1, overflow: 'hidden', background: 'var(--bg-panel)' },
  // Token view
  tokenGrid: { height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  tokenHeader: {
    display: 'flex', gap: '0',
    padding: '6px 12px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-elevated)',
    flexShrink: 0,
  },
  tokenRows: { flex: 1, overflowY: 'auto', padding: '4px 0' },
  tokenRow: {
    display: 'flex', gap: '0',
    padding: '3px 12px',
    borderBottom: '1px solid rgba(42,45,62,0.5)',
    fontSize: '12px',
    fontFamily: 'var(--font-mono)',
    lineHeight: '1.6',
  },
  col: { flex: 2, fontSize: '11px', letterSpacing: '0.02em', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' },
  colSmall: { flex: 1, fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' },
  // Semantic view
  semWrap: { height: '100%', overflowY: 'auto', padding: '12px' },
  semSection: { marginBottom: '20px' },
  semTitle: { fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: '8px' },
  successMsg: { fontSize: '12px', color: 'var(--green)', fontFamily: 'var(--font-mono)' },
  errorItem: { fontSize: '12px', color: 'var(--red)', fontFamily: 'var(--font-mono)', padding: '3px 0', display: 'flex', gap: '6px', alignItems: 'flex-start' },
  errorDot: { color: 'var(--red)', flexShrink: 0, marginTop: '1px' },
  tagCloud: { display: 'flex', flexWrap: 'wrap', gap: '4px' },
  tag: {
    fontSize: '11px', fontFamily: 'var(--font-mono)',
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    borderRadius: '4px', padding: '2px 7px', color: 'var(--text-secondary)',
  },
  fnItem: { display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 0', fontSize: '12px', fontFamily: 'var(--font-mono)' },
  fnName: { color: 'var(--cyan)', fontWeight: 500 },
  fnArity: { color: 'var(--text-muted)', fontSize: '11px' },
  muted: { fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' },
  // JSON view
  jsonWrap: { height: '100%', overflowY: 'auto', padding: '12px' },
  json: {
    fontSize: '11px',
    fontFamily: 'var(--font-mono)',
    color: '#8b9cc8',
    lineHeight: '1.7',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
}
