import React, { useMemo, useState } from 'react'
import {
  ArrowDownTrayIcon,
  ClipboardDocumentIcon,
  CodeBracketSquareIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import { generateFixedCode } from '../services/api'

function formatApiError(err) {
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(', ')
  }
  return err.message || 'Fixed code generation failed'
}

function extensionForLanguage(language = '') {
  const normalized = language.toLowerCase()
  if (normalized === 'java') return '.java'
  if (normalized === 'python') return '.py'
  return '.txt'
}

function fixedFileName(fileName, language) {
  const fallback = `fixed_code${extensionForLanguage(language)}`
  if (!fileName) return fallback

  const cleanName = fileName.split(/[\\/]/).pop()
  const match = cleanName.match(/^(.*?)(\.[^.]+)?$/)
  const base = match?.[1] || 'fixed_code'
  const ext = match?.[2] || extensionForLanguage(language)
  return `${base}.fixed${ext}`
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
      type="button"
      onClick={handleCopy}
      disabled={!text}
      className="text-xs px-3 py-1 rounded bg-[#2d3748] hover:bg-[#374151] disabled:opacity-50 disabled:cursor-not-allowed text-gray-300 transition-colors inline-flex items-center gap-1.5"
    >
      <ClipboardDocumentIcon className="w-4 h-4" />
      {copied ? 'Copied' : 'Copy code'}
    </button>
  )
}

function DownloadButton({ code, fileName }) {
  const handleDownload = () => {
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <button
      type="button"
      onClick={handleDownload}
      disabled={!code}
      className="text-xs px-3 py-1 rounded bg-cyan-700/80 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-colors inline-flex items-center gap-1.5"
    >
      <ArrowDownTrayIcon className="w-4 h-4" />
      Download file
    </button>
  )
}

export default function FixedCode({ data, fileName }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const language = data?.language || 'Python'
  const sourceCode = data?.code_content || ''
  const outputFileName = useMemo(
    () => fixedFileName(fileName, result?.language || language),
    [fileName, language, result?.language]
  )
const cleanedCode = result?.fixed_code
  ?.replace(/```python/g, '')
  ?.replace(/```/g, '')
  ?.trim()

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await generateFixedCode({
        analysisData: data,
        codeContent: sourceCode,
        language,
        fileName,
      })
      setResult(response)
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-base font-bold text-white">Fixed Code</h2>
          <p className="text-sm text-gray-400 mt-1">
AI-improved code generated from the current analysis    </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {result?.fixed_code && <CopyButton text={result.fixed_code} />}
          {result?.fixed_code && (
            <DownloadButton code={result.fixed_code} fileName={outputFileName} />
          )}
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading || !sourceCode}
           className="text-sm px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-all duration-300 hover:scale-[1.02] inline-flex items-center gap-2 font-semibold"        >
            <SparklesIcon className="w-4 h-4" />
{loading ? 'Improving...' : result ? 'Generate New Fix' : 'Improve Code'}          </button>
        </div>
      </div>

      {!sourceCode && (
        <div className="rounded-lg border border-[#2d3748] bg-[#0f1623]/50 px-4 py-3 text-sm text-gray-500">
          Source code is not available for fixed-code generation.
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-3">
          <p className="text-xs font-semibold text-red-400 mb-1 uppercase tracking-wide">Error</p>
          <p className="text-sm text-gray-200 leading-relaxed">{error}</p>
        </div>
      )}

      {!result && !error && (
        <div className="rounded-2xl border border-cyan-500/20 bg-[#071426] backdrop-blur-sm px-4 py-3">
          <div className="flex items-start gap-3">
<CodeBracketSquareIcon className="w-6 h-6 text-cyan-400 shrink-0 mt-0.5" />            <p className="text-sm text-gray-200 leading-relaxed">
             Generate an improved and safer version of your code using AI-assisted analysis.
            </p>
          </div>
        </div>
      )}

      {result && (
        <>
          {/* <div className="rounded-lg border border-cyan-800/50 bg-cyan-900/10 px-4 py-3">
            <div className="flex items-center justify-between gap-3 flex-wrap mb-2">
              <p className="text-xs font-semibold text-cyan-400 uppercase tracking-wide">
                Generated fix
              </p>
              <span className="text-xs text-gray-500">
                {result.model} | confidence {result.confidence}
              </span>
            </div>
            <p className="text-sm text-gray-200 leading-relaxed">{result.summary}</p>
          </div> */}

          {result.changes?.length > 0 && (
            <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] px-5 py-4">
              <p className="text-xs font-semibold text-cyan-400 mb-2 uppercase tracking-wide">
                Exact changes made
              </p>
              <ul className="text-sm text-gray-300 space-y-3">
                {result.changes.map((change, index) => (
                  <li key={`${JSON.stringify(change)}-${index}`} className="list-none">
                    {typeof change === 'string' ? (
                      <p>{change}</p>
                    ) : (
                      <div className="space-y-1">
                        <p className="font-medium text-gray-200">{change.change}</p>
                        {change.why_behavior_is_preserved && (
                          <p className="text-xs text-gray-400 leading-relaxed">
                            Behavior preserved: {change.why_behavior_is_preserved}
                          </p>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.not_fixed?.length > 0 && (
            <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-5 py-4">
              <p className="text-xs font-semibold text-amber-300 mb-2 uppercase tracking-wide">
                Issues not fixed due to behavior risk
              </p>
              <ul className="text-sm text-gray-300 space-y-3">
                {result.not_fixed.map((item, index) => (
                  <li key={`${JSON.stringify(item)}-${index}`} className="list-none">
                    {typeof item === 'string' ? (
                      <p>{item}</p>
                    ) : (
                      <div className="space-y-1">
                        <p className="font-medium text-gray-200">{item.issue}</p>
                        {item.reason && (
                          <p className="text-xs text-gray-400 leading-relaxed">
                            Reason: {item.reason}
                          </p>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="rounded-lg border border-[#2d3748] bg-[#0f1623] overflow-hidden">
            <div className="flex items-center justify-between gap-3 flex-wrap border-b border-[#2d3748] bg-[#1a2332] px-4 py-2">
              <span className="text-xs text-gray-400">{outputFileName}</span>
              <span className="text-xs px-3 py-1 rounded-full border border-cyan-800/50 bg-cyan-900/20 text-cyan-300">
                {result.language || language}
              </span>
            </div>
            <pre className="max-h-[560px] overflow-auto p-4 text-sm text-gray-300 font-mono leading-relaxed whitespace-pre">
            <code>{cleanedCode}</code>    
        </pre>
          </div>
        </>
      )}
    </div>
  )
}
