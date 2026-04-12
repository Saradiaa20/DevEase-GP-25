import React, { useMemo } from 'react'
import { CpuChipIcon } from '@heroicons/react/24/outline'

/** Backend label → display notation (matches ml_complexity_predictor complexity_mapping) */
const COMPLEXITY_DISPLAY = {
  '1': 'O(1)',
  logn: 'O(log n)',
  n: 'O(n)',
  nlogn: 'O(n log n)',
  n_square: 'O(n²)',
  n_cube: 'O(n³)',
  exponential: 'O(2^n)',
}

const COMPLEXITY_COLORS = {
  'O(1)': '#10b981',
  'O(log n)': '#3b82f6',
  'O(n)': '#f59e0b',
  'O(n log n)': '#ef4444',
  'O(n²)': '#dc2626',
  'O(n³)': '#991b1b',
  'O(2^n)': '#7f1d1d',
}

/** Short, user-friendly explanation: what the class means for runtime */
const COMPLEXITY_EXPLANATIONS = {
  'O(1)': {
    headline: 'Constant time',
    body:
      'The amount of work stays about the same even if your input gets much bigger. That usually means very predictable, fast behavior for large data.',
  },
  'O(log n)': {
    headline: 'Grows slowly with input size',
    body:
      'When you double the input, you only add a little extra work—not double. Often appears with smart search, balanced trees, or halving the problem each step.',
  },
  'O(n)': {
    headline: 'Scales in line with input size',
    body:
      'Roughly speaking, if you double the amount of data, the work about doubles too. Typical for a single pass over a list or array.',
  },
  'O(n log n)': {
    headline: 'A bit more than linear',
    body:
      'Common for efficient sorting and many solid algorithms. Grows faster than O(n) but still manageable for large inputs—much gentler than O(n²).',
  },
  'O(n²)': {
    headline: 'Work can grow quickly',
    body:
      'Often tied to nested loops over the same data. Doubling the input can roughly quadruple the work, so performance can drop fast as data grows.',
  },
  'O(n³)': {
    headline: 'Very steep growth',
    body:
      'Work grows with the cube of input size. Triple-nested loops over the same growing data often land here—large inputs become expensive quickly.',
  },
  'O(2^n)': {
    headline: 'Exponential growth',
    body:
      'Each extra bit of input can roughly double the work. Typical of brute-force exploration or naive recursion without memoization—fine for tiny inputs only.',
  },
}

function toDisplayNotation(rawKey) {
  if (!rawKey) return null
  const s = String(rawKey)
  if (COMPLEXITY_DISPLAY[s]) return COMPLEXITY_DISPLAY[s]
  if (COMPLEXITY_COLORS[s]) return s
  return s
}

function getExplanation(displayNotation) {
  return COMPLEXITY_EXPLANATIONS[displayNotation] || {
    headline: 'Estimated complexity class',
    body:
      'This is the model’s best guess for how runtime grows with input size. Larger complexity classes usually mean the program may slow down more as data grows.',
  }
}

function summarizeFeatures(features) {
  if (!features || typeof features !== 'object') return null
  const ifs = features.no_of_ifs ?? 0
  const loops = features.no_of_loop ?? 0
  const breaks = features.no_of_break ?? 0
  const depth = features.nested_loop_depth ?? 0
  const sorts = features.no_of_sort ?? 0
  const pq = features.priority_queue_present
  const hs = features.hash_set_present
  const hm = features.hash_map_present
  const rec = features.recursion_present

  const parts = []
  if (loops > 0) parts.push(`${loops} loop${loops === 1 ? '' : 's'}`)
  if (depth > 1) parts.push(`nested loop depth up to ${depth}`)
  if (ifs > 0) parts.push(`${ifs} branch${ifs === 1 ? '' : 'es'} (if-like)`)
  if (sorts > 0) parts.push(`${sorts} sort call${sorts === 1 ? '' : 's'}`)
  if (breaks > 0) parts.push(`${breaks} break`)
  if (pq) parts.push('priority-queue style usage')
  if (hs) parts.push('set / hash-set style usage')
  if (hm) parts.push('map / hash-map style usage')
  if (rec) parts.push('possible recursion')

  if (parts.length === 0) {
    return 'The model saw relatively few loop and branch signals in the snippet it analyzed.'
  }
  return `Signals the model used include: ${parts.join('; ')}.`
}

