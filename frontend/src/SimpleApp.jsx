import React from 'react'

function SimpleApp() {
  return (
    <div style={{
      padding: '40px',
      background: '#0a0e27',
      color: 'white',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#00d9ff', fontSize: '48px', marginBottom: '20px' }}>
        ✅ DevEase Frontend is Working!
      </h1>
      <p style={{ fontSize: '24px', color: '#10b981', marginBottom: '30px' }}>
        Your frontend is successfully running!
      </p>
      <div style={{ padding: '20px', background: '#1a2332', borderRadius: '8px', marginTop: '20px' }}>
        <p style={{ color: '#3b82f6', marginBottom: '10px' }}>✅ React is rendering</p>
        <p style={{ color: '#3b82f6', marginBottom: '10px' }}>✅ CSS is loading</p>
        <p style={{ color: '#3b82f6' }}>✅ JavaScript is executing</p>
      </div>
      <p style={{ marginTop: '30px', color: '#a0aec0' }}>
        Now let's load the full app...
      </p>
    </div>
  )
}

export default SimpleApp
