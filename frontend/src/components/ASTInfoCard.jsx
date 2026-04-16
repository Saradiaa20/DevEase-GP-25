import React from 'react'
import { CodeBracketIcon } from '@heroicons/react/24/outline'

function ASTInfoCard({ astData }) {
  const displayFields = ['language', 'classes', 'functions', 'methods', 'imports', 'variables', 'fields', 'total_nodes', 'total_classes', 'total_methods']

  return (
    <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4">
      <div className="flex items-center space-x-3 mb-4">
        <CodeBracketIcon className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-semibold text-cyan-400">AST analysis</h3>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayFields.map((field) => {
          const value = astData[field]
          if (value === undefined || value === null) return null

          if (Array.isArray(value)) {
            return (
              <div key={field} className="bg-[var(--bg-primary)] p-4 rounded-lg border border-[#2d3748]">
                <p className="text-sm font-semibold text-gray-300 mb-2 capitalize">
                  {field.replace(/_/g, ' ')} ({value.length})
                </p>
                <div className="flex flex-wrap gap-1">
                  {value.slice(0, 5).map((item, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-[var(--bg-primary)] text-xs text-gray-300 rounded border border-[#2d3748]"
                    >
                      {item}
                    </span>
                  ))}
                  {value.length > 5 && (
                    <span className="px-2 py-1 bg-[var(--bg-primary)] text-xs text-gray-400 rounded border border-[#2d3748]">
                      +{value.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )
          }

          return (
            <div key={field} className="bg-[var(--bg-primary)] p-4 rounded-lg border border-[#2d3748]">
              <p className="text-sm font-semibold text-gray-300 mb-1 capitalize">
                {field.replace(/_/g, ' ')}
              </p>
              <p className="text-lg font-bold text-white">{value}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ASTInfoCard
