import React from 'react'
import { ChartBarIcon } from '@heroicons/react/24/outline'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

function QualityScoreCard({ qualityScore }) {
  const getScoreColor = (score) => {
    if (score >= 85) return '#10b981' // green - Excellent
    if (score >= 70) return '#3b82f6' // blue - Good
    if (score >= 55) return '#f59e0b' // yellow - Fair
    return '#ef4444' // red - Needs Improvement
  }

  const getScoreLabel = (score) => {
    if (score >= 85) return 'Excellent'
    if (score >= 70) return 'Good'
    if (score >= 55) return 'Fair'
    return 'Needs Improvement'
  }

  const pieData = [
    { name: 'Maintainability', value: qualityScore.maintainability, color: getScoreColor(qualityScore.maintainability) },
    { name: 'Readability', value: qualityScore.readability, color: getScoreColor(qualityScore.readability) },
    { name: 'Complexity', value: qualityScore.complexity, color: getScoreColor(qualityScore.complexity) },
    { name: 'Documentation', value: qualityScore.documentation, color: getScoreColor(qualityScore.documentation) },
  ]

  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3 mb-4">
        <ChartBarIcon className="w-6 h-6 text-cyan-400" />
        <h3 className="text-xl font-semibold text-white">Quality Score</h3>
      </div>

      <div className="text-center mb-6">
        <div className="inline-block relative">
          <svg className="transform -rotate-90 w-32 h-32">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-[#2d3748]"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={`${(qualityScore.overall_score / 100) * 351.86} 351.86`}
              className={getScoreColor(qualityScore.overall_score)}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div>
              <div className="text-3xl font-bold" style={{ color: getScoreColor(qualityScore.overall_score) }}>
                {qualityScore.overall_score.toFixed(1)}
              </div>
              <div className="text-xs text-gray-400">/ 100</div>
            </div>
          </div>
        </div>
        {/* Evaluation label hidden
        <p className="mt-2 text-lg font-medium" style={{ color: getScoreColor(qualityScore.overall_score) }}>
          {getScoreLabel(qualityScore.overall_score)}
        </p>
        */}
      </div>

      <div className="space-y-3">
        {pieData.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <span className="text-sm text-gray-300">{item.name}</span>
            <div className="flex items-center space-x-2">
              <div className="w-24 h-2 bg-[#2d3748] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${item.value}%`,
                    backgroundColor: item.color
                  }}
                />
              </div>
              <span className="text-sm font-semibold w-12 text-right" style={{ color: item.color }}>
                {item.value.toFixed(1)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {qualityScore.issues && qualityScore.issues.length > 0 && (
        <div className="mt-6 pt-4 border-t border-[#2d3748]">
          <h4 className="text-sm font-semibold text-gray-300 mb-2">Issues Found:</h4>
          <ul className="space-y-1">
            {qualityScore.issues.slice(0, 3).map((issue, idx) => (
              <li key={idx} className="text-xs text-gray-400 flex items-start">
                <span className="text-red-400 mr-2">•</span>
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default QualityScoreCard
