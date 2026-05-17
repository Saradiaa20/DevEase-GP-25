import { useEffect, useRef } from 'react'
import { useDyslexia } from './DyslexiaContext'

const CLS = 'dx-sentence-active'

export default function SentenceHighlighter() {
  const { settings } = useDyslexia()
  const prevRef = useRef(null)
  const rafRef = useRef(null)

  useEffect(() => {
    if (!settings.enabled || !settings.sentenceHighlight) {
      if (prevRef.current) {
        prevRef.current.classList.remove(CLS)
        prevRef.current = null
      }
      return
    }

    const onMove = (e) => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = requestAnimationFrame(() => {
        const el = document.elementFromPoint(e.clientX, e.clientY)
        const block = el?.closest('p, li, h1, h2, h3, h4, h5, h6, td, th, label, span')
        if (block === prevRef.current) return
        if (prevRef.current) prevRef.current.classList.remove(CLS)
        if (block) block.classList.add(CLS)
        prevRef.current = block ?? null
      })
    }

    window.addEventListener('mousemove', onMove)
    return () => {
      window.removeEventListener('mousemove', onMove)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      if (prevRef.current) prevRef.current.classList.remove(CLS)
    }
  }, [settings.enabled, settings.sentenceHighlight])

  return null
}
