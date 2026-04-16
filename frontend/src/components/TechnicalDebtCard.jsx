import React from 'react'
import { CurrencyDollarIcon, ClockIcon } from '@heroicons/react/24/outline'

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

  return (
    <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4">
      <div className="flex items-center mb-4">
        <div className="flex items-center space-x-3">
          <CurrencyDollarIcon className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-semibold text-cyan-400">Technical debt</h3>
        </div>
      </div>

      {/* Total Debt Score */}
      <div className="mb-6">
        <div className="text-center p-4 bg-[var(--bg-primary)] rounded-lg border border-[#2d3748]">
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
        <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-lg border border-[#2d3748]">
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-semibold text-gray-300">Estimated Fix Time</p>
              <p className="text-lg font-bold text-white">{(technicalDebt.estimated_hours || 0).toFixed(1)} hours</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TechnicalDebtCard
