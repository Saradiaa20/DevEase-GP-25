"""
wrapper_groq.py
Wrapper Generator — Step 2: Groq-powered, code-specific suggestions.
Receives an UnsafePattern (with the exact snippet + context) and asks
llama-3 to suggest a safer, wrapped version of THAT exact code.
"""

import os
import json
from typing import List, Dict, Any, Optional

from groq import Groq
from app.ml.wrapper_detector import UnsafePattern


# ─── Prompts ─────────────────────────────────────────────────────────────────

_SYSTEM = """\
You are DevEase's Wrapper Generator — an expert code safety advisor embedded in a developer tool.

Your task:
1. Receive a specific unsafe code snippet (a bare API call, missing try-catch, unclosed resource, etc.).
2. Analyse EXACTLY what that snippet is doing.
3. Suggest a safer "wrapped" version of that EXACT snippet — not a generic template.
4. Explain why the original is unsafe and what your suggestion fixes.

Rules:
- Preserve the original logic 100%; only add safety wrappers.
- Use the same language (Python or Java) as the input.
- Be specific: name the exception types, the variables, the function names from the real code.
- Do NOT force the fix — phrase everything as a suggestion the developer can accept or dismiss.
- Return ONLY valid JSON matching the schema below. No markdown, no prose outside the JSON.

JSON schema:
{
  "suggestion_title": "<short title, e.g. 'Wrap requests.get in try/except'>",
  "explanation": "<2-4 sentences: why the code is unsafe and what the fix addresses>",
  "wrapped_code": "<the complete safer version of the snippet — exact, runnable code>",
  "changes_made": ["<specific change 1>", "<specific change 2>"],
  "severity": "high|medium|low",
  "accept_label": "Apply Suggestion",
  "dismiss_label": "Keep Original"
}"""


def _build_user_prompt(pattern: UnsafePattern, full_code: str) -> str:
    lines = full_code.splitlines()
    ctx_start = max(0, pattern.line_number - 6)
    ctx_end   = min(len(lines), pattern.end_line + 6)
    ctx_window = "\n".join(lines[ctx_start:ctx_end])

    return f"""\
Language : {pattern.language}

UNSAFE PATTERN DETECTED
  Type     : {pattern.pattern_type}
  Severity : {pattern.severity}
  Lines    : {pattern.line_number}–{pattern.end_line}
  Issue    : {pattern.description}

EXACT UNSAFE SNIPPET (lines {pattern.line_number}–{pattern.end_line}):
```
{pattern.code_snippet}
```

SURROUNDING CONTEXT (lines {ctx_start + 1}–{ctx_end}):
```
{ctx_window}
```

Suggest a safer version of the EXACT snippet above.
Return only the JSON object — no markdown fences, no extra text."""


# ─── Generator ───────────────────────────────────────────────────────────────

class WrapperSuggestionGenerator:

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. Add it to backend/.env or your environment."
            )
        self._client = Groq(api_key=key)
        self._model  = "llama-3.3-70b-versatile"

    # ── single pattern ────────────────────────────────────────────────────────

    def generate_suggestion(
        self, pattern: UnsafePattern, full_code: str
    ) -> Dict[str, Any]:
        chat = self._client.chat.completions.create(
            model    = self._model,
            messages = [
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": _build_user_prompt(pattern, full_code)},
            ],
            temperature     = 0.15,
            max_tokens      = 1200,
            response_format = {"type": "json_object"},
        )

        raw = chat.choices[0].message.content
        try:
            suggestion = json.loads(raw)
        except json.JSONDecodeError:
            suggestion = {
                "suggestion_title": "Safety Wrapper Suggested",
                "explanation": "The detected pattern may cause unhandled errors.",
                "wrapped_code": pattern.code_snippet,
                "changes_made": ["Manual review recommended"],
                "severity": pattern.severity,
                "accept_label": "Apply Suggestion",
                "dismiss_label": "Keep Original",
            }

        # Enrich with pattern metadata for the frontend
        suggestion.update({
            "pattern_id":    pattern.pattern_id,
            "pattern_type":  pattern.pattern_type,
            "line_number":   pattern.line_number,
            "end_line":      pattern.end_line,
            "original_code": pattern.code_snippet,
            "language":      pattern.language,
        })
        return suggestion

    # ── all patterns (sorted high → low, capped) ─────────────────────────────

    def generate_all_suggestions(
        self,
        patterns: List[UnsafePattern],
        full_code: str,
        max_patterns: int = 10,
    ) -> List[Dict[str, Any]]:
        results = []
        for pattern in patterns[:max_patterns]:
            try:
                results.append(self.generate_suggestion(pattern, full_code))
            except Exception as exc:
                results.append({
                    "pattern_id":      pattern.pattern_id,
                    "pattern_type":    pattern.pattern_type,
                    "line_number":     pattern.line_number,
                    "end_line":        pattern.end_line,
                    "original_code":   pattern.code_snippet,
                    "language":        pattern.language,
                    "severity":        pattern.severity,
                    "suggestion_title": "Analysis unavailable",
                    "explanation":     f"Could not generate suggestion: {exc}",
                    "wrapped_code":    pattern.code_snippet,
                    "changes_made":    [],
                    "accept_label":    "Apply Suggestion",
                    "dismiss_label":   "Keep Original",
                    "error":           str(exc),
                })
        return results
