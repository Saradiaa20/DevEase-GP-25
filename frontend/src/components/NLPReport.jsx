import React, { useState } from 'react'
import { jsPDF } from 'jspdf'

function InlineMarkdown({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g)
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i} className="text-white font-medium">{part.slice(2, -2)}</strong>
        }
        if (part.startsWith('*') && part.endsWith('*')) {
          return <em key={i} className="text-gray-400 italic">{part.slice(1, -1)}</em>
        }
        return <span key={i}>{part}</span>
      })}
    </>
  )
}

function MarkdownText({ text }) {
  if (!text) return null
  const lines = text.split('\n')
  const elements = []
  let key = 0

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i]

    if (/^---+$/.test(line.trim())) {
      elements.push(<hr key={key} className="border-[#2d3748] my-2" />)
      key += 1
      continue
    }

    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={key} className="text-base font-semibold text-cyan-400 mt-4 mb-1">
          {line.slice(3)}
        </h2>
      )
      key += 1
      continue
    }

    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={key} className="text-sm font-semibold text-cyan-300 mt-3 mb-1">
          {line.slice(4)}
        </h3>
      )
      key += 1
      continue
    }

    if (/^\s*- /.test(line)) {
      elements.push(
        <li key={key} className="ml-4 text-sm text-gray-300 leading-relaxed list-disc">
          <InlineMarkdown text={line.replace(/^\s*- /, '')} />
        </li>
      )
      key += 1
      continue
    }

    if (line.trim() === '') {
      elements.push(<div key={key} className="h-2" />)
      key += 1
      continue
    }

    elements.push(
      <p key={key} className="text-sm text-gray-300 leading-relaxed">
        <InlineMarkdown text={line} />
      </p>
    )
    key += 1
  }

  return <div className="space-y-1">{elements}</div>
}

