import React from 'react'

const LANGUAGES = [
  { id: 'python', label: 'Python', icon: '🐍', color: '#3b82f6' },
  { id: 'cpp', label: 'C++', icon: '⚙️', color: '#f97316' },
  { id: 'javascript', label: 'JavaScript', icon: '⚡', color: '#eab308' },
]

export default function LanguageSelector({ sourceLang, targetLang, onTargetChange }) {
  const source = LANGUAGES.find(l => l.id === sourceLang)
  const target = LANGUAGES.find(l => l.id === targetLang)

  return (
    <div style={styles.wrapper}>
      {/* Source */}
      <div style={styles.langBadge}>
        <span style={styles.icon}>{source.icon}</span>
        <span style={{ ...styles.langLabel, color: source.color }}>{source.label}</span>
        <span style={styles.pill}>source</span>
      </div>

      {/* Arrow */}
      <div style={styles.arrowWrap}>
        <div style={styles.arrowLine} />
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style={styles.arrowHead}>
          <path d="M4 9h10M10 5l4 4-4 4" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      {/* Target selector */}
      <div style={styles.selectWrap}>
        <span style={styles.icon}>{target.icon}</span>
        <select
          value={targetLang}
          onChange={e => onTargetChange(e.target.value)}
          style={styles.select}
        >
          <option value="cpp">C++</option>
          <option value="javascript">JavaScript</option>
        </select>
        <span style={styles.pill}>target</span>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={styles.chevron}>
          <path d="M3 4.5l3 3 3-3" stroke="var(--text-secondary)" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  langBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '6px 12px',
    height: '36px',
  },
  icon: {
    fontSize: '14px',
    lineHeight: 1,
  },
  langLabel: {
    fontWeight: 600,
    fontSize: '13px',
    letterSpacing: '0.02em',
  },
  pill: {
    fontSize: '10px',
    color: 'var(--text-muted)',
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '1px 5px',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  },
  arrowWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
    opacity: 0.7,
  },
  arrowLine: {
    width: '20px',
    height: '1px',
    background: 'linear-gradient(to right, transparent, var(--accent))',
  },
  arrowHead: {
    marginLeft: '-8px',
  },
  selectWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border-bright)',
    borderRadius: '8px',
    padding: '6px 12px',
    height: '36px',
    position: 'relative',
    cursor: 'pointer',
  },
  select: {
    background: 'transparent',
    border: 'none',
    color: 'var(--accent)',
    fontWeight: 600,
    fontSize: '13px',
    outline: 'none',
    cursor: 'pointer',
    appearance: 'none',
    paddingRight: '16px',
    letterSpacing: '0.02em',
  },
  chevron: {
    position: 'absolute',
    right: '10px',
    pointerEvents: 'none',
  },
}
