import React, { useState } from 'react'
import QualityScoreCard from './QualityScoreCard'
import CodeSmellsList from './CodeSmellsList'
import MLComplexityCard from './MLComplexityCard'
import ASTInfoCard from './ASTInfoCard'
import TechnicalDebtCard from './TechnicalDebtCard'
import AnnotatedCode from './AnnotatedCode'
// import FunctionComplexity from './FunctionComplexity'  // Hidden - Complexity tab disabled
import DesignPatternCard from './DesignPatternCard'

function AnalysisResults({ data }) {
  const [activeTab, setActiveTab] = useState('overview')

  // Tab display names
  const tabNames = {
    'overview': 'Analysis Details',
    'code': 'Code'
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-2 border-b border-[#2d3748]">
        {['overview', 'code'].map((tab) => (
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

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Quality Score */}
            {data.quality_score && (
              <QualityScoreCard qualityScore={data.quality_score} />
            )}

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

      {/* Complexity Tab - Hidden
      {activeTab === 'complexity' && (
        <FunctionComplexity data={data} />
      )}
      */}
    </div>
  )
}

export default AnalysisResults
