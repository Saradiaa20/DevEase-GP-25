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
    <div className="cyber-card">
      <div 
        className="flex items-center justify-between mb-4 cursor-pointer"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <h2 className="text-xl font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Source Code
        </h2>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
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
        <div className="bg-[#0d1117] rounded-lg border border-[#30363d] overflow-hidden">
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full border-collapse">
              <tbody>
                {lines.map((line, idx) => {
                  const lineNumber = idx + 1
                  
                  return (
                    <tr 
                      key={idx} 
                      className="hover:bg-[#161b22]"
                    >
                      {/* Line Number */}
                      <td 
                        className="px-3 py-0 text-right select-none font-mono text-xs border-r border-[#30363d] text-gray-600" 
                        style={{ width: '50px', minWidth: '50px' }}
                      >
                        {lineNumber}
                      </td>
                      
                      {/* Code Content */}
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
          
          {/* Summary Footer */}
          <div className="border-t border-[#30363d] bg-[#161b22] px-4 py-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">
                {lines.length} lines
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnnotatedCode
