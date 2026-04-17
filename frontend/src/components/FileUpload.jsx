import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { ArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

function FileUpload({ onFileUpload, onContentAnalysis, loading }) {
  const [content, setContent] = useState('')
  /** 'upload' = drag/drop only; 'paste' = textarea only */
  const [inputMode, setInputMode] = useState('upload')

  const isPyOrJava = useCallback((file) => {
    const name = (file?.name || '').toLowerCase()
    return name.endsWith('.py') || name.endsWith('.java')
  }, [])

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileUpload(acceptedFiles[0])
      }
    },
    [onFileUpload]
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    // Avoid `text/*` — on Windows it widens the picker (e.g. Excel, CSV). Lock to extensions + common MIME hints.
    accept: {
      'text/x-python': ['.py'],
      'text/x-java-source': ['.java'],
      'application/x-python-code': ['.py'],
      'application/octet-stream': ['.py', '.java'],
    },
    validator: (file) => (isPyOrJava(file) ? null : { code: 'file-invalid-type', message: 'Only .py and .java files are allowed.' }),
    maxFiles: 1,
    disabled: loading,
  })

  const handleContentSubmit = (e) => {
    e.preventDefault()
    if (content.trim()) {
      onContentAnalysis(content)
    }
  }

  return (
    <div className="space-y-4">
      {/* Keep file input mounted so open() works from "Upload File" (same as old direct picker) */}
      <input
        {...getInputProps({
          // Native filter for the OS file dialog (esp. Windows)
          accept: '.py,.java,.PY,.JAVA',
        })}
        className="sr-only"
        aria-hidden
      />

      {/* Title + mode toggles on one row */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-2xl font-semibold text-white flex items-center min-w-0 tracking-tight">
          <svg className="w-6 h-6 mr-2 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Code Input
        </h2>
        <div className="flex shrink-0 gap-3 flex-wrap justify-end">
          <button
            type="button"
            onClick={() => setInputMode('paste')}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-base transition-all inline-flex items-center ${
              inputMode === 'paste'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                : 'bg-[var(--bg-panel)] border border-[var(--border-primary)] text-gray-300 hover:bg-[var(--bg-card-hover)] hover:border-cyan-500/50'
            }`}
          >
            <DocumentTextIcon className="w-5 h-5 mr-2 shrink-0" />
            Paste Code
          </button>
          <button
            type="button"
            onClick={() => {
              setInputMode('upload')
              window.setTimeout(() => open(), 0)
            }}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-base transition-all inline-flex items-center ${
              inputMode === 'upload'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                : 'bg-[var(--bg-panel)] border border-[var(--border-primary)] text-gray-300 hover:bg-[var(--bg-card-hover)] hover:border-cyan-500/50'
            }`}
          >
            <ArrowUpIcon className="w-5 h-5 mr-2 shrink-0" />
            Upload File
          </button>
        </div>
      </div>

      {inputMode === 'upload' && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg py-20 px-8 min-h-[min(28rem,52vh)] flex flex-col items-center justify-center text-center cursor-pointer transition-all bg-[var(--bg-panel)] ${
            isDragActive
              ? 'border-cyan-500 bg-cyan-500/10'
              : 'border-[var(--border-primary)] hover:border-cyan-500/50 hover:bg-[var(--bg-card-hover)]'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="text-6xl mb-4">📁</div>
          {isDragActive ? (
            <p className="text-cyan-400 font-medium text-base">Drop the file here...</p>
          ) : (
            <>
              <p className="text-gray-300 mb-2 text-base">
                Drag & drop your Python or Java files here
              </p>
              <p className="text-gray-500 mb-4 text-base">or</p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  open()
                }}
                className="px-4 py-2 text-base bg-[var(--bg-panel)] border border-[var(--border-primary)] text-gray-300 rounded-lg hover:bg-[var(--bg-card-hover)] hover:border-cyan-500/50 transition-all"
              >
                Browse Files
              </button>
            </>
          )}
        </div>
      )}

      {inputMode === 'paste' && (
        <form onSubmit={handleContentSubmit} className="space-y-3">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your code here..."
            className="w-full min-h-[min(28rem,52vh)] max-h-[75vh] resize-y p-4 bg-[var(--bg-panel)] border border-[var(--border-primary)] rounded-lg focus:outline-none focus:border-cyan-500 font-mono text-base text-gray-300 placeholder-gray-500"
            disabled={loading}
          />
          <div className="flex justify-center gap-3 flex-wrap">
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="px-4 py-2 text-base bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all inline-flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>
            <button
              type="button"
              onClick={() => {
                setInputMode('upload')
                setContent('')
              }}
              className="px-4 py-2 text-base bg-[var(--bg-panel)] border border-[var(--border-primary)] text-gray-300 rounded-lg hover:bg-[var(--bg-card-hover)] transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      )}


      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
          <p className="mt-2 text-gray-400 text-base">Analyzing code...</p>
        </div>
      )}
    </div>
  )
}

export default FileUpload
