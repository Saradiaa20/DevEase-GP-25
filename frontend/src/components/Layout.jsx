import React, { useState, useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
HomeIcon,
ChartBarIcon,
FolderIcon,
DocumentTextIcon,
Cog6ToothIcon,
UserIcon,
ArrowRightOnRectangleIcon,
BookOpenIcon,
ArrowDownIcon,
UserCircleIcon
} from '@heroicons/react/24/outline'
import { getCurrentUser, logoutUser } from '../services/api'

function Layout({ children }) {
const location = useLocation()
const user = getCurrentUser()
const [showExportMenu, setShowExportMenu] = useState(false)
const exportMenuRef = useRef(null)

// Close export menu when clicking outside
useEffect(() => {
const handleClickOutside = (event) => {
if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
setShowExportMenu(false)
}
}
document.addEventListener('mousedown', handleClickOutside)
return () => document.removeEventListener('mousedown', handleClickOutside)
}, [])

// Export analysis results
const exportAnalysis = (format) => {
const savedAnalysis = localStorage.getItem('lastAnalysis')

if (!savedAnalysis) {
alert('No analysis data to export. Please analyze a file first.')
setShowExportMenu(false)
return
}

const analysis = JSON.parse(savedAnalysis)
const timestamp = new Date().toISOString().split('T')[0]

if (format === 'json') {
// Export as JSON
const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' })
const url = URL.createObjectURL(blob)
const a = document.createElement('a')
a.href = url
a.download = `devease-analysis-${timestamp}.json`
document.body.appendChild(a)
a.click()
document.body.removeChild(a)
URL.revokeObjectURL(url)
} else if (format === 'txt') {
// Export as formatted text report
const report = generateTextReport(analysis)
const blob = new Blob([report], { type: 'text/plain' })
const url = URL.createObjectURL(blob)
const a = document.createElement('a')
a.href = url
a.download = `devease-analysis-${timestamp}.txt`
document.body.appendChild(a)
a.click()
document.body.removeChild(a)
URL.revokeObjectURL(url)
} else if (format === 'csv') {
// Export smells as CSV
const csv = generateCSV(analysis)
const blob = new Blob([csv], { type: 'text/csv' })
const url = URL.createObjectURL(blob)
const a = document.createElement('a')
a.href = url
a.download = `devease-smells-${timestamp}.csv`
document.body.appendChild(a)
a.click()
document.body.removeChild(a)
URL.revokeObjectURL(url)
}

setShowExportMenu(false)
}

const generateTextReport = (analysis) => {
const data = analysis.data
const lines = [
'═══════════════════════════════════════════════════════════════',
' DevEase Code Analysis Report ',
'═══════════════════════════════════════════════════════════════',
'',
`File: ${analysis.fileName}`,
`Date: ${new Date(analysis.timestamp).toLocaleString()}`,
`Language: ${data.language || 'Unknown'}`,
'',
'───────────────────────────────────────────────────────────────',
' QUALITY SCORE ',
'───────────────────────────────────────────────────────────────',
'',
`Overall Score: ${data.quality_score?.overall_score?.toFixed(1) || 'N/A'} / 100`,
`Maintainability: ${data.quality_score?.maintainability?.toFixed(1) || 'N/A'}`,
`Readability: ${data.quality_score?.readability?.toFixed(1) || 'N/A'}`,
`Complexity: ${data.quality_score?.complexity?.toFixed(1) || 'N/A'}`,
`Documentation: ${data.quality_score?.documentation?.toFixed(1) || 'N/A'}`,
'',
'───────────────────────────────────────────────────────────────',
' TECHNICAL DEBT ',
'───────────────────────────────────────────────────────────────',
'',
`Total Debt Score: ${data.technical_debt?.total_debt_score?.toFixed(1) || 'N/A'}`,
`Debt Level: ${data.technical_debt?.debt_level || 'N/A'}`,
`Estimated Fix Time: ${data.technical_debt?.estimated_hours?.toFixed(1) || 'N/A'} hours`,
'',
'───────────────────────────────────────────────────────────────',
' CODE SMELLS ',
'───────────────────────────────────────────────────────────────',
'',
`Total Smells: ${data.code_smells?.total_smells || 0}`,
''
]

// Add each smell
if (data.code_smells?.smells) {
data.code_smells.smells.forEach((smell, idx) => {
lines.push(`${idx + 1}. [${smell.severity?.toUpperCase()}] ${smell.type?.replace(/_/g, ' ')}`)
lines.push(` Line: ${smell.line}`)
lines.push(` Description: ${smell.description}`)
if (smell.suggestion) {
lines.push(` Suggestion: ${smell.suggestion}`)
}
lines.push('')
})
}

lines.push('───────────────────────────────────────────────────────────────')
lines.push(' RECOMMENDATIONS ')
lines.push('───────────────────────────────────────────────────────────────')
lines.push('')

if (data.technical_debt?.recommendations) {
data.technical_debt.recommendations.forEach((rec, idx) => {
lines.push(`${idx + 1}. ${rec}`)
})
}

lines.push('')
lines.push('═══════════════════════════════════════════════════════════════')
lines.push(' Generated by DevEase AI ')
lines.push('═══════════════════════════════════════════════════════════════')

return lines.join('\n')
}

