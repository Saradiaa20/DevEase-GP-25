import React from 'react'
import Layout from '../components/Layout'
import { useSettings } from '../contexts/SettingsContext'
import DyslexiaPanel from '../components/dyslexia/DyslexiaPanel'

function Settings() {
  const { settings, setTheme, setToggle } = useSettings()

  const handleToggle = (key) => setToggle(key, !settings[key])
  const handleThemeChange = (theme) => setTheme(theme)

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold theme-text-primary mb-2">Settings</h1>
          <p className="theme-text-muted">Customize your accessibility preferences</p>
        </div>

        {/* Dyslexia Friendly Mode */}
        <DyslexiaPanel />

        {/* Accessibility Options */}
        <div className="cyber-card-panel">
          <h2 className="text-xl font-semibold theme-text-primary mb-4">Accessibility Options</h2>
          <div className="space-y-4">
            <ToggleOption
              label="Low Vision"
              description="Increase contrast for better visibility"
              checked={settings.highContrast}
              onChange={() => handleToggle('highContrast')}
            />
            <ToggleOption
              label="ADHD Focus"
              description="Reduce distractions for better focus"
              checked={settings.focusMode}
              onChange={() => handleToggle('focusMode')}
            />
          </div>
        </div>

        {/* Theme Settings */}
        <div className="cyber-card-panel">
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
              Dark Mode
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

