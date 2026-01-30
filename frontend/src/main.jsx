import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import SimpleApp from './SimpleApp'
import './index.css'

const USE_SIMPLE = false // Set to true to test basic rendering

console.log('🚀 Starting DevEase app...')

window.addEventListener('error', (event) => {
  console.error('❌ Global error:', event.error)
  const rootEl = document.getElementById('root')
  if (rootEl && !rootEl.innerHTML.includes('Error')) {
    rootEl.innerHTML = `
      <div style="padding: 40px; color: white; background: #0a0e27; min-height: 100vh; font-family: monospace;">
        <h1 style="color: red; font-size: 32px;">⚠️ JavaScript Error</h1>
        <div style="margin-top: 20px; padding: 20px; background: #1a2332; border-radius: 8px;">
          <pre style="color: #ef4444; white-space: pre-wrap;">${event.error?.toString() || event.message}</pre>
          <pre style="color: #718096; margin-top: 10px; white-space: pre-wrap;">${event.error?.stack || ''}</pre>
        </div>
      </div>
    `
  }
})

try {
  const root = ReactDOM.createRoot(document.getElementById('root'))
  
  if (USE_SIMPLE) {
    console.log('🧪 Using SimpleApp for testing')
    root.render(<React.StrictMode><SimpleApp /></React.StrictMode>)
  } else {
    console.log('🚀 Rendering full App...')
    root.render(<React.StrictMode><App /></React.StrictMode>)
  }
  
  console.log('✅ Render completed')
  
  setTimeout(() => {
    const rootEl = document.getElementById('root')
    if (rootEl && rootEl.children.length === 0) {
      console.error('⚠️ Root is empty!')
      rootEl.innerHTML = `
        <div style="padding: 40px; color: white; background: #0a0e27; min-height: 100vh; font-family: monospace;">
          <h1 style="color: #f59e0b; font-size: 32px;">⚠️ No Content Rendered</h1>
          <p style="color: #a0aec0; margin-top: 20px;">Check console for errors (F12 → Console tab)</p>
        </div>
      `
    }
  }, 1000)
  
} catch (error) {
  console.error('❌ Fatal error:', error)
  const rootEl = document.getElementById('root')
  if (rootEl) {
    rootEl.innerHTML = `
      <div style="padding: 40px; color: white; background: #0a0e27; min-height: 100vh; font-family: monospace;">
        <h1 style="color: red; font-size: 32px;">❌ Fatal Error</h1>
        <pre style="color: #ef4444; white-space: pre-wrap; margin-top: 20px;">${error.toString()}</pre>
        <pre style="color: #718096; white-space: pre-wrap; margin-top: 10px;">${error.stack}</pre>
      </div>
    `
  }
}
