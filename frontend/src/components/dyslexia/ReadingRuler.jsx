import { useEffect, useRef } from 'react'
import { useDyslexia } from './DyslexiaContext'

export default function ReadingRuler() {
  const { settings } = useDyslexia()
  const rulerRef = useRef(null)
  const rafRef = useRef(null)

  useEffect(() => {
    if (!settings.enabled || !settings.ruler) return

    const ruler = rulerRef.current
    if (!ruler) return

    const onMove = (e) => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = requestAnimationFrame(() => {
        ruler.style.top = `${e.clientY - settings.rulerHeight / 2}px`
        ruler.style.display = 'block'
      })
    }

    window.addEventListener('mousemove', onMove)
    return () => {
      window.removeEventListener('mousemove', onMove)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [settings.enabled, settings.ruler, settings.rulerHeight])

  if (!settings.enabled || !settings.ruler) return null

  const shadowColor = `rgba(0,0,0,${settings.rulerOpacity})`

  return (
    <div
      ref={rulerRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        left: 0,
        right: 0,
        height: settings.rulerHeight,
        pointerEvents: 'none',
        zIndex: 8900,
        display: 'none',
        boxShadow: `0 -2000px 0 2000px ${shadowColor}, 0 2000px 0 2000px ${shadowColor}`,
        borderTop: '1px solid rgba(34,211,238,0.3)',
        borderBottom: '1px solid rgba(34,211,238,0.3)',
      }}
    />
  )
}
