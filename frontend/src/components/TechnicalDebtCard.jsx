import React from 'react'
import { CurrencyDollarIcon, ClockIcon, ArrowTrendingUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/24/outline'

function TechnicalDebtCard({ technicalDebt }) {
  if (!technicalDebt) {
    return null
  }

  const getDebtLevelColor = (level) => {
    switch (level) {
      case 'critical':
        return '#dc2626' // red
      case 'high':
        return '#f59e0b' // orange
      case 'medium':
        return '#eab308' // yellow
      case 'low':
        return '#10b981' // green
      default:
        return '#6b7280' // gray
    }
  }

  const getDebtLevelLabel = (level) => {
    switch (level) {
      case 'critical':
        return 'Critical'
      case 'high':
        return 'High'
      case 'medium':
        return 'Medium'
      case 'low':
        return 'Low'
      default:
        return 'Unknown'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <ArrowTrendingUpIcon className="w-5 h-5 text-red-500" />
      case 'low':
        return <ArrowDownIcon className="w-5 h-5 text-green-500" />
      default:
        return <MinusIcon className="w-5 h-5 text-gray-500" />
    }
  }

  const debtSeverity = technicalDebt.debt_severity || technicalDebt.debt_level || 'medium'
  return (
    <div className="cyber-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <CurrencyDollarIcon className="w-6 h-6 text-yellow-400" />
          <h3 className="text-xl font-semibold text-white">Technical Debt</h3>
        </div>
        <div className="flex items-center space-x-2">
          {getSeverityIcon(debtSeverity)}
          <span className="text-sm text-gray-400 capitalize">{debtSeverity}</span>
        </div>
      </div>

      {/* Total Debt Score */}
      <div className="mb-6">
        <div className="text-center p-4 bg-[#202835] rounded-lg border border-[#2d3748]">
          <p className="text-sm text-gray-400 mb-1">Total Debt Score</p>
          <div className="flex items-center justify-center space-x-3">
            <div className="text-4xl font-bold" style={{ color: getDebtLevelColor(technicalDebt.debt_level) }}>
              {technicalDebt.total_debt_score?.toFixed(1) || 0}
            </div>
            <div className="text-sm">
              <div className="font-semibold" style={{ color: getDebtLevelColor(technicalDebt.debt_level) }}>
                {getDebtLevelLabel(technicalDebt.debt_level)}
              </div>
              <div className="text-gray-500">/ 100</div>
            </div>
          </div>
        </div>
      </div>

      {/* Estimated Hours */}
      {technicalDebt.estimated_hours != null && (
        <div className="mb-6 p-3 bg-blue-500/20 rounded-lg border border-blue-500/50">
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-5 h-5 text-blue-400" />
            <div>
              <p className="text-sm font-semibold text-blue-300">Estimated Fix Time</p>
              <p className="text-lg font-bold text-blue-400">{(technicalDebt.estimated_hours || 0).toFixed(1)} hours</p>
            </div>
          </div>
        </div>
      )}

      {/* Priority Issues */}
      {technicalDebt.priority_issues && technicalDebt.priority_issues.length > 0 && (
        <div className="mb-6 pt-4 border-t border-[#2d3748]">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">
            Priority Issues ({technicalDebt.priority_issues.length})
          </h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {technicalDebt.priority_issues.slice(0, 5).map((issue, idx) => (
              <div key={idx} className="bg-red-500/20 p-2 rounded border border-red-500/50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-xs font-semibold text-red-400 capitalize">
                        {issue.severity}
                      </span>
                      <span className="text-xs text-gray-400">
                        {issue.type.replace(/_/g, ' ')}
                      </span>
                      {issue.line > 0 && (
                        <span className="text-xs text-gray-500">Line {issue.line}</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-300">{issue.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {technicalDebt.recommendations && technicalDebt.recommendations.length > 0 && (
        <div className="pt-4 border-t border-[#2d3748]">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Recommendations</h4>
          <ul className="space-y-2">
            {technicalDebt.recommendations.map((rec, idx) => (
              <li key={idx} className="text-xs text-gray-400 flex items-start">
                <span className="text-cyan-400 mr-2">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default TechnicalDebtCard