function SectionBadge({ label, color = 'cyan' }) {
  const colors = {
    cyan: 'bg-cyan-900/40 text-cyan-300 border border-cyan-800',
    amber: 'bg-amber-900/40 text-amber-300 border border-amber-800',
    red: 'bg-red-900/40 text-red-300 border border-red-800',
    green: 'bg-green-900/40 text-green-300 border border-green-800',
    purple: 'bg-purple-900/40 text-purple-300 border border-purple-800',
    blue: 'bg-blue-900/40 text-blue-300 border border-blue-800',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[color] || colors.cyan}`}>
      {label}
    </span>
  )
}

function ReportSection({ title, badge, badgeColor, content, defaultOpen = false, icon }) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="border border-[#2d3748] rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((value) => !value)}
        className="w-full flex items-center justify-between px-4 py-3 bg-[#1a2332] hover:bg-[#1e293b] transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon && <span className="text-base">{icon}</span>}
          <span className="text-sm font-semibold text-gray-200">{title}</span>
          {badge && <SectionBadge label={badge} color={badgeColor} />}
        </div>
        <span className="text-gray-500 text-xs">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="px-4 py-3 bg-[#0f1623] border-t border-[#2d3748]">
          <MarkdownText text={content} />
        </div>
      )}
    </div>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }
  return (
    <button
      onClick={handleCopy}
      className="text-xs px-3 py-1 rounded bg-[#2d3748] hover:bg-[#374151] text-gray-300 transition-colors"
    >
      {copied ? '✓ Copied' : 'Copy report'}
    </button>
  )
}

function DownloadPdfButton({ text, generatedAt }) {
  const [downloading, setDownloading] = useState(false)

  const toPlainText = (input) => (
    (input || '')
      .replace(/^#+\s/gm, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/^- /gm, '• ')
      .replace(/---+/g, '\n')
  )

  const handleDownload = () => {
    try {
      setDownloading(true)
      const doc = new jsPDF({ unit: 'pt', format: 'a4' })
      const pageWidth = doc.internal.pageSize.getWidth()
      const pageHeight = doc.internal.pageSize.getHeight()
      const margin = 40
      const maxWidth = pageWidth - margin * 2
      let y = margin

      const title = 'DevEase AI NLP Report'
      const generatedLabel = generatedAt
        ? `Generated: ${new Date(generatedAt).toLocaleString()}`
        : `Generated: ${new Date().toLocaleString()}`

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(16)
      doc.text(title, margin, y)
      y += 24

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(10)
      doc.text(generatedLabel, margin, y)
      y += 22

      const plainText = toPlainText(text)
      doc.setFontSize(11)
      const lines = doc.splitTextToSize(plainText, maxWidth)

      lines.forEach((line) => {
        if (y > pageHeight - margin) {
          doc.addPage()
          y = margin
        }
        doc.text(line, margin, y)
        y += 16
      })

      doc.save(`devease_nlp_report_${new Date().toISOString().slice(0, 10)}.pdf`)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <button
      onClick={handleDownload}
      className="text-xs px-3 py-1 rounded bg-cyan-700/80 hover:bg-cyan-600 text-white transition-colors"
      disabled={downloading}
    >
      {downloading ? 'Generating PDF...' : 'Download PDF'}
    </button>
  )
}

export default function NLPReport({ nlpReport }) {
  const [view, setView] = useState('sections')

  if (!nlpReport) {
    return (
      <div className="text-gray-500 text-sm italic p-4 text-center">
        No NLP report available for this analysis.
      </div>
    )
  }

  const {
    summary,
    overview,
    quality,
    code_smells: codeSmells,
    technical_debt: technicalDebt,
    complexity,
    design_patterns: designPatterns,
    full_report: fullReport,
    generated_at: generatedAt,
  } = nlpReport

  const sections = [
    { key: 'overview', title: 'Code Overview', icon: '🔍', content: overview, defaultOpen: true },
    { key: 'quality', title: 'Quality Metrics', icon: '📊', content: quality, defaultOpen: true },
    { key: 'smells', title: 'Code Smells', icon: '🧪', content: codeSmells, badgeColor: 'amber' },
    { key: 'debt', title: 'Technical Debt', icon: '💳', content: technicalDebt, badgeColor: 'red' },
    {
      key: 'complexity',
      title: 'Complexity Analysis',
      icon: '🤖',
      content: complexity,
      badge: 'ML-powered',
      badgeColor: 'purple',
    },
    { key: 'patterns', title: 'Design Patterns', icon: '🏗️', content: designPatterns, badgeColor: 'blue' },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white">AI Analysis Report</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Plain-English explanation of all analysis results
            {generatedAt && ` · Generated ${new Date(generatedAt).toLocaleTimeString()}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded overflow-hidden border border-[#2d3748] text-xs">
            <button
              onClick={() => setView('sections')}
              className={`px-3 py-1 transition-colors ${view === 'sections' ? 'bg-cyan-900/50 text-cyan-300' : 'bg-[#1a2332] text-gray-400 hover:text-gray-200'}`}
            >
              Sections
            </button>
            <button
              onClick={() => setView('full')}
              className={`px-3 py-1 transition-colors ${view === 'full' ? 'bg-cyan-900/50 text-cyan-300' : 'bg-[#1a2332] text-gray-400 hover:text-gray-200'}`}
            >
              Full report
            </button>
          </div>
          {fullReport && <CopyButton text={fullReport} />}
          {fullReport && <DownloadPdfButton text={fullReport} generatedAt={generatedAt} />}
        </div>
      </div>

      {summary && (
        <div className="rounded-lg border border-cyan-800/50 bg-cyan-900/10 px-4 py-3">
          <p className="text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wide">
            Summary
          </p>
          <p className="text-sm text-gray-200 leading-relaxed">
            <InlineMarkdown text={summary} />
          </p>
        </div>
      )}

      {view === 'sections' && (
        <div className="space-y-2">
          {sections.map((section) => (
            <ReportSection
              key={section.key}
              title={section.title}
              icon={section.icon}
              badge={section.badge}
              badgeColor={section.badgeColor}
              content={section.content}
              defaultOpen={section.defaultOpen}
            />
          ))}
        </div>
      )}

      {view === 'full' && fullReport && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4">
          <MarkdownText text={fullReport} />
        </div>
      )}
    </div>
  )
}
