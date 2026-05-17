import { useState } from 'react'
import { useDyslexia } from './DyslexiaContext'

const PRESETS = [
  { label: 'Cream',    color: '#fef9c3' },
  { label: 'Rose',     color: '#fce7f3' },
  { label: 'Mint',     color: '#d1fae5' },
  { label: 'Lavender', color: '#ede9fe' },
  { label: 'Sky',      color: '#e0f2fe' },
  { label: 'Peach',    color: '#ffedd5' },
]

export default function DyslexiaOverlay() {
  const { settings, setSettings } = useDyslexia()
  const [showConfig, setShowConfig] = useState(false)

  if (!settings.enabled || !settings.overlay) return null

  const rgba = hexToRgba(settings.overlayColor, settings.overlayOpacity)

  return (
    <>
      {/* The overlay itself */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: rgba,
          mixBlendMode: 'multiply',
          zIndex: 9000,
          pointerEvents: 'none',
        }}
      />

      {/* Config button */}
      <button
        onClick={() => setShowConfig(!showConfig)}
        title="Colour overlay settings"
        style={{ position: 'fixed', bottom: 80, right: 16, zIndex: 9100 }}
        className="w-8 h-8 rounded-full border-2 shadow-lg"
        style={{
          position: 'fixed', bottom: 80, right: 16, zIndex: 9100,
          width: 32, height: 32, borderRadius: '50%',
          background: settings.overlayColor,
          border: '2px solid #fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          cursor: 'pointer',
        }}
      />

      {showConfig && (
        <div
          style={{ position: 'fixed', bottom: 120, right: 16, zIndex: 9200, width: 220 }}
          className="cyber-card-panel p-3 space-y-3 text-sm"
        >
          <p className="theme-text-primary font-semibold">Overlay colour</p>
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((p) => (
              <button
                key={p.color}
                title={p.label}
                onClick={() => setSettings({ overlayColor: p.color })}
                style={{
                  width: 28, height: 28, borderRadius: '50%',
                  background: p.color,
                  border: settings.overlayColor === p.color ? '2px solid #22d3ee' : '2px solid transparent',
                  cursor: 'pointer',
                }}
              />
            ))}
            <input
              type="color"
              value={settings.overlayColor}
              onChange={(e) => setSettings({ overlayColor: e.target.value })}
              title="Custom colour"
              style={{ width: 28, height: 28, borderRadius: '50%', cursor: 'pointer', border: 'none' }}
            />
          </div>
          <div className="space-y-1">
            <div className="flex justify-between theme-text-muted">
              <span>Opacity</span>
              <span>{Math.round(settings.overlayOpacity * 100)}%</span>
            </div>
            <input
              type="range" min={0} max={0.7} step={0.01}
              value={settings.overlayOpacity}
              onChange={(e) => setSettings({ overlayOpacity: parseFloat(e.target.value) })}
              className="w-full accent-cyan-400"
            />
          </div>
        </div>
      )}
    </>
  )
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}
