import React from 'react'

function TestApp() {
  return (
    <div style={{
      padding: '40px',
      background: '#0a0e27',
      color: 'white',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#00d9ff', fontSize: '32px', marginBottom: '20px' }}>
        ✅ React is Working!
      </h1>
      <p style={{ fontSize: '18px', color: '#a0aec0' }}>
        If you can see this, React is rendering correctly.
      </p>
      <div style={{ marginTop: '30px', padding: '20px', background: '#1a2332', borderRadius: '8px' }}>
        <p style={{ color: '#10b981' }}>✅ CSS Variables are working</p>
        <p style={{ color: '#3b82f6' }}>✅ JavaScript is executing</p>
        <p style={{ color: '#f59e0b' }}>✅ React is mounted</p>
      </div>
    </div>
  )
}

export default TestApp
