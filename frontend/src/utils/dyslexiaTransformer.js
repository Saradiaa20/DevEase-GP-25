/**
 * Dyslexia Mode Text Transformer
 *
 * Simulates the visual perception experience of dyslexia by shuffling the
 * middle letters of words while keeping first and last letters intact.
 *
 * Rules:
 *  - Words ≤ 3 chars are left unchanged
 *  - Numbers, URLs, emails, and code tokens are left unchanged
 *  - Capitalization of the first letter is preserved
 *  - Punctuation attached to words is preserved
 *  - The shuffle is deterministic per word (seeded by char codes) so the
 *    same word always transforms the same way within a session
 */

// ---------------------------------------------------------------------------
// Seeded pseudo-random (mulberry32) — deterministic per word so re-renders
// don't re-shuffle causing flicker
// ---------------------------------------------------------------------------
function mulberry32(seed) {
  return function () {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function wordSeed(word) {
  let h = 0
  for (let i = 0; i < word.length; i++) {
    h = (Math.imul(31, h) + word.charCodeAt(i)) | 0
  }
  return h
}

// ---------------------------------------------------------------------------
// Patterns that should never be transformed
// ---------------------------------------------------------------------------
const SKIP_PATTERNS = [
  /^https?:\/\//i,           // URLs
  /^www\./i,                  // www. links
  /^[\w.+-]+@[\w-]+\.\w+$/i, // emails
  /^\d[\d.,_]*$/,             // pure numbers / numeric literals
  /^0x[0-9a-f]+$/i,           // hex literals
  /^[#$%&*@!^~`|\\/<>{}[\]()=+\-:;,."']+$/, // pure punctuation / operators
]

function shouldSkip(word) {
  if (word.length <= 3) return true
  for (const pat of SKIP_PATTERNS) {
    if (pat.test(word)) return true
  }
  return false
}

// ---------------------------------------------------------------------------
// Shuffle the middle letters of a single word token
// ---------------------------------------------------------------------------
function shuffleMiddle(word) {
  if (shouldSkip(word)) return word

  // Strip leading/trailing punctuation so we only touch the alpha core
  const leadMatch = word.match(/^([^a-zA-Z0-9]*)/)
  const trailMatch = word.match(/([^a-zA-Z0-9]*)$/)
  const lead = leadMatch ? leadMatch[1] : ''
  const trail = trailMatch ? trailMatch[1] : ''
  const core = word.slice(lead.length, word.length - trail.length || undefined)

  if (core.length <= 3) return word

  const first = core[0]
  const last = core[core.length - 1]
  const middle = core.slice(1, -1).split('')

  // Shuffle using seeded RNG so the same word always produces the same result
  const rng = mulberry32(wordSeed(core.toLowerCase()))
  for (let i = middle.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1))
    ;[middle[i], middle[j]] = [middle[j], middle[i]]
  }

  return lead + first + middle.join('') + last + trail
}

// ---------------------------------------------------------------------------
// Transform a full string (may contain multiple words / whitespace)
// ---------------------------------------------------------------------------
export function transformText(text) {
  if (!text || typeof text !== 'string') return text

  // Split on whitespace boundaries, preserving the whitespace tokens
  const tokens = text.split(/(\s+)/)
  return tokens
    .map((token) => {
      // Whitespace — pass through
      if (/^\s+$/.test(token)) return token
      return shuffleMiddle(token)
    })
    .join('')
}

// ---------------------------------------------------------------------------
// Check if a text node is inside a code/pre block or an input element
// ---------------------------------------------------------------------------
export function isCodeContext(node) {
  let el = node.parentElement
  while (el) {
    const tag = el.tagName?.toLowerCase()
    if (tag === 'code' || tag === 'pre' || tag === 'kbd' || tag === 'samp') return true
    // Monaco editor lines
    if (el.classList?.contains('view-line')) return true
    if (el.classList?.contains('mtk1')) return true
    el = el.parentElement
  }
  return false
}
