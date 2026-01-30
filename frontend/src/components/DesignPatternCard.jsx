import React from 'react'

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
  const confidence = patterns.confidence || 0
  const detectedPatterns = patterns.detected_patterns || []
  const suggestedPattern = patterns.suggested_pattern || {}
  const analysisMethod = patterns.analysis_method || 'heuristic'

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

  // Get confidence level label
  const getConfidenceLabel = (conf) => {
    if (conf >= 0.8) return { label: 'High', color: 'text-green-400' }
    if (conf >= 0.5) return { label: 'Medium', color: 'text-yellow-400' }
    return { label: 'Low', color: 'text-red-400' }
  }

  const confidenceInfo = getConfidenceLabel(confidence)
  const patternConfidenceInfo = getConfidenceLabel(suggestedPattern.confidence || 0)

  return (
    <div className="cyber-card p-6">
      <h3 className="text-xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
        <span className="text-2xl">🏗️</span>
        Design Patterns
        <span className="ml-auto text-xs px-2 py-1 rounded bg-cyan-500/20 text-cyan-300">
          {analysisMethod === 'deep_learning' ? 'ML' : 'Heuristic'}
        </span>
      </h3>

      {/* Predicted Category and Pattern Type */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">Predicted Pattern</span>
          <span className={`text-sm ${confidenceInfo.color}`}>
            {confidenceInfo.label} Confidence ({(confidence * 100).toFixed(1)}%)
          </span>
        </div>
        <div className={`p-4 rounded-lg border ${getCategoryColor(predictedCategory)}`}>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold">{suggestedPattern.name || 'Unknown'}</span>
            <span className="text-sm px-2 py-0.5 rounded bg-black/30">{predictedCategory}</span>
          </div>
          <div className="text-sm opacity-90 mb-2">
            {suggestedPattern.description || 'Pattern description not available'}
          </div>
          {suggestedPattern.reason && (
            <div className="text-xs opacity-60 italic">
              💡 {suggestedPattern.reason}
            </div>
          )}
        </div>
      </div>

      {/* Detected Specific Patterns */}
      {detectedPatterns.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Detected Patterns</h4>
          <div className="space-y-3">
            {detectedPatterns.map((pattern, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${getCategoryColor(pattern.category)}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold">{pattern.name}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-black/20">
                    {(pattern.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="text-sm opacity-75">{pattern.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

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
