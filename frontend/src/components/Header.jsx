import React from 'react'

function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">D</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">DevEase</h1>
              <p className="text-sm text-gray-500">Code Complexity Analysis Tool</p>
            </div>
          </div>
          <nav className="flex items-center space-x-4">
            <a href="/" className="text-gray-600 hover:text-gray-900 font-medium">
              Home
            </a>
            <a href="/docs" className="text-gray-600 hover:text-gray-900 font-medium">
              API Docs
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
