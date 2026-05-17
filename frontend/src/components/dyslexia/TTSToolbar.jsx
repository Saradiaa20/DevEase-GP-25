import { useState, useEffect, useRef } from 'react'
import { useDyslexia } from './DyslexiaContext'

export default function TTSToolbar() {
  const { settings, setSettings } = useDyslexia()
  const [voices, setVoices] = useState([])
  const [speaking, setSpeaking] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const uttRef = useRef(null)

  useEffect(() => {
    const load = () => setVoices(window.speechSynthesis.getVoices())
    load()
    window.speechSynthesis.addEventListener('voiceschanged', load)
    return () => window.speechSynthesis.removeEventListener('voiceschanged', load)
  }, [])

  if (!settings.enabled || !settings.tts) return null

  const speak = () => {
    const text = window.getSelection()?.toString()
    if (!text) return
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    utt.rate = settings.ttsRate
    utt.pitch = settings.ttsPitch
    if (settings.ttsVoice) {
      utt.voice = voices.find((v) => v.name === settings.ttsVoice) ?? null
    }
    utt.onstart = () => setSpeaking(true)
    utt.onend = () => setSpeaking(false)
    utt.onerror = () => setSpeaking(false)
    uttRef.current = utt
    window.speechSynthesis.speak(utt)
  }

  const stop = () => {
    window.speechSynthesis.cancel()
    setSpeaking(false)
  }

  return (
    <div style={{ position: 'fixed', bottom: 16, right: 16, zIndex: 9300 }} className="flex items-center gap-2">
      {showConfig && (
        <div className="cyber-card-panel p-3 space-y-3 text-sm" style={{ width: 220 }}>
          <p className="theme-text-primary font-semibold">Text-to-speech</p>
          <label className="block space-y-1">
            <span className="theme-text-muted">Voice</span>
            <select
              value={settings.ttsVoice}
              onChange={(e) => setSettings({ ttsVoice: e.target.value })}
              className="w-full bg-gray-800 text-white rounded px-2 py-1 text-xs border border-gray-600"
            >
              <option value="">System default</option>
              {voices.map((v) => (
                <option key={v.name} value={v.name}>{v.name} ({v.lang})</option>
              ))}
            </select>
          </label>
          <div className="space-y-1">
            <div className="flex justify-between theme-text-muted"><span>Speed</span><span>{settings.ttsRate}x</span></div>
            <input type="range" min={0.5} max={2} step={0.1} value={settings.ttsRate}
              onChange={(e) => setSettings({ ttsRate: parseFloat(e.target.value) })}
              className="w-full accent-cyan-400" />
          </div>
          <div className="space-y-1">
            <div className="flex justify-between theme-text-muted"><span>Pitch</span><span>{settings.ttsPitch}</span></div>
            <input type="range" min={0.5} max={2} step={0.1} value={settings.ttsPitch}
              onChange={(e) => setSettings({ ttsPitch: parseFloat(e.target.value) })}
              className="w-full accent-cyan-400" />
          </div>
        </div>
      )}

      <div className="flex items-center gap-1 bg-gray-900 border border-gray-700 rounded-full px-3 py-1 shadow-lg">
        <button
          onClick={speaking ? stop : speak}
          title={speaking ? 'Stop' : 'Read selected text'}
          className="text-cyan-400 hover:text-cyan-300 font-bold text-lg w-7 h-7 flex items-center justify-center"
        >
          {speaking ? '■' : '▶'}
        </button>
        <button
          onClick={() => setShowConfig(!showConfig)}
          title="TTS settings"
          className="text-gray-400 hover:text-gray-200 text-sm w-6 h-6 flex items-center justify-center"
        >
          ⚙
        </button>
      </div>
    </div>
  )
}
