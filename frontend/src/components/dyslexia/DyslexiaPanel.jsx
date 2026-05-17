import { useState } from 'react'
import { useDyslexia } from './DyslexiaContext'

const FONTS = [
  { id: 'lexend',       label: 'Lexend',               desc: 'Optimised for reading proficiency' },
  { id: 'atkinson',     label: 'Atkinson Hyperlegible', desc: 'Maximum letter distinctiveness' },
  { id: 'opendyslexic', label: 'OpenDyslexic',          desc: 'Bottom-weighted glyphs' },
]

function Slider({ label, value, min, max, step, unit, onChange }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="theme-text-muted">{label}</span>
        <span className="theme-text-primary font-mono">{value}{unit}</span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full accent-cyan-400"
      />
    </div>
  )
}

export default function DyslexiaPanel() {
  const { settings, setSettings } = useDyslexia()
  const [open, setOpen] = useState(false)

  return (
    <div className="cyber-card-panel space-y-4">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="theme-text-primary font-semibold text-lg">Dyslexia Friendly Mode</h3>
          <p className="theme-text-muted text-sm">Font, spacing, and reading aids</p>
        </div>
        <button
          onClick={() => setSettings({ enabled: !settings.enabled })}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            settings.enabled ? 'bg-cyan-500' : 'bg-gray-600'
          }`}
        >
          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            settings.enabled ? 'translate-x-6' : 'translate-x-1'
          }`} />
        </button>
      </div>

      {settings.enabled && (
        <>
          {/* Font picker */}
          <div className="space-y-2">
            <p className="text-sm theme-text-muted font-medium">Font</p>
            <div className="grid grid-cols-1 gap-2">
              {FONTS.map((f) => (
                <button
                  key={f.id}
                  onClick={() => setSettings({ font: f.id })}
                  className={`text-left px-3 py-2 rounded-lg border text-sm transition-all ${
                    settings.font === f.id
                      ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                      : 'theme-bg-card theme-border theme-text-muted hover:border-cyan-500/50'
                  }`}
                >
                  <span className="font-medium">{f.label}</span>
                  <span className="ml-2 opacity-60 text-xs">{f.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Spacing sliders — collapsible */}
          <button
            onClick={() => setOpen(!open)}
            className="w-full text-left text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>{open ? '▾' : '▸'}</span> Spacing &amp; line height
          </button>

          {open && (
            <div className="space-y-4 pl-2">
              <Slider
                label="Letter spacing" value={settings.letterSpacing}
                min={0} max={0.25} step={0.01} unit="em"
                onChange={(v) => setSettings({ letterSpacing: v })}
              />
              <Slider
                label="Word spacing" value={settings.wordSpacing}
                min={0} max={0.5} step={0.01} unit="em"
                onChange={(v) => setSettings({ wordSpacing: v })}
              />
              <Slider
                label="Line height" value={settings.lineHeight}
                min={1.2} max={3} step={0.1} unit=""
                onChange={(v) => setSettings({ lineHeight: v })}
              />
            </div>
          )}

          {/* Quick toggles for other features */}
          <div className="grid grid-cols-2 gap-2 pt-1">
            {[
              { key: 'overlay',           label: 'Colour overlay' },
              { key: 'tts',               label: 'Text-to-speech' },
              { key: 'ruler',             label: 'Reading ruler' },
              { key: 'sentenceHighlight', label: 'Sentence focus' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setSettings({ [key]: !settings[key] })}
                className={`px-3 py-2 rounded-lg border text-sm transition-all ${
                  settings[key]
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                    : 'theme-bg-card theme-border theme-text-muted hover:border-cyan-500/50'
                }`}
              >
                {settings[key] ? '✓ ' : ''}{label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
