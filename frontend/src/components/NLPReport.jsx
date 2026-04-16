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

function DownloadPdfButton({ text }) {
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

      const title = 'DevEase Explanation Report'

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(16)
      doc.text(title, margin, y)
      y += 28

      const plainText = toPlainText(text)
      doc.setFont('helvetica', 'normal')
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
  if (!nlpReport) {
    return (
      <div className="text-gray-500 text-sm italic p-4 text-center">
        No NLP report available for this analysis.
      </div>
    )
  }

  const {
    summary,
    full_report: fullReport,
  } = nlpReport

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white">Explanation Report</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            English explanation of all analysis results (NLP)
          </p>
        </div>
        <div className="flex items-center gap-2">
          {fullReport && <CopyButton text={fullReport} />}
          {fullReport && <DownloadPdfButton text={fullReport} />}
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

      {fullReport && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4">
          <MarkdownText text={fullReport} />
        </div>
      )}

      {!fullReport && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623]/50 px-4 py-3 text-sm text-gray-500">
          Full report text is not available for this analysis.
        </div>
      )}
    </div>
  )
}
