import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'devease-settings'

const defaults = {
  theme: 'dark',
  disabilityPreset: 'default',
  dyslexicFont: false,
  highContrast: false,
  focusMode: false,
}

function load() {
  try {
    const s = localStorage.getItem(STORAGE_KEY)
    if (!s) return defaults
    const parsed = JSON.parse(s)
    return { ...defaults, ...parsed }
  } catch {
    return defaults
  }
}

function save(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch (_) {}
}

const SettingsContext = createContext(null)

export function SettingsProvider({ children }) {
  const [settings, setSettingsState] = useState(load)

  const setSettings = useCallback((update) => {
    setSettingsState((prev) => {
      const next = typeof update === 'function' ? update(prev) : { ...prev, ...update }
      save(next)
      return next
    })
  }, [])

  const setTheme = useCallback((theme) => setSettings({ theme }), [setSettings])
  const setDisabilityPreset = useCallback((preset) => {
    setSettings((prev) => ({
      ...prev,
      disabilityPreset: preset,
      dyslexicFont: preset === 'dyslexia' || preset === 'adhdFocus',
      highContrast: preset === 'lowVision',
      focusMode: preset === 'adhdFocus',
    }))
  }, [setSettings])
  const setDyslexicFont = useCallback((v) => setSettings({ dyslexicFont: v }), [setSettings])
  const setHighContrast = useCallback((v) => setSettings({ highContrast: v }), [setSettings])
  const setFocusMode = useCallback((v) => setSettings({ focusMode: v }), [setSettings])
  const setToggle = useCallback((key, value) => setSettings({ [key]: value }), [setSettings])

  // Apply to document so CSS and layout react
  useEffect(() => {
    const root = document.documentElement
    root.setAttribute('data-theme', settings.theme)

    root.classList.toggle('dyslexia-font', settings.dyslexicFont)
    root.classList.toggle('high-contrast', settings.highContrast)
    root.classList.toggle('focus-mode', settings.focusMode)
  }, [settings.theme, settings.dyslexicFont, settings.highContrast, settings.focusMode])

  const value = {
    settings,
    setSettings,
    setTheme,
    setDisabilityPreset,
    setDyslexicFont,
    setHighContrast,
    setFocusMode,
    setToggle,
  }

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const ctx = useContext(SettingsContext)
  if (!ctx) throw new Error('useSettings must be used within SettingsProvider')
  return ctx
}
