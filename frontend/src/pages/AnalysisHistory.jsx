import React, { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function AnalysisHistory() {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    avgDebtHours: 0,
    avgSmells: 0,
    totalLOC: 0,
  })

  // Mock data - in production, fetch from backend
  useEffect(() => {
    // Simulate fetching history data
    const mockHistory = [
      {
        id: 3,
        file: 'textPythonCode.py',
        date: '2026-01-09',
        loc: 77,
        smells: 2,
        security: 0,
        complexity: 20,
        debt: 2.8,
        rating: 'A',
      },
      {
        id: 2,
        file: 'pasted_code.py',
        date: '2026-01-09',
        loc: 77,
        smells: 2,
        security: 0,
        complexity: 20,
        debt: 2.8,
        rating: 'A',
      },
      {
        id: 1,
        file: 'textPythonCode.py',
        date: '2026-01-09',
        loc: 77,
        smells: 2,
        security: 0,
        complexity: 20,
        debt: 2.8,
        rating: 'A',
      },
    ]

    setHistory(mockHistory)
    setStats({
      totalAnalyses: mockHistory.length,
      avgDebtHours: mockHistory.reduce((sum, h) => sum + h.debt, 0) / mockHistory.length,
      avgSmells: mockHistory.reduce((sum, h) => sum + h.smells, 0) / mockHistory.length,
      totalLOC: mockHistory.reduce((sum, h) => sum + h.loc, 0),
    })
  }, [])

  // Prepare chart data
  const debtTrendData = history.map((item) => ({
    date: item.date,
    'Avg. Debt Hours': item.debt,
    'Avg. Complexity': item.complexity / 10, // Normalize
  }))

  const issuesTrendData = history.map((item) => ({
    date: item.date,
    Smells: item.smells,
    'Security Issues': item.security,
  }))

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'A': return 'bg-green-500/20 text-green-400 border-green-500/50'
      case 'B': return 'bg-blue-500/20 text-blue-400 border-blue-500/50'
      case 'C': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50'
      case 'D': return 'bg-orange-500/20 text-orange-400 border-orange-500/50'
      default: return 'bg-red-500/20 text-red-400 border-red-500/50'
    }
  }

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-3xl font-bold text-white mb-6">Analysis History</h1>

        {/* Overall Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="Total Analyses" value={stats.totalAnalyses} icon="📊" />
          <StatCard title="Avg. Debt Hours" value={`${stats.avgDebtHours.toFixed(1)}h`} icon="⏱️" />
          <StatCard title="Avg. Smells" value={stats.avgSmells.toFixed(0)} icon="🐛" />
          <StatCard title="Total LOC Analyzed" value={stats.totalLOC} icon="📝" />
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Technical Debt Trend */}
          <div className="cyber-card">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Technical Debt Trend
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={debtTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                <XAxis dataKey="date" stroke="#718096" />
                <YAxis stroke="#718096" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid #2d3748',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="Avg. Debt Hours" stroke="#fbbf24" strokeWidth={2} />
                <Line type="monotone" dataKey="Avg. Complexity" stroke="#8b5cf6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Issues Trend */}
          <div className="cyber-card">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Issues Trend
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={issuesTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                <XAxis dataKey="date" stroke="#718096" />
                <YAxis stroke="#718096" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid #2d3748',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Bar dataKey="Smells" fill="#f59e0b" />
                <Bar dataKey="Security Issues" fill="#ec4899" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Analysis History Table */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Analysis History
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2d3748]">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">ID</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">File</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Date</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">LOC</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Smells</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Security</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Complexity</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Debt</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Rating</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id} className="border-b border-[#2d3748] hover:bg-[#202835] transition-colors">
                    <td className="py-3 px-4 text-gray-300">{item.id}</td>
                    <td className="py-3 px-4 text-cyan-400">{item.file}</td>
                    <td className="py-3 px-4 text-gray-300">{item.date}</td>
                    <td className="py-3 px-4 text-gray-300">{item.loc}</td>
                    <td className="py-3 px-4 text-gray-300">{item.smells}</td>
                    <td className="py-3 px-4 text-gray-300">{item.security}</td>
                    <td className="py-3 px-4 text-gray-300">{item.complexity}</td>
                    <td className="py-3 px-4 text-yellow-400">{item.debt}h</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded border text-xs font-medium ${getRatingColor(item.rating)}`}>
                        {item.rating}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex space-x-2">
                        <button className="text-cyan-400 hover:text-cyan-300 text-sm">View</button>
                        <button className="text-red-400 hover:text-red-300 text-sm">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  )
}

function StatCard({ title, value, icon }) {
  return (
    <div className="cyber-card">
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-3xl font-bold text-cyan-400 mb-1">{value}</div>
      <div className="text-sm text-gray-400">{title}</div>
    </div>
  )
}

export default AnalysisHistory
