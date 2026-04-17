import React, { useState } from 'react'
import Layout from '../components/Layout'
import FileUpload from '../components/FileUpload'
import AnalysisResults from '../components/AnalysisResults'
import { analyzeFileWithExplanation, analyzeContent, explainAnalysis } from '../services/api'
import {
  CurrencyDollarIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'


function formatApiError(err) {
  const d = err.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d.map((e) => (typeof e === 'string' ? e : e.msg || JSON.stringify(e))).join(', ')
  }
  return err.message || 'Analysis failed'
}

function Dashboard() {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    setAnalysisData(null)
    
    if (!file || file.size === 0) {
      setSelectedFile(null)
      setError('This file is empty. Upload a file with code to analyze.')
      setLoading(false)
      return
    }

    setSelectedFile(file.name)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const result = await analyzeFileWithExplanation(formData)
      setAnalysisData(result.data)
      // Save to localStorage for export functionality
      localStorage.setItem('lastAnalysis', JSON.stringify({
        fileName: file.name,
        timestamp: new Date().toISOString(),
        data: result.data
      }))
    } catch (err) {
      const isNetworkError = err.message === 'Network Error' || err.code === 'ERR_NETWORK'
      const message = isNetworkError
        ? 'Backend server is not running. Start it first: from the project folder run start_backend.bat, or open a terminal, cd backend, then run: python -m app.main'
        : formatApiError(err)
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleContentAnalysis = async (content) => {
    setLoading(true)
    setError(null)
    setAnalysisData(null)
    setSelectedFile('pasted_code.py')

    try {
      const result = await analyzeContent(content)
      const explainResult = await explainAnalysis(result.data)
      const mergedData = {
        ...result.data,
        nlp_report: explainResult.data?.nlp_report,
      }
      setAnalysisData(mergedData)
      // Save to localStorage for export functionality
      localStorage.setItem('lastAnalysis', JSON.stringify({
        fileName: 'pasted_code.py',
        timestamp: new Date().toISOString(),
        data: mergedData
      }))
    } catch (err) {
      const isNetworkError = err.message === 'Network Error' || err.code === 'ERR_NETWORK'
      const message = isNetworkError
        ? 'Backend server is not running. Start it first: from the project folder run start_backend.bat, or open a terminal, cd backend, then run: python -m app.main'
        : formatApiError(err)
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  // Extract metrics for summary cards
  const getMetrics = () => {
    if (!analysisData) return null

    const technicalDebt = analysisData.technical_debt
    const codeSmells = analysisData.code_smells
    const qualityScore = analysisData.quality_score
    const mlComplexity = analysisData.ml_complexity

    const debtScore = technicalDebt?.total_debt_score || 0
    const estimatedHours = technicalDebt?.estimated_hours || 0
    const totalSmells = codeSmells?.length || 0
    const overallQuality = qualityScore?.overall_score || 0
    
    const mlBigO = mlComplexity?.prediction?.complexity_description
    const cyclomaticValue =
      mlBigO ||
      (qualityScore?.complexity != null ? Number(qualityScore.complexity).toFixed(1) : 'N/A')
    const cyclomaticSubtitle = mlBigO ? 'Predicted complexity' : 'Complexity score'

    return {
      technicalDebt: debtScore,
      technicalDebtHours: estimatedHours,
      debtRating: getDebtRating(debtScore, estimatedHours, totalSmells, overallQuality),
      complexity: mlComplexity?.prediction?.complexity_description || 'N/A',
      complexityScore: qualityScore?.complexity || 0,
      cyclomaticValue,
      cyclomaticSubtitle,
      smells: totalSmells,
      rating: getRating(overallQuality),  // Quality rating
    }
  }

  // Rating for quality score (higher score = better grade)
  // Aligned with Technical Debt thresholds for consistency
  const getRating = (score) => {
    if (score >= 85) return { letter: 'A', color: 'green' }
    if (score >= 70) return { letter: 'B', color: 'blue' }
    if (score >= 55) return { letter: 'C', color: 'yellow' }
    if (score >= 40) return { letter: 'D', color: 'orange' }
    return { letter: 'F', color: 'red' }
  }

  // Technical Debt rating based primarily on estimated hours to fix
  // Lower hours = better grade (less debt = better)
  const getDebtRating = (debtScore, estimatedHours, smellCount, qualityScore) => {
    const safeHours = estimatedHours || 0
    const safeSmells = smellCount || 0
    
    // Primary factor: Estimated hours determines the baseline grade
    // Very lenient thresholds - most code should be A or B
    let baseGrade
    if (safeHours < 2) baseGrade = 'A'        // Under 2 hours = excellent
    else if (safeHours < 4) baseGrade = 'A'   // 2-4 hours = still excellent  
    else if (safeHours < 8) baseGrade = 'B'   // 4-8 hours = good (full day)
    else if (safeHours < 16) baseGrade = 'C'  // 8-16 hours = fair (1-2 days)
    else if (safeHours < 32) baseGrade = 'D'  // 16-32 hours = needs attention (2-4 days)
    else baseGrade = 'F'                       // 32+ hours = critical (4+ days)
    
    // Secondary adjustment based on smell count (very lenient)
    const grades = ['A', 'B', 'C', 'D', 'F']
    const colors = { 'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'F': 'red' }
    
    let gradeIndex = grades.indexOf(baseGrade)
    
    // Only penalize for very high smell counts
    if (safeSmells > 20) gradeIndex += 1
    else if (safeSmells > 15) gradeIndex += 0.5
    
    // Perfect code bonus
    if (safeHours === 0 && safeSmells === 0) gradeIndex = 0  // Force A
    
    // Low hours with minor smells should still be A
    if (safeHours < 2 && safeSmells < 15) gradeIndex = 0  // Force A
    
    gradeIndex = Math.min(4, Math.max(0, Math.round(gradeIndex)))
    
    const finalGrade = grades[gradeIndex]
    return { letter: finalGrade, color: colors[finalGrade] }
  }

  const metrics = getMetrics()
  const showResults = !!analysisData

  const handleNewAnalysis = () => {
    setAnalysisData(null)
    setError(null)
    setSelectedFile(null)
  }

  const dashboardSubtitle = showResults
    ? 'Review analysis details, report and safety wrappers.'
    : 'Analyze your code and track quality metrics'

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {!showResults ? (
          <div className="w-full max-w-none mx-auto space-y-6 min-h-[min(72vh,calc(100vh-14rem))]">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Main Dashboard</h1>
                <p className="text-gray-400">{dashboardSubtitle}</p>
              </div>
            </div>
            {error && (
              <div className="cyber-card border-red-500/50 bg-red-500/10 p-4">
                <div className="text-red-400 font-semibold mb-2">Error</div>
                <div className="text-gray-300 text-sm whitespace-pre-wrap">{error}</div>
              </div>
            )}
            <div className="cyber-card-panel">
              <FileUpload
                onFileUpload={handleFileUpload}
                onContentAnalysis={handleContentAnalysis}
                loading={loading}
              />

              {selectedFile && (
                <div className="mt-4 p-3 bg-[var(--bg-panel)] rounded-lg border border-[var(--border-primary)]">
                  <div className="flex items-center space-x-2 text-green-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-base font-medium">{selectedFile}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto w-full space-y-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Main Dashboard</h1>
                <p className="text-gray-400">{dashboardSubtitle}</p>
              </div>
              <button
                type="button"
                onClick={handleNewAnalysis}
                className="shrink-0 px-4 py-2 rounded-lg text-sm font-medium border border-[var(--border-primary)] bg-[var(--bg-panel)] text-cyan-400 hover:border-cyan-500/50 hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                New analysis
              </button>
            </div>
            {metrics && (
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <MetricCard
                  icon={CurrencyDollarIcon}
                  title="Technical Debt"
                  value={metrics.debtRating.letter}
                  subtitle={`${metrics.technicalDebtHours.toFixed(1)}h estimated`}
                  color={metrics.debtRating.color}
                />
                <MetricCard
                  icon={CpuChipIcon}
                  title="Cyclomatic"
                  value={metrics.cyclomaticValue}
                  subtitle={metrics.cyclomaticSubtitle}
                  color="blue"
                />
                <MetricCard
                  icon={ExclamationTriangleIcon}
                  title="Code Smells"
                  value={metrics.smells}
                  subtitle="Issues"
                  color={metrics.smells > 5 ? 'red' : 'green'}
                />
              </div>
            )}

            {error && (
              <div className="cyber-card border-red-500/50 bg-red-500/10 p-4">
                <div className="text-red-400 font-semibold mb-2">Error</div>
                <div className="text-gray-300 text-sm whitespace-pre-wrap">{error}</div>
              </div>
            )}

            <AnalysisResults data={analysisData} />
          </div>
        )}
      </div>
    </Layout>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color, score }) {
  const accents = {
    green: {
      text: 'text-green-400',
      border: 'border-green-500/50',
      hoverBorder: 'hover:border-green-500/50',
      bg: 'bg-green-400/10',
      bar: 'bg-green-400',
    },
    blue: {
      text: 'text-blue-400',
      border: 'border-blue-500/50',
      hoverBorder: 'hover:border-blue-500/50',
      bg: 'bg-blue-400/10',
      bar: 'bg-blue-400',
    },
    yellow: {
      text: 'text-yellow-400',
      border: 'border-yellow-500/50',
      hoverBorder: 'hover:border-yellow-500/50',
      bg: 'bg-yellow-400/10',
      bar: 'bg-yellow-400',
    },
    orange: {
      text: 'text-orange-400',
      border: 'border-orange-500/50',
      hoverBorder: 'hover:border-orange-500/50',
      bg: 'bg-orange-400/10',
      bar: 'bg-orange-400',
    },
    red: {
      text: 'text-red-400',
      border: 'border-red-500/50',
      hoverBorder: 'hover:border-red-500/50',
      bg: 'bg-red-400/10',
      bar: 'bg-red-400',
    },
  }
  const a = accents[color] || accents.blue

  return (
    <div
      className={`cyber-card metric-card border ${a.border} ${a.hoverBorder} ${a.bg}`}
    >
      <div className="grid grid-cols-2 gap-3 items-stretch min-h-[5.5rem]">
        <div className="min-w-0 flex w-full flex-col justify-center items-start text-left">
          <span className="text-lg sm:text-xl font-semibold text-gray-200 leading-snug pr-2">
            {title}
          </span>
        </div>
        <div className="min-w-0 flex flex-col items-end justify-center text-right shrink-0">
          <Icon className={`w-6 h-6 shrink-0 ${a.text}`} />
          <div className={`text-3xl font-bold mt-1 mb-1 ${a.text}`}>
            {value}
          </div>
          <div className="text-xs text-gray-400">{subtitle}</div>
        </div>
      </div>
      {score !== undefined && (
        <div className="mt-2 h-1 bg-[#2d3748] rounded-full overflow-hidden">
          <div
            className={`h-full ${a.bar}`}
            style={{ width: `${Math.min(100, score)}%` }}
          />
        </div>
      )}
    </div>
  )
}

export default Dashboard