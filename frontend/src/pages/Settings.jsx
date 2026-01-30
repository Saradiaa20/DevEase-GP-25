import React from 'react'
import Layout from '../components/Layout'
import { useSettings } from '../contexts/SettingsContext'

function Settings() {
  const { settings, setDisabilityPreset, setTheme, setToggle } = useSettings()

  const presets = [
    { id: 'default', name: 'Default' },
    { id: 'dyslexia', name: 'Dyslexia' },
    { id: 'lowVision', name: 'Low Vision' },
    { id: 'adhdFocus', name: 'ADHD Focus' },
  ]

  const handlePresetChange = (preset) => setDisabilityPreset(preset)
  const handleToggle = (key) => setToggle(key, !settings[key])
  const handleThemeChange = (theme) => setTheme(theme)

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold theme-text-primary mb-2">Settings</h1>
          <p className="theme-text-muted">Customize your accessibility preferences</p>
        </div>

        {/* Disability Presets */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold theme-text-primary mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Disability Presets
          </h2>
          <div className="space-y-2">
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handlePresetChange(preset.id)}
                className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                  settings.disabilityPreset === preset.id
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                    : 'theme-bg-card theme-border theme-text-muted hover:border-cyan-500/50'
                }`}
              >
                {preset.name}
                {settings.disabilityPreset === preset.id && (
                  <span className="ml-2 text-xs">✓ Selected</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Granular Controls */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold theme-text-primary mb-4">Accessibility Options</h2>
          <div className="space-y-4">
            <ToggleOption
              label="Dyslexic-Friendly Font"
              description="Use fonts optimized for dyslexia"
              checked={settings.dyslexicFont}
              onChange={() => handleToggle('dyslexicFont')}
            />
            <ToggleOption
              label="High Contrast Mode"
              description="Increase contrast for better visibility"
              checked={settings.highContrast}
              onChange={() => handleToggle('highContrast')}
            />
            <ToggleOption
              label="Focus Mode"
              description="Reduce distractions for better focus"
              checked={settings.focusMode}
              onChange={() => handleToggle('focusMode')}
            />
          </div>
        </div>

        {/* Theme Settings */}
        <div className="cyber-card">
          <h2 className="text-xl font-semibold theme-text-primary mb-4">Theme</h2>
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => handleThemeChange('dark')}
              className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                settings.theme === 'dark'
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                  : 'theme-bg-card theme-border theme-text-muted hover:border-cyan-500/50'
              }`}
            >
              Dark Mode (Cyber Vibes)
              {settings.theme === 'dark' && <span className="ml-2 text-xs">✓ Selected</span>}
            </button>
            <button
              type="button"
              onClick={() => handleThemeChange('light')}
              className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                settings.theme === 'light'
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                  : 'theme-bg-card theme-border theme-text-muted hover:border-cyan-500/50'
              }`}
            >
              Light Mode
              {settings.theme === 'light' && <span className="ml-2 text-xs">✓ Selected</span>}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}

function ToggleOption({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between p-4 theme-bg-card rounded-lg theme-border border">
      <div>
        <div className="theme-text-primary font-medium">{label}</div>
        <div className="theme-text-muted text-sm">{description}</div>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? 'bg-cyan-500' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}

export default Settings
