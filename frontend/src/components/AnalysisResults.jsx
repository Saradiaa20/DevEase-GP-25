import React, { useState } from 'react'
import CodeSmellsList from './CodeSmellsList'
import ASTInfoCard from './ASTInfoCard'
import TechnicalDebtCard from './TechnicalDebtCard'
import AnnotatedCode from './AnnotatedCode'
// import FunctionComplexity from './FunctionComplexity'  // Hidden - Complexity tab disabled
import DesignPatternCard from './DesignPatternCard'
import NLPReport from './NLPReport'
import {
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
  const [activeTab, setActiveTab] = useState('overview')

  // Tab display names (order below: Analysis Details → Explanation Report → Safety Wrappers → Source Code)
  const tabNames = {
    report: 'Explanation Report',
    overview: 'Analysis Details',
    code: 'Source Code',
    wrappers: 'Safety Wrappers',
  }

  const tabs = ['overview']
  if (hasNlpReport) tabs.push('report')
  if (hasWrapperTab) tabs.push('wrappers')
  tabs.push('code')

  // Backend returns code_smells as an array; some paths use { total_smells, smells }.
  const rawSmells = data?.code_smells
  const smellListForUi = Array.isArray(rawSmells) ? rawSmells : rawSmells?.smells ?? []

  return (
    <div className="space-y-4">
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

      {/* Explanation Report tab */}
      {activeTab === 'report' && (
        <NLPReport nlpReport={data.nlp_report} />
      )}

      {/* Overview Tab — same shell as Explanation Report / Safety Wrappers */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div>
            {/* <h2 className="text-base font-bold text-white">Analysis Details</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              AST structure, code smells, design patterns, and technical debt
            </p> */}
          </div>

          {/* AST analysis */}
          {data.language && (
            <ASTInfoCard astData={data} />
          )}

          {/* Code smells */}
          {smellListForUi.length > 0 && <CodeSmellsList smells={smellListForUi} />}

          {/* Design patterns */}
          {data.design_patterns && (
            <DesignPatternCard data={data} />
          )}

          {/* Technical debt */}
          {data.technical_debt && (
            <TechnicalDebtCard technicalDebt={data.technical_debt} />
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
      <div className="space-y-4">
        <div>
          <h2 className="text-base font-bold text-white">Safety Wrappers</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Unsafe patterns and suggested safer replacements
          </p>
        </div>
        <div className="rounded-lg border border-cyan-800/50 bg-cyan-900/10 px-4 py-3">
          <p className="text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wide">Status</p>
          <div className="flex items-center gap-2 text-sm text-gray-200 leading-relaxed">
            <CheckCircleIcon className="w-5 h-5 text-cyan-400 shrink-0" />
            <span>No unsafe wrapper patterns found. {wrapperData?.message || 'Your code looks safe.'}</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
 <div>
        <h2 className="text-base font-bold text-white">Safety Wrappers</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Unsafe patterns and suggested safer replacements
        </p>
      </div>
      {wrapperData?.message && (
        <div className="rounded-lg border border-cyan-800/50 bg-cyan-900/10 px-4 py-3">
          <p className="text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wide">Overview</p>
          <p className="text-sm text-gray-200 leading-relaxed">{wrapperData.message}</p>
        </div>
      )}

      {suggestions.map((s) => (
        <div
          key={s.pattern_id}
          className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4 space-y-3"
        >
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <h3 className="text-sm font-semibold text-cyan-400">
              {s.suggestion_title || 'Safety wrapper suggested'}
            </h3>
            <span className="text-xs text-gray-500">Line {s.line_number}</span>
          </div>

          {s.explanation && (
            <p className="text-sm text-gray-300 leading-relaxed">{s.explanation}</p>
          )}

          {s.changes_made?.length > 0 && (
            <ul className="text-sm text-gray-400 list-disc list-inside space-y-1 pl-1">
              {s.changes_made.map((change, idx) => (
                <li key={`${s.pattern_id}-${idx}`}>{change}</li>
              ))}
            </ul>
          )}

          <div className="grid md:grid-cols-2 gap-3 pt-1">
            <div>
              <p className="text-xs text-red-400 font-semibold mb-1 flex items-center gap-1">
                <XMarkIcon className="w-3 h-3" />
                Original
              </p>
              <pre className="bg-[var(--bg-primary)] rounded-lg p-3 text-xs text-red-300 overflow-x-auto whitespace-pre-wrap break-words border border-red-900/50 max-h-64 leading-relaxed">
                {s.original_code}
              </pre>
            </div>
            <div>
              <p className="text-xs text-green-400 font-semibold mb-1 flex items-center gap-1">
                <CheckCircleIcon className="w-3 h-3" />
                Suggested safer version
              </p>
              <pre className="bg-[var(--bg-primary)] rounded-lg p-3 text-xs text-green-300 overflow-x-auto whitespace-pre-wrap break-words border border-green-900/50 max-h-64 leading-relaxed">
                {s.wrapped_code}
              </pre>
            </div>
          </div>
        </div>
      ))}

      {suggestions.length === 0 && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623]/80 px-5 py-4">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="w-5 h-5 text-amber-400/90 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-gray-200">Suggestions unavailable</p>
              <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                Unsafe patterns were detected, but suggestions could not be generated right now.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalysisResults
