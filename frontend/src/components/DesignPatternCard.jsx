import React from 'react'

/** If you do not see this ID in the Design Patterns box, the browser is loading an old bundle or a different project folder. */
const DP_UI_BUILD = 'ml-card-2026-04-08'

const DesignPatternCard = ({ data }) => {
  if (!data || !data.design_patterns) {
    return (
      <div className="cyber-card p-6">
        <h3 className="text-xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
          <span className="text-2xl">🏗️</span>
          Design Patterns
        </h3>
        <p className="text-gray-400">No design pattern analysis available</p>
      </div>
    )
  }

  const patterns = data.design_patterns
  const predictedCategory = patterns.predicted_category || 'Unknown'
  const suggestedPattern = patterns.suggested_pattern || {}
  const analysisMethod = patterns.analysis_method || ''

  // Category colors
  const getCategoryColor = (category) => {
    switch (category) {
      case 'Creational':
        return 'text-green-400 bg-green-500/10 border-green-500/30'
      case 'Structural':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      case 'Behavioral':
        return 'text-purple-400 bg-purple-500/10 border-purple-500/30'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  return (
    <div className="cyber-card p-6">
      <h3 className="text-xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
        <span className="text-2xl">🏗️</span>
        Design Patterns
      </h3>
      {analysisMethod === 'none' && (
        <p className="text-xs text-amber-400/90 mb-4">
          Model files missing — run in backend:{' '}
          <code className="text-amber-200/90">python train_design_pattern_model.py</code>
        </p>
      )}

      {/* Predicted Category and Pattern Type */}
      <div className="mb-6">
        <div className="mb-2">
          <span className="text-gray-400 text-sm">Predicted Pattern</span>
        </div>
        <div className={`p-4 rounded-lg border ${getCategoryColor(predictedCategory)}`}>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold">{suggestedPattern.name || 'Unknown'}</span>
            <span className="text-sm px-2 py-0.5 rounded bg-black/30">{predictedCategory}</span>
          </div>
          <div className="text-sm opacity-90">
            {suggestedPattern.description || 'Pattern description not available'}
          </div>
        </div>
      </div>

      {/* Pattern Categories Legend */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h4 className="text-xs font-semibold text-gray-400 mb-2">Pattern Categories</h4>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 rounded bg-green-500/20 text-green-400">
            Creational: Singleton, Factory, Builder, Prototype
          </span>
          <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-400">
            Structural: Adapter, Decorator, Facade, Proxy
          </span>
          <span className="px-2 py-1 rounded bg-purple-500/20 text-purple-400">
            Behavioral: Observer, Strategy, Command, State
          </span>
        </div>
      </div>
    </div>
  )
}

export default DesignPatternCard
