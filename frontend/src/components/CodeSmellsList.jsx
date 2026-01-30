import React, { useState } from 'react'
import { ExclamationTriangleIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

function CodeSmellsList({ smells }) {
  const [expandedSeverity, setExpandedSeverity] = useState(null)

  const severityColors = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
  }

  const severityIcons = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🔵',
  }

  const toggleSeverity = (severity) => {
    setExpandedSeverity(expandedSeverity === severity ? null : severity)
  }

  return (
    <div className="cyber-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center">
          <ExclamationTriangleIcon className="w-6 h-6 text-yellow-400 mr-2" />
          Code Smells Detected
        </h3>
        <span className="bg-red-500/20 text-red-400 border border-red-500/50 px-3 py-1 rounded-full text-sm font-semibold">
          {smells.total_smells} Total
        </span>
      </div>

      <div className="space-y-3">
        {Object.entries(smells.by_severity)
          .filter(([_, count]) => count > 0)
          .map(([severity, count]) => (
            <div key={severity} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSeverity(severity)}
                className={`w-full px-4 py-3 flex items-center justify-between ${severityColors[severity]}`}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{severityIcons[severity]}</span>
                  <span className="font-semibold capitalize">{severity}</span>
                  <span className="text-sm">({count} issues)</span>
                </div>
                {expandedSeverity === severity ? (
                  <ChevronUpIcon className="w-5 h-5" />
                ) : (
                  <ChevronDownIcon className="w-5 h-5" />
                )}
              </button>

              {expandedSeverity === severity && (
                <div className="p-4 bg-[#202835] border-t border-[#2d3748]">
                  <div className="space-y-3">
                    {smells.smells
                      .filter((smell) => smell.severity === severity)
                      .slice(0, 10)
                      .map((smell, idx) => (
                        <div key={idx} className="bg-[#1a2332] p-3 rounded border border-[#2d3748]">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-xs font-semibold text-gray-400">
                                  {smell.type.replace(/_/g, ' ').toUpperCase()}
                                </span>
                                <span className="text-xs text-gray-500">Line {smell.line}</span>
                              </div>
                              <p className="text-sm text-gray-300">{smell.description}</p>
                              <p className="text-xs text-gray-400 mt-1 italic">
                                💡 {smell.suggestion}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          ))}
      </div>

      {smells.by_type && Object.keys(smells.by_type).length > 0 && (
        <div className="mt-6 pt-4 border-t border-[#2d3748]">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">By Type:</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(smells.by_type).map(([type, count]) => (
              <span
                key={type}
                className="px-3 py-1 bg-[#202835] text-gray-300 border border-[#2d3748] rounded-full text-xs font-medium"
              >
                {type.replace(/_/g, ' ')}: {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CodeSmellsList
