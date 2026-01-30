import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { ArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

function FileUpload({ onFileUpload, onContentAnalysis, loading }) {
  const [content, setContent] = useState('')
  const [showContentInput, setShowContentInput] = useState(false)

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0])
    }
  }, [onFileUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.py', '.java', '.js', '.cpp', '.cs', '.php'],
    },
    maxFiles: 1,
    disabled: loading
  })

  const handleContentSubmit = (e) => {
    e.preventDefault()
    if (content.trim()) {
      onContentAnalysis(content)
    }
  }

  return (
    <div className="space-y-4">
      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={() => setShowContentInput(!showContentInput)}
          className="px-4 py-2 bg-[#1a2332] border border-[#2d3748] text-gray-300 rounded-lg hover:bg-[#202835] hover:border-cyan-500/50 transition-all"
        >
          <DocumentTextIcon className="w-5 h-5 inline mr-2" />
          Paste Code
        </button>
        <button
          onClick={() => document.querySelector('input[type="file"]')?.click()}
          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all"
        >
          <ArrowUpIcon className="w-5 h-5 inline mr-2" />
          Upload File
        </button>
      </div>

      {/* Drag & Drop Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-cyan-500 bg-cyan-500/10'
            : 'border-[#2d3748] hover:border-cyan-500/50 hover:bg-[#202835]'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="text-6xl mb-4">📁</div>
        {isDragActive ? (
          <p className="text-cyan-400 font-medium">Drop the file here...</p>
        ) : (
          <>
            <p className="text-gray-300 mb-2">
              Drag & drop your Python file here
            </p>
            <p className="text-gray-500 mb-4">or</p>
            <button className="px-4 py-2 bg-[#1a2332] border border-[#2d3748] text-gray-300 rounded-lg hover:bg-[#202835] hover:border-cyan-500/50 transition-all">
              Browse Files
            </button>
          </>
        )}
      </div>

      {/* Code Paste Input */}
      {showContentInput && (
        <form onSubmit={handleContentSubmit} className="space-y-3">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your code here..."
            className="w-full h-48 p-4 bg-[#202835] border border-[#2d3748] rounded-lg focus:outline-none focus:border-cyan-500 font-mono text-sm text-gray-300 placeholder-gray-500"
            disabled={loading}
          />
          <div className="flex space-x-2">
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowContentInput(false)
                setContent('')
              }}
              className="px-4 py-2 bg-[#1a2332] border border-[#2d3748] text-gray-300 rounded-lg hover:bg-[#202835] transition-colors"
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
          <p className="mt-2 text-gray-400">Analyzing code...</p>
        </div>
      )}
    </div>
  )
}

export default FileUpload
