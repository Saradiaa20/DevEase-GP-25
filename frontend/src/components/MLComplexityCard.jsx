import React from 'react'
import { CpuChipIcon } from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

function MLComplexityCard({ mlData }) {
  const { features, prediction } = mlData

  if (prediction.error) {
    return (
      <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4">
        <p className="text-yellow-400 text-sm">{prediction.error}</p>
      </div>
    )
  }

  const complexityColors = {
    'O(1)': '#10b981',
    'O(log n)': '#3b82f6',
    'O(n)': '#f59e0b',
    'O(n log n)': '#ef4444',
    'O(n²)': '#dc2626',
  }

  const chartData = Object.entries(features || {}).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: typeof value === 'number' ? value : (value ? 1 : 0),
  }))

  const probabilities = prediction.all_probabilities || {}

  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3 mb-4">
        <CpuChipIcon className="w-6 h-6 text-purple-400" />
        <h3 className="text-xl font-semibold text-white">ML Complexity Prediction</h3>
      </div>

      {prediction.predicted_complexity && (
        <div className="mb-6">
          <div className="text-center p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
            <p className="text-sm text-gray-400 mb-1">Predicted Complexity</p>
            <p
              className="text-3xl font-bold"
              style={{ color: complexityColors[prediction.complexity_description] || '#6b7280' }}
            >
              {prediction.complexity_description || prediction.predicted_complexity}
            </p>
            {prediction.confidence && (
              <p className="text-sm text-gray-400 mt-2">
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </p>
            )}
          </div>
        </div>
      )}

      {Object.keys(probabilities).length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Probability Distribution</h4>
          <div className="space-y-2">
            {Object.entries(probabilities)
              .sort(([, a], [, b]) => b - a)
              .map(([complexity, prob]) => (
                <div key={complexity} className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{complexity}</span>
                  <div className="flex items-center space-x-2 flex-1 mx-2">
                    <div className="flex-1 h-2 bg-[#2d3748] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${prob * 100}%`,
                          backgroundColor: complexityColors[complexity] || '#6b7280'
                        }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-gray-300 w-12 text-right">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {features && (
        <div className="mt-6 pt-4 border-t border-[#2d3748]">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Extracted Features</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(features).map(([key, value]) => (
              <div key={key} className="bg-[#202835] p-2 rounded border border-[#2d3748]">
                <p className="text-xs text-gray-400 mb-1">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
                <p className="text-sm font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default MLComplexityCard
