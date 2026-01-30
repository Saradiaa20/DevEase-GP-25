import React, { useState } from 'react'
import Layout from '../components/Layout'
import FileUpload from '../components/FileUpload'
import AnalysisResults from '../components/AnalysisResults'
import { analyzeFile, analyzeContent } from '../services/api'
import {
  CurrencyDollarIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline'

function Dashboard() {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    setAnalysisData(null)
    setSelectedFile(file.name)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const result = await analyzeFile(formData)
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
        : (err.response?.data?.detail || err.message || 'Analysis failed')
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
      setAnalysisData(result.data)
      // Save to localStorage for export functionality
      localStorage.setItem('lastAnalysis', JSON.stringify({
        fileName: 'pasted_code.py',
        timestamp: new Date().toISOString(),
        data: result.data
      }))
    } catch (err) {
      const isNetworkError = err.message === 'Network Error' || err.code === 'ERR_NETWORK'
      const message = isNetworkError
        ? 'Backend server is not running. Start it first: from the project folder run start_backend.bat, or open a terminal, cd backend, then run: python -m app.main'
        : (err.response?.data?.detail || err.message || 'Analysis failed')
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
    const totalSmells = codeSmells?.total_smells || 0
    const overallQuality = qualityScore?.overall_score || 0
    
    return {
      technicalDebt: debtScore,
      technicalDebtHours: estimatedHours,
      debtRating: getDebtRating(debtScore, estimatedHours, totalSmells, overallQuality),
      complexity: mlComplexity?.prediction?.complexity_description || 'N/A',
      complexityScore: qualityScore?.complexity || 0,
      smells: totalSmells,
      security: 0, // Would come from security analysis
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

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Main Dashboard</h1>
            <p className="text-gray-400">Analyze your code and track quality metrics</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Code Input */}
          <div className="lg:col-span-1">
            <div className="cyber-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center">
                  <svg className="w-5 h-5 mr-2 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Code Input
                </h2>
                {analysisData?.language && (
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                    {analysisData.language}
                  </span>
                )}
              </div>

              <FileUpload
                onFileUpload={handleFileUpload}
                onContentAnalysis={handleContentAnalysis}
                loading={loading}
              />

              {selectedFile && (
                <div className="mt-4 p-3 bg-[#202835] rounded-lg border border-[#2d3748]">
                  <div className="flex items-center space-x-2 text-green-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-sm font-medium">{selectedFile}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Summary Cards */}
            {metrics && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                  icon={CurrencyDollarIcon}
                  title="Technical Debt"
                  value={metrics.debtRating.letter}
                  subtitle={`${metrics.technicalDebtHours.toFixed(1)}h estimated`}
                  color={metrics.debtRating.color}
                  score={metrics.technicalDebt}
                />
                <MetricCard
                  icon={CpuChipIcon}
                  title="Cyclomatic"
                  value={metrics.complexityScore}
                  subtitle="Complexity Score"
                  color="blue"
                />
                <MetricCard
                  icon={ExclamationTriangleIcon}
                  title="Smells"
                  value={metrics.smells}
                  subtitle="Issues"
                  color={metrics.smells > 5 ? 'red' : 'green'}
                />
                <MetricCard
                  icon={ShieldCheckIcon}
                  title="Security"
                  value={metrics.security}
                  subtitle="Vulnerabilities"
                  color={metrics.security > 0 ? 'red' : 'green'}
                />
              </div>
            )}

            {/* Analysis Results */}
            {error && (
              <div className="cyber-card border-red-500/50 bg-red-500/10 p-4">
                <div className="text-red-400 font-semibold mb-2">Error</div>
                <div className="text-gray-300 text-sm whitespace-pre-wrap">{error}</div>
              </div>
            )}

            {analysisData && (
              <AnalysisResults data={analysisData} />
            )}

            {/* Empty State */}
            {!analysisData && !loading && (
              <div className="cyber-card text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4 text-cyan-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-gray-400">Upload a file or paste code to start analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color, score }) {
  const colorClasses = {
    green: 'text-green-400 bg-green-400/10 border-green-500/50',
    blue: 'text-blue-400 bg-blue-400/10 border-blue-500/50',
    yellow: 'text-yellow-400 bg-yellow-400/10 border-yellow-500/50',
    orange: 'text-orange-400 bg-orange-400/10 border-orange-500/50',
    red: 'text-red-400 bg-red-400/10 border-red-500/50',
  }

  return (
    <div className={`cyber-card border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className={`w-6 h-6 ${colorClasses[color].split(' ')[0]}`} />
        <span className="text-xs text-gray-400">{title}</span>
      </div>
      <div className={`text-3xl font-bold mb-1 ${colorClasses[color].split(' ')[0]}`}>
        {value}
      </div>
      <div className="text-xs text-gray-400">{subtitle}</div>
      {score !== undefined && (
        <div className="mt-2 h-1 bg-[#2d3748] rounded-full overflow-hidden">
          <div
            className={`h-full ${colorClasses[color].split(' ')[1]}`}
            style={{ width: `${Math.min(100, score)}%` }}
          />
        </div>
      )}
    </div>
  )
}

export default Dashboard
