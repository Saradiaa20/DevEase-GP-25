import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'devease-dyslexia-v2'

const defaults = {
  enabled: false,
  font: 'lexend',           // 'lexend' | 'atkinson' | 'opendyslexic'
  letterSpacing: 0.05,      // em
  wordSpacing: 0.1,         // em
  lineHeight: 1.6,
  overlay: false,
  overlayColor: '#fef9c3',  // cream
  overlayOpacity: 0.35,
  tts: false,
  ttsRate: 1,
  ttsPitch: 1,
  ttsVoice: '',
  ruler: false,
  rulerHeight: 32,
  rulerOpacity: 0.15,
  sentenceHighlight: false,
}

const DyslexiaContext = createContext(null)

export function DyslexiaProvider({ children }) {
  const [settings, setSettingsRaw] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY))
      return saved ? { ...defaults, ...saved } : defaults
    } catch {
      return defaults
    }
  })

  const setSettings = useCallback((patch) => {
    setSettingsRaw((prev) => ({ ...prev, ...patch }))
  }, [])

  // Write CSS custom properties to <html> on every change
  useEffect(() => {
    const root = document.documentElement
    if (settings.enabled) {
      const fontMap = {
        lexend: "'Lexend', sans-serif",
        atkinson: "'Atkinson Hyperlegible', sans-serif",
        opendyslexic: "'OpenDyslexic', sans-serif",
      }
      root.style.setProperty('--dx-font-family', fontMap[settings.font] ?? fontMap.lexend)
      root.style.setProperty('--dx-letter-spacing', `${settings.letterSpacing}em`)
      root.style.setProperty('--dx-word-spacing', `${settings.wordSpacing}em`)
      root.style.setProperty('--dx-line-height', settings.lineHeight)
      root.classList.add('dx-active')
    } else {
      root.style.removeProperty('--dx-font-family')
      root.style.removeProperty('--dx-letter-spacing')
      root.style.removeProperty('--dx-word-spacing')
      root.style.removeProperty('--dx-line-height')
      root.classList.remove('dx-active')
    }
  }, [settings.enabled, settings.font, settings.letterSpacing, settings.wordSpacing, settings.lineHeight])

  // Persist
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  }, [settings])

  return (
    <DyslexiaContext.Provider value={{ settings, setSettings }}>
      {children}
    </DyslexiaContext.Provider>
  )
}

export function useDyslexia() {
  const ctx = useContext(DyslexiaContext)
  if (!ctx) throw new Error('useDyslexia must be used inside DyslexiaProvider')
  return ctx
}