function MLComplexityCard({ mlData }) {
  if (!mlData) return null

  const features = mlData.features || {}
  const prediction = mlData.prediction || {}

  const featureSummary = useMemo(() => summarizeFeatures(features), [features])

  if (prediction.error) {
    return (
      <div className="cyber-card border-yellow-500/40">
        <div className="flex items-center space-x-3 mb-3">
          <CpuChipIcon className="w-6 h-6 text-yellow-400" aria-hidden="true" />
          <h3 className="text-xl font-semibold text-white">Code complexity (estimated)</h3>
        </div>
        <p className="text-yellow-400 text-sm mb-3">{prediction.error}</p>
        <p className="text-xs text-gray-400 mb-3">
          The server could not train or load the model (for example, <code className="text-gray-300">dataset1.csv</code>{' '}
          missing next to the backend, or training failed). Check backend logs. You can still read the code signals
          below.
        </p>
        {featureSummary && (
          <div className="p-4 rounded-lg bg-[#1a2332] border border-[#2d3748]">
            <p className="text-xs font-semibold text-gray-400 mb-1">Signals read from your code</p>
            <p className="text-sm text-gray-300 leading-relaxed">{featureSummary}</p>
          </div>
        )}
      </div>
    )
  }

  const displayNotation =
    prediction.complexity_description || toDisplayNotation(prediction.predicted_complexity)
  const explanation = useMemo(() => getExplanation(displayNotation), [displayNotation])
  const accentColor = COMPLEXITY_COLORS[displayNotation] || '#6b7280'

  const probabilities = prediction.all_probabilities || {}
  const sortedProbs = Object.entries(probabilities).sort(([, a], [, b]) => b - a)

  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3 mb-4">
        <CpuChipIcon className="w-6 h-6 text-purple-400" aria-hidden="true" />
        <h3 className="text-xl font-semibold text-white">Code complexity (estimated)</h3>
      </div>

      <div className="mb-6 space-y-4">
        {prediction.predicted_complexity ? (
          <>
            <div
              className="p-5 rounded-lg border bg-[#202835]"
              style={{ borderColor: `${accentColor}55` }}
            >
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400 mb-1">
                Expected growth of work with input size
              </p>
              <p className="text-4xl font-bold mb-2" style={{ color: accentColor }}>
                {displayNotation || 'Unknown'}
              </p>
              <p className="text-base font-semibold text-white mb-2">{explanation.headline}</p>
              <p className="text-sm text-gray-300 leading-relaxed">{explanation.body}</p>
              {prediction.confidence != null && (
                <p className="text-xs text-gray-500 mt-3">
                  Model confidence in this class: {(prediction.confidence * 100).toFixed(0)}%. This is a
                  statistical guess from code patterns, not a guarantee of real-world speed (I/O,
                  hardware, and libraries also matter).
                </p>
              )}
              {prediction.training_info && (
                <p className="text-xs text-gray-500 mt-2 border-t border-[#2d3748] pt-2">
                  Last training run: best classifier <span className="text-gray-400">{prediction.training_info.best_model}</span>
                  {' · '}
                  hold-out accuracy {(prediction.training_info.holdout_accuracy * 100).toFixed(1)}% (
                  {prediction.training_info.test_samples} test samples).
                </p>
              )}
            </div>
          </>
        ) : (
          <div className="p-4 rounded-lg bg-[#202835] border border-[#2d3748]">
            <p className="text-sm text-gray-300">
              No complexity class was returned for this run. Check that the ML model is loaded and the
              analysis completed successfully.
            </p>
          </div>
        )}

        {featureSummary && (
          <div className="p-4 rounded-lg bg-[#1a2332] border border-[#2d3748]">
            <p className="text-xs font-semibold text-gray-400 mb-1">
              {prediction.predicted_complexity ? 'What influenced this guess' : 'Signals read from your code'}
            </p>
            <p className="text-sm text-gray-300 leading-relaxed">{featureSummary}</p>
          </div>
        )}
      </div>

      {sortedProbs.length > 0 && (
        <details className="mb-2 group">
          <summary className="cursor-pointer text-sm font-semibold text-cyan-400 hover:text-cyan-300 list-none flex items-center gap-2">
            <span className="group-open:rotate-90 transition-transform inline-block">▸</span>
            Other possibilities (model probabilities)
          </summary>
          <p className="text-xs text-gray-500 mt-2 mb-3">
            Shorter bars mean the model considered those complexity classes less likely for this snippet.
          </p>
          <div className="space-y-2 pl-1">
            {sortedProbs.map(([rawKey, prob]) => {
              const label = toDisplayNotation(rawKey)
              const barColor = COMPLEXITY_COLORS[label] || '#6b7280'
              return (
                <div key={rawKey} className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 w-24 shrink-0">{label}</span>
                  <div className="flex-1 h-2 bg-[#2d3748] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${prob * 100}%`, backgroundColor: barColor }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-gray-300 w-12 text-right shrink-0">
                    {(prob * 100).toFixed(0)}%
                  </span>
                </div>
              )
            })}
          </div>
        </details>
      )}
    </div>
  )
}

export default MLComplexityCard