const generateCSV = (analysis) => {
const data = analysis.data
const lines = ['Severity,Type,Line,Description,Suggestion']

if (data.code_smells?.smells) {
data.code_smells.smells.forEach(smell => {
const row = [
smell.severity || '',
(smell.type || '').replace(/_/g, ' '),
smell.line || '',
`"${(smell.description || '').replace(/"/g, '""')}"`,
`"${(smell.suggestion || '').replace(/"/g, '""')}"`
]
lines.push(row.join(','))
})
}

return lines.join('\n')
}

const navigation = [
{ name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
{ name: 'Projects', href: '/projects', icon: FolderIcon },
{ name: 'Analysis History', href: '/history', icon: BookOpenIcon },
{ name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
{ name: 'Profile', href: '/profile', icon: UserIcon },
]

const isActive = (path) => location.pathname === path

return (
<div className="min-h-screen cyber-bg">
{/* Top Navigation Bar */}
<nav className="theme-bg-secondary border-b theme-border sticky top-0 z-50">
<div className="px-4 sm:px-6 lg:px-8">
<div className="flex items-center h-16">
{/* Logo - positioned to align with sidebar */}
<Link to="/" className="flex items-center space-x-2 w-64 shrink-0">
<div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center glow-cyan">
<span className="theme-text-primary font-bold text-xl">D</span>
</div>
<span className="text-xl font-bold theme-text-primary">DevEase</span>
</Link>

{/* Right side actions */}
<div className="flex items-center space-x-4 ml-auto">
<Link
to="/history"
className="flex items-center space-x-2 px-3 py-2 rounded-lg theme-hover-bg transition-colors theme-nav-link"
>
<BookOpenIcon className="w-5 h-5" />
<span className="hidden sm:inline">History</span>
</Link>

<div className="relative" ref={exportMenuRef}>
<button
onClick={() => setShowExportMenu(!showExportMenu)}
className="flex items-center space-x-2 px-3 py-2 rounded-lg theme-hover-bg transition-colors theme-nav-link"
>
<ArrowDownIcon className="w-5 h-5" />
<span className="hidden sm:inline">Export</span>
</button>

{/* Export Dropdown Menu */}
{showExportMenu && (
<div className="absolute right-0 mt-2 w-48 bg-[#1c2128] border border-[#30363d] rounded-lg shadow-xl z-50">
<div className="py-1">
<button
onClick={() => exportAnalysis('json')}
className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#30363d] flex items-center space-x-2"
>
<span className="text-cyan-400">{'{ }'}</span>
<span>Export as JSON</span>
</button>
<button
onClick={() => exportAnalysis('txt')}
className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#30363d] flex items-center space-x-2"
>
<span className="text-green-400">📄</span>
<span>Export as Report (TXT)</span>
</button>
<button
onClick={() => exportAnalysis('csv')}
className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#30363d] flex items-center space-x-2"
>
<span className="text-yellow-400">📊</span>
<span>Export Smells (CSV)</span>
</button>
</div>
</div>
)}
</div>

<Link
to="/settings"
className="flex items-center space-x-2 px-3 py-2 rounded-lg theme-hover-bg transition-colors theme-nav-link"
>
<UserCircleIcon className="w-5 h-5" />
<span className="hidden sm:inline">Accessibility</span>
</Link>

{user && (
<button
onClick={() => {
logoutUser()
window.location.href = '/'
}}
className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-[var(--bg-card)] transition-colors text-red-400 hover:text-red-300"
>
<ArrowRightOnRectangleIcon className="w-5 h-5" />
<span className="hidden sm:inline">Logout</span>
</button>
)}
</div>
</div>
</div>
</nav>

{/* Main Content */}
<div className="flex">
{/* Sidebar Navigation */}
<aside className="w-64 theme-bg-secondary border-r theme-border min-h-[calc(100vh-4rem)] hidden lg:block">
<nav className="p-4 space-y-2">
{navigation.map((item) => {
const Icon = item.icon
const active = isActive(item.href)
return (
<Link
key={item.name}
to={item.href}
className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${active
? 'bg-[var(--bg-card)] text-cyan-400 border-l-4 border-cyan-400'
: 'theme-nav-link theme-hover-bg'
}`}
>
<Icon className="w-5 h-5" />
<span className="font-medium">{item.name}</span>
</Link>
)
})}
</nav>
</aside>

{/* Main Content Area */}
<main className="flex-1">
{children}
</main>
</div>
</div>
)
}

export default Layout