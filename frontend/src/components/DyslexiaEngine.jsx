/**
 * DyslexiaEngine
 *
 * Uses a TreeWalker to find every text node in the live DOM, transforms its
 * content, and stores the original so it can be perfectly restored.
 *
 * A MutationObserver watches for new nodes inserted after the initial pass
 * so dynamically-rendered content (route changes, lazy panels, tooltips,
 * error messages, dropdowns) is also transformed automatically.
 *
 * Mount once at app root via <DyslexiaEngine /> — the component is invisible
 * and manages its own lifecycle through useEffect.
 */

import { useEffect, useRef } from 'react'
import { transformText, isCodeContext } from '../utils/dyslexiaTransformer'
import { useSettings } from '../contexts/SettingsContext'

// Attribute we stamp on transformed text nodes' parents to track originals
const DATA_ATTR = 'data-dyslexia-original'
const DATA_PH_ATTR = 'data-dyslexia-ph-original'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Walk all text nodes under root, call cb for each */
function walkTextNodes(root, cb) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      // Skip empty / whitespace-only nodes
      if (!node.nodeValue?.trim()) return NodeFilter.FILTER_SKIP
      // Skip script / style content
      const tag = node.parentElement?.tagName?.toLowerCase()
      if (tag === 'script' || tag === 'style' || tag === 'noscript') return NodeFilter.FILTER_SKIP
      return NodeFilter.FILTER_ACCEPT
    },
  })
  let node
  while ((node = walker.nextNode())) cb(node)
}

/** Transform a single text node, saving original */
function transformNode(node) {
  if (isCodeContext(node)) return
  const original = node.nodeValue
  const transformed = transformText(original)
  if (transformed === original) return // nothing changed — skip storing

  // Store original on the parent element (survives React re-renders that
  // replace text content but keep the same parent element)
  const parent = node.parentElement
  if (parent && !parent.hasAttribute(DATA_ATTR)) {
    parent.setAttribute(DATA_ATTR, original)
  }
  node.nodeValue = transformed
}

/** Restore a single text node from saved original */
function restoreNode(node) {
  const parent = node.parentElement
  if (!parent) return
  const original = parent.getAttribute(DATA_ATTR)
  if (original !== null) {
    node.nodeValue = original
    parent.removeAttribute(DATA_ATTR)
  }
}

/** Transform placeholder text on inputs/textareas */
function transformPlaceholders(root) {
  const inputs = root.querySelectorAll
    ? root.querySelectorAll('input[placeholder], textarea[placeholder]')
    : []
  inputs.forEach((el) => {
    if (!el.hasAttribute(DATA_PH_ATTR)) {
      el.setAttribute(DATA_PH_ATTR, el.placeholder)
    }
    el.placeholder = transformText(el.placeholder)
  })
}

/** Restore placeholder text */
function restorePlaceholders(root) {
  const inputs = root.querySelectorAll
    ? root.querySelectorAll(`[${DATA_PH_ATTR}]`)
    : []
  inputs.forEach((el) => {
    el.placeholder = el.getAttribute(DATA_PH_ATTR)
    el.removeAttribute(DATA_PH_ATTR)
  })
}

// ---------------------------------------------------------------------------
// Transform / restore whole document
// ---------------------------------------------------------------------------

function transformAll() {
  walkTextNodes(document.body, transformNode)
  transformPlaceholders(document.body)
}

function restoreAll() {
  walkTextNodes(document.body, restoreNode)
  restorePlaceholders(document.body)
}

// ---------------------------------------------------------------------------
// React component — renders nothing, manages the observer lifecycle
// ---------------------------------------------------------------------------

export default function DyslexiaEngine() {
  const { settings } = useSettings()
  const active = settings.dyslexia
  const observerRef = useRef(null)

  useEffect(() => {
    if (!active) {
      // Tear down observer and restore text
      if (observerRef.current) {
        observerRef.current.disconnect()
        observerRef.current = null
      }
      restoreAll()
      return
    }

    // Initial full-document pass
    transformAll()

    // Watch for DOM changes (route changes, async renders, modals, tooltips…)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        // New nodes added to the DOM
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            transformNode(node)
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            walkTextNodes(node, transformNode)
            transformPlaceholders(node)
          }
        })

        // Character data changed on an existing text node (React updates)
        if (
          mutation.type === 'characterData' &&
          mutation.target.nodeType === Node.TEXT_NODE
        ) {
          // Only transform if not already in a transformed state
          const parent = mutation.target.parentElement
          if (parent && !parent.hasAttribute(DATA_ATTR)) {
            transformNode(mutation.target)
          }
        }
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    })

    observerRef.current = observer

    return () => {
      observer.disconnect()
      observerRef.current = null
    }
  }, [active])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
      restoreAll()
    }
  }, [])

  return null
}
