import React, { useState, useMemo } from 'react'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

function AnnotatedCode({ data }) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const codeContent = data.code_content || '// No code content available'
  const language = data.language || 'Python'

  const lines = useMemo(() => codeContent.split('\n'), [codeContent])

  // Simple syntax highlighting
  const highlightSyntax = (line) => {
    const keywords = [
      'def', 'class', 'import', 'from', 'return', 'if', 'elif', 'else', 'for', 'while',
      'try', 'except', 'finally', 'with', 'as', 'in', 'not', 'and', 'or', 'True', 'False', 'None',
      'public', 'private', 'protected', 'static', 'void', 'int', 'float', 'String', 'boolean',
      'new', 'this', 'super', 'extends', 'implements', 'throws', 'throw', 'const', 'let', 'var',
      'function', 'async', 'await', 'export', 'default', 'self', 'raise', 'pass', 'break', 'continue',
      'final', 'abstract', 'interface', 'enum', 'switch', 'case', 'default', 'Optional', 'List', 'Map'
    ]

    const trimmed = line.trim()

    // Comments
    if (trimmed.startsWith('#') || trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) {
      return <span className="text-green-500">{line}</span>
    }

    // Docstrings
    if (trimmed.includes('"""') || trimmed.includes("'''")) {
      return <span className="text-green-500">{line}</span>
    }

    let result = line
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b(${keyword})\\b`, 'g')
      if (typeof result === 'string') {
        result = result.replace(regex, `__KW__${keyword}__KW__`)
      }
    })

    if (typeof result === 'string') {
      const parts = result.split(/(__KW__\w+__KW__)/g)
      return (
        <span className="text-gray-300">
          {parts.map((part, i) => {
            if (part.startsWith('__KW__') && part.endsWith('__KW__')) {
              const keyword = part.replace(/__KW__/g, '')
              return <span key={i} className="text-purple-400 font-semibold">{keyword}</span>
            }
            const stringParts = part.split(/("[^"]*"|'[^']*')/g)
            return stringParts.map((sp, j) => {
              if ((sp.startsWith('"') && sp.endsWith('"')) || (sp.startsWith("'") && sp.endsWith("'"))) {
                return <span key={`${i}-${j}`} className="text-yellow-300">{sp}</span>
              }
              const numParts = sp.split(/(\b\d+\.?\d*\b)/g)
              return numParts.map((np, k) => {
                if (/^\d+\.?\d*$/.test(np)) {
                  return <span key={`${i}-${j}-${k}`} className="text-cyan-300">{np}</span>
                }
                return <span key={`${i}-${j}-${k}`}>{np}</span>
              })
            })
          })}
        </span>
      )
    }

    return <span className="text-gray-300">{line}</span>
  }

  return (
    <div className="space-y-4">
      <div
        className="flex items-start justify-between gap-4 flex-wrap cursor-pointer select-none"
        onClick={() => setIsCollapsed(!isCollapsed)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            setIsCollapsed(!isCollapsed)
          }
        }}
      >
        <div>
          <h2 className="text-base font-bold text-white">Source code</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Syntax-highlighted view with line numbers
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs px-3 py-1 rounded-full border border-cyan-800/50 bg-cyan-900/20 text-cyan-300">
            {language}
          </span>
          {isCollapsed ? (
            <ChevronDownIcon className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronUpIcon className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>

      {!isCollapsed && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] overflow-hidden">
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto bg-[#1a2332]">
            <table className="w-full border-collapse">
              <tbody>
                {lines.map((line, idx) => {
                  const lineNumber = idx + 1

                  return (
                    <tr
                      key={idx}
                      className="hover:bg-[#0f1623]/40"
                    >
                      <td
                        className="px-3 py-0 text-right select-none font-mono text-xs border-r border-[#2d3748] text-gray-500"
                        style={{ width: '50px', minWidth: '50px' }}
                      >
                        {lineNumber}
                      </td>

                      <td className="px-4 py-0 font-mono text-sm whitespace-pre">
                        <div className="flex items-center min-h-[24px]">
                          <code>{highlightSyntax(line || ' ')}</code>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="border-t border-[#2d3748] bg-[#0f1623] px-4 py-2">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{lines.length} lines</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnnotatedCode
