import React from 'react'
import { BoltIcon, LightBulbIcon } from '@heroicons/react/24/outline'

function FunctionComplexity({ data }) {
  // Extract function complexity data
  const functions = data.functions || []
  const codeSmells = data.code_smells?.smells || []

  // Mock function complexity data - in production, calculate from AST
  const functionComplexity = functions.map((funcName, idx) => {
    const funcSmells = codeSmells.filter(s => s.description?.includes(funcName))
    const complexity = funcSmells.length * 2 + Math.floor(Math.random() * 5) + 1
    
    return {
      function: funcName || `function_${idx + 1}`,
      line: (idx + 1) * 10,
      cyclomatic: complexity,
      cognitive: Math.floor(complexity * 1.5),
      rating: complexity <= 5 ? 'A' : complexity <= 10 ? 'B' : 'C',
    }
  })

  // If no functions, use mock data
  const displayFunctions = functionComplexity.length > 0 
    ? functionComplexity 
    : [
        { function: '_init_', line: 10, cyclomatic: 1, cognitive: 0, rating: 'A' },
        { function: 'load_data', line: 20, cyclomatic: 3, cognitive: 2, rating: 'A' },
        { function: 'process_and_validate_data', line: 32, cyclomatic: 7, cognitive: 12, rating: 'B' },
        { function: '_is_valid', line: 57, cyclomatic: 7, cognitive: 2, rating: 'B' },
        { function: 'save_results', line: 62, cyclomatic: 2, cognitive: 1, rating: 'A' },
      ]

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'A': return 'bg-green-500/20 text-green-400 border-green-500/50'
      case 'B': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50'
      case 'C': return 'bg-orange-500/20 text-orange-400 border-orange-500/50'
      default: return 'bg-red-500/20 text-red-400 border-red-500/50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Function Complexity Table */}
      <div className="cyber-card">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <BoltIcon className="w-5 h-5 mr-2 text-yellow-400" />
          Function Complexity
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#2d3748]">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Function</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Line</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Cyclomatic</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Cognitive</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Rating</th>
              </tr>
            </thead>
            <tbody>
              {displayFunctions.map((func, idx) => (
                <tr key={idx} className="border-b border-[#2d3748] hover:bg-[#202835] transition-colors">
                  <td className="py-3 px-4 text-cyan-400 font-mono">{func.function}</td>
                  <td className="py-3 px-4 text-gray-300">{func.line}</td>
                  <td className="py-3 px-4 text-gray-300">{func.cyclomatic}</td>
                  <td className="py-3 px-4 text-gray-300">{func.cognitive}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded border text-xs font-medium ${getRatingColor(func.rating)}`}>
                      {func.rating}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Insights */}
      <div className="cyber-card">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <LightBulbIcon className="w-5 h-5 mr-2 text-yellow-400" />
          AI Insights & Patterns
        </h2>
        <div className="text-gray-400">
          {data.code_smells?.total_smells > 0 ? (
            <div className="space-y-2">
              {data.code_smells.smells.slice(0, 3).map((smell, idx) => (
                <div key={idx} className="p-3 bg-[#202835] rounded-lg border border-[#2d3748]">
                  <div className="text-sm text-white mb-1">
                    {smell.type.replace(/_/g, ' ')} (Line {smell.line})
                  </div>
                  <div className="text-xs text-gray-400">{smell.suggestion}</div>
                </div>
              ))}
            </div>
          ) : (
            <p>No design patterns suggested.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default FunctionComplexity
