// frontend/src/pages/WrapperGenerator.jsx
// Wrapper Generator full page — upload or paste code, see unsafe patterns,
// read AI-generated suggestions, accept or dismiss each one.

import React, { useState, useRef } from 'react'
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
  CheckCircleIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  SparklesIcon,
  CodeBracketIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline'
import { analyzeFileForWrappers, analyzeContentForWrappers } from '../services/wrapperApi'

// ─── Severity config (matches project's colour palette) ──────────────────────

const SEV = {
  high:   { ring: 'border-red-500',    bg: 'bg-red-900/20',    text: 'text-red-400',    label: 'HIGH'   },
  medium: { ring: 'border-yellow-500', bg: 'bg-yellow-900/20', text: 'text-yellow-400', label: 'MEDIUM' },
  low:    { ring: 'border-blue-500',   bg: 'bg-blue-900/20',   text: 'text-blue-400',   label: 'LOW'    },
}

function SeverityBadge({ severity }) {
  const c = SEV[severity] || SEV.low
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${c.ring} ${c.text} ${c.bg}`}>
      {c.label}
    </span>
  )
}

// ─── Single suggestion card ───────────────────────────────────────────────────

function SuggestionCard({ s, onAccept, onDismiss, accepted }) {
  const [open,   setOpen]   = useState(true)
  const [copied, setCopied] = useState(false)
  const c = SEV[s.severity] || SEV.low

  const copy = () => {
    navigator.clipboard.writeText(s.wrapped_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`rounded-xl border ${c.ring} ${c.bg} mb-4 overflow-hidden`}>
      {/* header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer select-none"
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex items-center gap-3 min-w-0">
          <SparklesIcon className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span className="font-semibold text-white text-sm truncate">{s.suggestion_title}</span>
          <SeverityBadge severity={s.severity} />
          <span className="text-xs text-gray-500 flex-shrink-0">line {s.line_number}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {accepted && (
            <span className="text-xs text-green-400 font-semibold flex items-center gap-1">
              <CheckCircleIcon className="w-4 h-4" /> Applied
            </span>
          )}
          {open
            ? <ChevronUpIcon   className="w-4 h-4 text-gray-400" />
            : <ChevronDownIcon className="w-4 h-4 text-gray-400" />}
        </div>
      </div>

      {open && (
        <div className="px-4 pb-4 space-y-4">
          {/* explanation */}
          <p className="text-sm text-gray-300 leading-relaxed">{s.explanation}</p>

          {/* changes list */}
          {s.changes_made?.length > 0 && (
            <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
              {s.changes_made.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          )}

          {/* side-by-side diff */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-red-400 font-semibold mb-1 flex items-center gap-1">
                <XMarkIcon className="w-3 h-3" /> Original (unsafe)
              </p>
              <pre className="bg-[#0a0e27] rounded-lg p-3 text-xs text-red-300 overflow-x-auto whitespace-pre-wrap break-words border border-red-900/50 max-h-64">
                {s.original_code}
              </pre>
            </div>
            <div>
              <p className="text-xs text-green-400 font-semibold mb-1 flex items-center gap-1">
                <CheckCircleIcon className="w-3 h-3" /> Suggested (safer)
              </p>
              <pre className="bg-[#0a0e27] rounded-lg p-3 text-xs text-green-300 overflow-x-auto whitespace-pre-wrap break-words border border-green-900/50 max-h-64">
                {s.wrapped_code}
              </pre>
            </div>
          </div>

          {/* action buttons */}
          {!accepted && (
            <div className="flex gap-3 pt-1">
              <button
                onClick={() => onAccept(s)}
                className="flex-1 py-2 rounded-lg bg-cyan-400/10 hover:bg-cyan-400/20 text-cyan-400 text-sm font-semibold border border-cyan-400/30 transition-colors"
              >
                {s.accept_label || 'Apply Suggestion'}
              </button>
              <button
                onClick={copy}
                className="px-4 py-2 rounded-lg bg-[#1e2a3a] hover:bg-[#263444] text-gray-300 text-sm transition-colors flex items-center gap-1"
              >
                <ClipboardDocumentIcon className="w-4 h-4" />
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button
                onClick={() => onDismiss(s.pattern_id)}
                className="px-4 py-2 rounded-lg bg-[#1a2332] hover:bg-[#1e2a3a] text-gray-500 text-sm transition-colors"
              >
                {s.dismiss_label || 'Keep Original'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Pattern summary row ─────────────────────────────────────────────────────

function PatternRow({ p }) {
  const c = SEV[p.severity] || SEV.low
  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${c.ring} ${c.bg} mb-2`}>
      <ExclamationTriangleIcon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${c.text}`} />
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1">
          <SeverityBadge severity={p.severity} />
          <span className="text-xs text-gray-400">Line {p.line_number}</span>
          <code className="text-xs text-gray-500 truncate">{p.pattern_type}</code>
        </div>
        <p className="text-xs text-gray-300 leading-relaxed">{p.description}</p>
      </div>
    </div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function WrapperGenerator() {
  const [mode,      setMode]      = useState('upload')   // 'upload' | 'paste'
  const [paste,     setPaste]     = useState('')
  const [lang,      setLang]      = useState('')
  const [dragOver,  setDragOver]  = useState(false)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [result,    setResult]    = useState(null)
  const [accepted,  setAccepted]  = useState({})
  const [dismissed, setDismissed] = useState({})

  const fileRef = useRef()

  const reset = () => {
    setResult(null); setError(null); setPaste('')
    setAccepted({}); setDismissed({})
    if (fileRef.current) fileRef.current.value = ''
  }

  const run = async (fn) => {
    setLoading(true); setError(null); setResult(null)
    setAccepted({}); setDismissed({})
    try   { setResult(await fn()) }
    catch (e) { setError(e.response?.data?.detail || e.message || 'Analysis failed') }
    finally   { setLoading(false) }
  }

  const handleFile = (file) => {
    if (file) run(() => analyzeFileForWrappers(file))
  }

  const handlePaste = () => {
    if (!paste.trim()) { setError('Please paste some code first.'); return }
    run(() => analyzeContentForWrappers(paste, lang || null))
  }

  return (
    <div className="min-h-screen bg-[#0a0e27] text-white p-6">

      {/* ── Page header ── */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-xl bg-cyan-400/10 border border-cyan-400/20">
            <ShieldCheckIcon className="w-7 h-7 text-cyan-400" />
          </div>
          <h1 className="text-2xl font-bold theme-text-primary">Wrapper Generator</h1>
        </div>
        <p className="text-gray-400 text-sm max-w-2xl">
          Upload or paste your code. DevEase detects unsafe patterns via AST analysis, then uses
          Groq AI to suggest a safer wrapped version — tailored to your exact code, not a template.
          You choose whether to apply or keep the original.
        </p>
      </div>

      {/* ── Input section ── */}
      {!result && (
        <div className="max-w-3xl">

          {/* Mode toggle */}
          <div className="flex gap-2 mb-6">
            {[['upload','↑ Upload File'],['paste','</> Paste Code']].map(([m, label]) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-5 py-2 rounded-lg text-sm font-semibold transition-colors ${
                  mode === m
                    ? 'bg-cyan-400 text-[#0a0e27]'
                    : 'bg-[#1a2332] text-gray-300 hover:bg-[#1e2a3a]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Upload drop zone */}
          {mode === 'upload' && (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
              onClick={() => fileRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                dragOver
                  ? 'border-cyan-400 bg-cyan-400/5'
                  : 'border-gray-600 hover:border-gray-500 bg-[#1a2332]/50'
              }`}
            >
              <ArrowUpTrayIcon className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <p className="text-gray-300 font-medium mb-1">Drop your file here or click to browse</p>
              <p className="text-gray-500 text-sm">.py and .java files supported</p>
              <input
                ref={fileRef} type="file" accept=".py,.java" className="hidden"
                onChange={e => handleFile(e.target.files[0])}
              />
            </div>
          )}

          {/* Paste mode */}
          {mode === 'paste' && (
            <div className="space-y-4">
              <select
                value={lang} onChange={e => setLang(e.target.value)}
                className="bg-[#1a2332] border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-400"
              >
                <option value="">Auto-detect language</option>
                <option value="Python">Python</option>
                <option value="Java">Java</option>
              </select>
              <textarea
                value={paste} onChange={e => setPaste(e.target.value)}
                placeholder="# Paste your Python or Java code here…"
                className="w-full h-80 bg-[#0a0e27] border border-gray-600 rounded-xl p-4 text-sm text-gray-200 font-mono focus:outline-none focus:border-cyan-400 resize-none"
              />
              <button
                onClick={handlePaste} disabled={loading}
                className="w-full py-3 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-[#0a0e27] font-bold text-sm transition-colors disabled:opacity-50"
              >
                {loading ? 'Analysing…' : 'Analyse Code'}
              </button>
            </div>
          )}

          {loading && (
            <div className="mt-6 flex items-center gap-3 text-cyan-400 animate-pulse">
              <SparklesIcon className="w-5 h-5" />
              <span className="text-sm">Detecting unsafe patterns and generating suggestions…</span>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-red-900/20 border border-red-500 text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
      )}

      {/* ── Results section ── */}
      {result && (
        <div className="max-w-5xl">

          {/* Result header */}
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div className="flex items-center gap-3">
              {result.patterns_found === 0
                ? <CheckCircleIcon className="w-6 h-6 text-green-400" />
                : <ExclamationTriangleIcon className="w-6 h-6 text-yellow-400" />}
              <div>
                <h2 className="font-bold text-lg">
                  {result.patterns_found === 0
                    ? 'No unsafe patterns found'
                    : `${result.patterns_found} unsafe pattern${result.patterns_found > 1 ? 's' : ''} detected`}
                </h2>
                <p className="text-gray-400 text-sm">{result.message}</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-[#1a2332] border border-gray-600 text-xs text-gray-300">
                {result.language}
              </span>
            </div>
            <button
              onClick={reset}
              className="px-4 py-2 rounded-lg bg-[#1a2332] hover:bg-[#1e2a3a] text-gray-300 text-sm transition-colors"
            >
              ← Analyse Another File
            </button>
          </div>

          {result.patterns_found === 0 ? (
            <div className="p-8 rounded-xl border border-green-500/30 bg-green-900/10 text-center">
              <CheckCircleIcon className="w-12 h-12 mx-auto mb-3 text-green-400" />
              <p className="text-green-300 font-medium mb-1">All clear!</p>
              <p className="text-gray-400 text-sm">
                No unsafe patterns (bare API calls, missing try/catch, unclosed resources) were detected.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* Left: pattern list */}
              <div className="lg:col-span-1">
                <h3 className="font-semibold text-sm text-gray-300 mb-3 flex items-center gap-2">
                  <CodeBracketIcon className="w-4 h-4" /> Detected Patterns
                </h3>
                {result.patterns.map(p => (
                  <PatternRow key={p.pattern_id} p={p} />
                ))}
              </div>

              {/* Right: suggestions */}
              <div className="lg:col-span-2">
                <h3 className="font-semibold text-sm text-gray-300 mb-3 flex items-center gap-2">
                  <SparklesIcon className="w-4 h-4 text-cyan-400" /> AI-Generated Suggestions
                  <span className="text-xs text-gray-500 font-normal">(Groq · llama-3.3-70b)</span>
                </h3>
                {result.suggestions
                  .filter(s => !dismissed[s.pattern_id])
                  .map(s => (
                    <SuggestionCard
                      key={s.pattern_id}
                      s={s}
                      onAccept={(s) => setAccepted(p => ({ ...p, [s.pattern_id]: true }))}
                      onDismiss={(id) => setDismissed(p => ({ ...p, [id]: true }))}
                      accepted={!!accepted[s.pattern_id]}
                    />
                  ))}
                {result.suggestions.every(s => dismissed[s.pattern_id]) && (
                  <p className="text-gray-500 text-sm">All suggestions dismissed.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
