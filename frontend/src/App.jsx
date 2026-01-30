import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { SettingsProvider } from './contexts/SettingsContext'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetails from './pages/ProjectDetails'
import AnalysisHistory from './pages/AnalysisHistory'
import Settings from './pages/Settings'
import Profile from './pages/Profile'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({ errorInfo })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'white', background: '#0a0e27', minHeight: '100vh', fontFamily: 'monospace' }}>
          <h1 style={{ color: 'red', fontSize: '24px', marginBottom: '20px' }}>⚠️ Something went wrong</h1>
          <div style={{ background: '#1a2332', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
            <h2 style={{ color: '#00d9ff', marginBottom: '10px' }}>Error:</h2>
            <pre style={{ color: '#ef4444', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {this.state.error?.toString()}
            </pre>
            {this.state.errorInfo && (
              <details style={{ marginTop: '15px' }}>
                <summary style={{ color: '#a0aec0', cursor: 'pointer' }}>Stack Trace</summary>
                <pre style={{ color: '#718096', marginTop: '10px', whiteSpace: 'pre-wrap' }}>
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  console.log('App component rendering...')
  
  try {
    return (
      <ErrorBoundary>
        <SettingsProvider>
          <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectDetails />} />
            <Route path="/history" element={<AnalysisHistory />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
        </SettingsProvider>
      </ErrorBoundary>
    )
  } catch (error) {
    console.error('App render error:', error)
    console.error('Error stack:', error.stack)
    return (
      <div style={{ padding: '20px', color: 'white', background: '#0a0e27', minHeight: '100vh', fontFamily: 'monospace' }}>
        <h1 style={{ color: 'red', fontSize: '24px' }}>⚠️ Fatal Error in App</h1>
        <div style={{ marginTop: '20px', padding: '15px', background: '#1a2332', borderRadius: '8px' }}>
          <pre style={{ color: '#ef4444', whiteSpace: 'pre-wrap' }}>{error.toString()}</pre>
          <pre style={{ color: '#718096', marginTop: '10px', whiteSpace: 'pre-wrap' }}>{error.stack}</pre>
        </div>
      </div>
    )
  }
}

export default App
