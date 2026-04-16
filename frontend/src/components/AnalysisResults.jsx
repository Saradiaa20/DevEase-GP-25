import React, { useState } from 'react'
// import QualityScoreCard from './QualityScoreCard'
import CodeSmellsList from './CodeSmellsList'
import MLComplexityCard from './MLComplexityCard'
import ASTInfoCard from './ASTInfoCard'
import TechnicalDebtCard from './TechnicalDebtCard'
import AnnotatedCode from './AnnotatedCode'
// import FunctionComplexity from './FunctionComplexity'  // Hidden - Complexity tab disabled
import DesignPatternCard from './DesignPatternCard'
import NLPReport from './NLPReport'
import {
  SparklesIcon,
  CheckCircleIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

function AnalysisResults({ data }) {
  const hasNlpReport = !!data?.nlp_report
  const wrapperData = data?.wrapper_generator
  const hasWrapperTab =
    wrapperData &&
    (wrapperData.patterns_found > 0 || wrapperData.suggestions?.length > 0 || wrapperData.message)
  const [activeTab, setActiveTab] = useState(hasNlpReport ? 'report' : 'overview')

  // Tab display names
  const tabNames = {
    'report': 'AI Report',
    'overview': 'Analysis Details',
    'code': 'Code',
    'wrappers': 'Safety Wrappers',
  }

  const tabs = hasNlpReport ? ['report', 'overview', 'code'] : ['overview', 'code']
  if (hasWrapperTab) tabs.splice(hasNlpReport ? 2 : 1, 0, 'wrappers')

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-2 border-b border-[#2d3748]">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab
                ? 'text-cyan-400 border-b-2 border-cyan-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            {tabNames[tab]}
          </button>
        ))}
      </div>

      {/* NLP Report Tab */}
      {activeTab === 'report' && (
        <NLPReport nlpReport={data.nlp_report} />
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Quality Score */}
            {/* {data.quality_score && ( */}
              {/* <QualityScoreCard qualityScore={data.quality_score} /> */}
            {/* )} */}

            {/* ML Complexity Prediction */}
            {data.ml_complexity && data.ml_complexity.prediction && !data.ml_complexity.prediction.error && (
              <MLComplexityCard mlData={data.ml_complexity} />
            )}
          </div>

          {/* Technical Debt */}
          {data.technical_debt && (
            <TechnicalDebtCard technicalDebt={data.technical_debt} />
          )}

          {/* Design Patterns */}
          {data.design_patterns && (
            <DesignPatternCard data={data} />
          )}

          {/* Code Smells */}
          {data.code_smells && data.code_smells.total_smells > 0 && (
            <CodeSmellsList smells={data.code_smells} />
          )}

          {/* AST Information */}
          {data.language && (
            <ASTInfoCard astData={data} />
          )}
        </div>
      )}

      {/* Code Tab */}
      {activeTab === 'code' && (
        <AnnotatedCode data={data} />
      )}

      {/* Wrapper Generator Tab */}
      {activeTab === 'wrappers' && wrapperData && (
        <WrapperResults wrapperData={wrapperData} />
      )}

      {/* Complexity Tab - Hidden
      {activeTab === 'complexity' && (
        <FunctionComplexity data={data} />
      )}
      */}
    </div>
  )
}

function WrapperResults({ wrapperData }) {
  const suggestions = wrapperData?.suggestions || []
  const patternsFound = wrapperData?.patterns_found || 0

  if (patternsFound === 0 && suggestions.length === 0) {
    return (
      <div className="cyber-card border-green-500/40 bg-green-500/10">
        <div className="flex items-center gap-2 text-green-400 font-semibold mb-2">
          <CheckCircleIcon className="w-5 h-5" />
          No unsafe wrapper patterns found
        </div>
        <p className="text-sm text-gray-300">{wrapperData?.message || 'Your code looks safe.'}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="cyber-card p-4">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold">
            <SparklesIcon className="w-5 h-5" />
            Wrapper Generator Suggestions
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-[#202835] border border-[#2d3748] text-gray-300">
            {patternsFound} pattern{patternsFound === 1 ? '' : 's'} detected
          </span>
        </div>
        {wrapperData?.message && (
          <p className="text-sm text-gray-400 mt-2">{wrapperData.message}</p>
        )}
      </div>

      {suggestions.map((s) => (
        <div key={s.pattern_id} className="cyber-card p-4 border border-[#2d3748]">
          <div className="flex items-center justify-between gap-3 mb-3">
            <h4 className="font-semibold text-white text-sm">{s.suggestion_title || 'Safety Wrapper Suggested'}</h4>
            <span className="text-xs text-gray-400">Line {s.line_number}</span>
          </div>

          <p className="text-sm text-gray-300 mb-3">{s.explanation}</p>

          {s.changes_made?.length > 0 && (
            <ul className="text-xs text-gray-400 list-disc list-inside mb-3 space-y-1">
              {s.changes_made.map((change, idx) => (
                <li key={`${s.pattern_id}-${idx}`}>{change}</li>
              ))}
            </ul>
          )}

          <div className="grid md:grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-red-400 font-semibold mb-1 flex items-center gap-1">
                <XMarkIcon className="w-3 h-3" />
                Original
              </p>
              <pre className="bg-[#0a0e27] rounded-lg p-3 text-xs text-red-300 overflow-x-auto whitespace-pre-wrap break-words border border-red-900/50 max-h-64">
                {s.original_code}
              </pre>
            </div>

            <div>
              <p className="text-xs text-green-400 font-semibold mb-1 flex items-center gap-1">
                <CheckCircleIcon className="w-3 h-3" />
                Suggested Safer Version
              </p>
              <pre className="bg-[#0a0e27] rounded-lg p-3 text-xs text-green-300 overflow-x-auto whitespace-pre-wrap break-words border border-green-900/50 max-h-64">
                {s.wrapped_code}
              </pre>
            </div>
          </div>
        </div>
      ))}

      {suggestions.length === 0 && (
        <div className="cyber-card border-yellow-500/40 bg-yellow-500/10">
          <div className="flex items-center gap-2 text-yellow-400 font-semibold mb-2">
            <ExclamationTriangleIcon className="w-5 h-5" />
            Suggestions unavailable
          </div>
          <p className="text-sm text-gray-300">
            Unsafe patterns were detected, but suggestions could not be generated right now.
          </p>
        </div>
      )}
    </div>
  )
}

export default AnalysisResults
