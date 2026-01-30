import React from 'react'
import { CodeBracketIcon } from '@heroicons/react/24/outline'

function ASTInfoCard({ astData }) {
  const displayFields = ['language', 'classes', 'functions', 'methods', 'imports', 'variables', 'fields', 'total_nodes', 'total_classes', 'total_methods']

  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3 mb-4">
        <CodeBracketIcon className="w-6 h-6 text-green-400" />
        <h3 className="text-xl font-semibold text-white">AST Analysis</h3>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayFields.map((field) => {
          const value = astData[field]
          if (value === undefined || value === null) return null

          if (Array.isArray(value)) {
            return (
              <div key={field} className="bg-[#202835] p-4 rounded-lg border border-[#2d3748]">
                <p className="text-sm font-semibold text-gray-300 mb-2 capitalize">
                  {field.replace(/_/g, ' ')} ({value.length})
                </p>
                <div className="flex flex-wrap gap-1">
                  {value.slice(0, 5).map((item, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-[#1a2332] text-xs text-gray-300 rounded border border-[#2d3748]"
                    >
                      {item}
                    </span>
                  ))}
                  {value.length > 5 && (
                    <span className="px-2 py-1 bg-[#1a2332] text-xs text-gray-400 rounded border border-[#2d3748]">
                      +{value.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )
          }

          return (
            <div key={field} className="bg-[#202835] p-4 rounded-lg border border-[#2d3748]">
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
