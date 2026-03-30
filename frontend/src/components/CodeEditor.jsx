import React from 'react'
import Editor from '@monaco-editor/react'

const SAMPLE_CODE = `# MultiLingual Transpiler — Example
x = 10
y = 20

def add(a, b):
    return a + b

def greet(name):
    print("Hello, " + name)

result = add(x, y)
print(result)

if result > 25:
    greet("World")
elif result == 30:
    print("thirty!")
else:
    print("small number")

i = 0
while i < 3:
    print(i)
    i += 1

for j in range(5):
    print(j)
`

export default function CodeEditor({ value, onChange }) {
  return (
    <div style={styles.wrapper}>
      <Editor
        height="100%"
        defaultLanguage="python"
        value={value}
        onChange={val => onChange(val || '')}
        theme="vs-dark"
        options={{
          fontSize: 13,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontLigatures: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          renderLineHighlight: 'gutter',
          padding: { top: 16, bottom: 16 },
          bracketPairColorization: { enabled: true },
          smoothScrolling: true,
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          overviewRulerBorder: false,
          overviewRulerLanes: 0,
          hideCursorInOverviewRuler: true,
          scrollbar: {
            verticalScrollbarSize: 6,
            horizontalScrollbarSize: 6,
          },
          wordWrap: 'on',
        }}
        beforeMount={monaco => {
          monaco.editor.defineTheme('transpiler-dark', {
            base: 'vs-dark',
            inherit: true,
            rules: [
              { token: 'keyword', foreground: '7c6af7', fontStyle: 'bold' },
              { token: 'string', foreground: '4ade80' },
              { token: 'number', foreground: 'fb923c' },
              { token: 'comment', foreground: '4a4d62', fontStyle: 'italic' },
              { token: 'identifier', foreground: 'e8eaf0' },
            ],
            colors: {
              'editor.background': '#13141a',
              'editor.foreground': '#e8eaf0',
              'editor.lineHighlightBackground': '#1a1b24',
              'editor.selectionBackground': '#7c6af730',
              'editorCursor.foreground': '#7c6af7',
              'editorLineNumber.foreground': '#2a2d3e',
              'editorLineNumber.activeForeground': '#7c6af7',
              'editorIndentGuide.background': '#1e2030',
            },
          })
        }}
        onMount={(editor, monaco) => {
          monaco.editor.setTheme('transpiler-dark')
        }}
      />
    </div>
  )
}

export { SAMPLE_CODE }

const styles = {
  wrapper: {
    height: '100%',
    width: '100%',
    overflow: 'hidden',
  },
}
