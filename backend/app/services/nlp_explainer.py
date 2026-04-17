"""
AI-powered NLP Explainer for DevEase.
Primary mode uses GroqCloud LLM API; fallback uses local rule-based generation.
"""

from datetime import datetime
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
import requests


# Load environment variables with explicit precedence:
# project root .env first, then backend/.env overrides it.
_ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT_DIR / ".env", override=False)
load_dotenv(_ROOT_DIR / "backend" / ".env", override=True)


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT_SECONDS", "25"))
GROQ_FALLBACK_MODELS = os.getenv(
    "GROQ_FALLBACK_MODELS",
    "llama-3.1-8b-instant,llama3-70b-8192",
)


def _plural(count: int, singular: str, plural: str = "") -> str:
    if not plural:
        plural = singular + "s"
    return singular if count == 1 else plural


def _score_label(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 55:
        return "fair"
    if score >= 40:
        return "poor"
    return "very poor"


def _smells_to_list(smells_data: Union[Dict[str, Any], List[Dict[str, Any]], None]) -> List[Dict[str, Any]]:
    if isinstance(smells_data, list):
        return smells_data
    return []


def _smells_summary(smells_data: Union[Dict[str, Any], List[Dict[str, Any]], None]) -> Dict[str, Any]:
    if isinstance(smells_data, dict):
        by_severity = smells_data.get("by_severity", {}) or {}
        total = smells_data.get("total_smells")
        if total is None:
            total = sum(v for v in by_severity.values() if isinstance(v, int))
        return {"total_smells": int(total or 0), "by_severity": by_severity}

    smells_list = _smells_to_list(smells_data)
    by_severity: Dict[str, int] = {}
    for item in smells_list:
        sev = str(item.get("severity", "low")).lower()
        by_severity[sev] = by_severity.get(sev, 0) + 1
    return {"total_smells": len(smells_list), "by_severity": by_severity}


def _build_summary(data: Dict[str, Any]) -> str:
    language = data.get("language", "Unknown")
    quality = data.get("quality_score", {}) or {}
    debt = data.get("technical_debt", {}) or {}
    ml = data.get("ml_complexity", {}) or {}

    overall = float(quality.get("overall_score", 0) or 0)
    debt_level = str(debt.get("debt_level", "unknown")).lower()
    predicted = str((ml.get("prediction", {}) or {}).get("predicted_class", "unknown")).lower()
    smells_summary = _smells_summary(data.get("code_smells"))
    smells_count = int(smells_summary.get("total_smells", 0))

    return (
        f"This **{language}** file has an overall quality score of **{overall:.0f}/100** "
        f"({_score_label(overall)}). The analysis detected **{smells_count} code "
        f"{_plural(smells_count, 'smell')}**, estimated technical debt is **{debt_level}**, "
        f"and predicted complexity is **{predicted}**."
    )


def _build_overview(data: Dict[str, Any]) -> str:
    classes = data.get("classes", []) or []
    functions = data.get("functions", []) or []
    imports = data.get("imports", []) or []
    total_nodes = int(data.get("total_nodes", 0) or 0)
    return (
        f"The code structure contains **{len(classes)} {_plural(len(classes), 'class', 'classes')}**, "
        f"**{len(functions)} {_plural(len(functions), 'function')}**, and "
        f"**{len(imports)} {_plural(len(imports), 'import')}**. "
        f"The parsed AST has **{total_nodes} nodes**."
    )


def _build_quality(data: Dict[str, Any]) -> str:
    quality = data.get("quality_score", {}) or {}
    overall = float(quality.get("overall_score", 0) or 0)
    maintainability = float(quality.get("maintainability", 0) or 0)
    readability = float(quality.get("readability", 0) or 0)
    complexity = float(quality.get("complexity", 0) or 0)
    documentation = float(quality.get("documentation", 0) or 0)

    parts = [
        f"Overall quality is **{overall:.0f}/100** ({_score_label(overall)}).",
        f"- Maintainability: **{maintainability:.0f}/100**",
        f"- Readability: **{readability:.0f}/100**",
        f"- Complexity: **{complexity:.0f}/100**",
        f"- Documentation: **{documentation:.0f}/100**",
    ]

    issues = quality.get("issues", []) or []
    if issues:
        parts.append("Main issues:")
        parts.extend([f"- {issue}" for issue in issues[:5]])
    return "\n".join(parts)


def _build_code_smells(data: Dict[str, Any]) -> str:
    smells_data = data.get("code_smells")
    summary = _smells_summary(smells_data)
    total = int(summary.get("total_smells", 0))
    by_severity = summary.get("by_severity", {}) or {}
    if total == 0:
        return "No code smells were detected."

    lines = [f"Detected **{total} code {_plural(total, 'smell')}**."]
    for sev in ("critical", "high", "medium", "low"):
        count = int(by_severity.get(sev, 0) or 0)
        if count > 0:
            lines.append(f"- {sev.capitalize()}: {count}")

    smells_list = _smells_to_list(smells_data)
    if smells_list:
        lines.append("Top examples:")
        for item in smells_list[:5]:
            smell_type = item.get("type", "Unknown")
            desc = item.get("description", "")
            line = item.get("line")
            line_part = f" (line {line})" if line else ""
            lines.append(f"- **{smell_type}**{line_part}: {desc}")
    return "\n".join(lines)


def _build_technical_debt(data: Dict[str, Any]) -> str:
    debt = data.get("technical_debt", {}) or {}
    score = float(debt.get("total_debt_score", 0) or 0)
    level = str(debt.get("debt_level", "unknown"))
    hours = float(debt.get("estimated_hours", 0) or 0)
    trend = str(debt.get("debt_trend", "stable"))
    text = (
        f"Technical debt score is **{score:.1f}** with **{level}** risk. "
        f"Estimated cleanup effort is **{hours:.1f} hours** and trend is **{trend}**."
    )

    recs = debt.get("recommendations", []) or []
    if recs:
        text += "\nRecommended actions:\n" + "\n".join([f"- {r}" for r in recs[:5]])
    return text


def _build_complexity(data: Dict[str, Any]) -> str:
    ml = data.get("ml_complexity", {}) or {}
    pred = (ml.get("prediction", {}) or {})
    predicted_class = pred.get("predicted_class", "unknown")
    confidence = pred.get("confidence")
    score = pred.get("complexity_score")
    parts = [f"Predicted complexity class is **{predicted_class}**."]
    if score is not None:
        parts.append(f"Complexity score: **{float(score):.0f}/100**.")
    if confidence is not None:
        conf_val = float(confidence)
        if conf_val <= 1:
            conf_val *= 100
        parts.append(f"Model confidence is **{conf_val:.0f}%**.")
    return " ".join(parts)


def _build_design_patterns(data: Dict[str, Any]) -> str:
    patterns = data.get("design_patterns", {}) or {}
    if not patterns:
        return "No design patterns were detected."

    lines = []
    for name, details in patterns.items():
        pattern_name = str(name).replace("_", " ").title()
        if isinstance(details, dict):
            confidence = details.get("confidence")
            if confidence is None:
                lines.append(f"- **{pattern_name}**")
            else:
                conf_val = float(confidence)
                if conf_val <= 1:
                    conf_val *= 100
                lines.append(f"- **{pattern_name}** ({conf_val:.0f}% confidence)")
        elif isinstance(details, bool) and details:
            lines.append(f"- **{pattern_name}**")
        elif isinstance(details, (int, float)) and details > 0:
            lines.append(f"- **{pattern_name}** ({float(details):.2f})")

    if not lines:
        return "No design patterns were confidently detected."
    return "Detected design patterns:\n" + "\n".join(lines)


def _build_full_report(sections: Dict[str, str]) -> str:
    return "\n\n---\n\n".join(
        [
            f"## Executive Summary\n\n{sections['summary']}",
            f"## Code Overview\n\n{sections['overview']}",
            f"## Quality Metrics\n\n{sections['quality']}",
            f"## Code Smells\n\n{sections['code_smells']}",
            f"## Technical Debt\n\n{sections['technical_debt']}",
            f"## Complexity Analysis\n\n{sections['complexity']}",
            f"## Design Patterns\n\n{sections['design_patterns']}",
        ]
    )


def _fallback_report(analysis_data: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
    sections = {
        "summary": _build_summary(analysis_data),
        "overview": _build_overview(analysis_data),
        "quality": _build_quality(analysis_data),
        "code_smells": _build_code_smells(analysis_data),
        "technical_debt": _build_technical_debt(analysis_data),
        "complexity": _build_complexity(analysis_data),
        "design_patterns": _build_design_patterns(analysis_data),
    }

    full_report = _build_full_report(sections)

    return {
        **sections,
        "full_report": full_report,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generation_source": "fallback",
        "fallback_reason": reason or "Groq API key not configured",
    }


def _compact_analysis_for_prompt(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    quality = analysis_data.get("quality_score", {}) or {}
    smells_data = analysis_data.get("code_smells")
    smells_summary = _smells_summary(smells_data)
    smells_list = _smells_to_list(smells_data)
    debt = analysis_data.get("technical_debt", {}) or {}
    ml = analysis_data.get("ml_complexity", {}) or {}
    patterns = analysis_data.get("design_patterns", {}) or {}

    return {
        "language": analysis_data.get("language"),
        "overview": {
            "classes_count": len(analysis_data.get("classes", []) or []),
            "functions_count": len(analysis_data.get("functions", []) or []),
            "imports_count": len(analysis_data.get("imports", []) or []),
            "total_nodes": analysis_data.get("total_nodes"),
        },
        "quality_score": {
            "overall_score": quality.get("overall_score"),
            "maintainability": quality.get("maintainability"),
            "readability": quality.get("readability"),
            "complexity": quality.get("complexity"),
            "documentation": quality.get("documentation"),
            "issues": (quality.get("issues") or [])[:8],
            "recommendations": (quality.get("recommendations") or [])[:8],
        },
        "code_smells": {
            "total_smells": smells_summary.get("total_smells", 0),
            "by_severity": smells_summary.get("by_severity", {}),
            "top_smells": smells_list[:8],
        },
        "technical_debt": {
            "total_debt_score": debt.get("total_debt_score"),
            "debt_level": debt.get("debt_level"),
            "debt_breakdown": debt.get("debt_breakdown", {}),
            "estimated_hours": debt.get("estimated_hours"),
            "debt_trend": debt.get("debt_trend"),
            "priority_issues": (debt.get("priority_issues") or [])[:8],
            "recommendations": (debt.get("recommendations") or [])[:8],
        },
        "ml_complexity": {
            "prediction": (ml.get("prediction") or {}),
        },
        "design_patterns": patterns,
    }


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _candidate_models() -> List[str]:
    models: List[str] = []
    for item in [GROQ_DEFAULT_MODEL, *GROQ_FALLBACK_MODELS.split(",")]:
        model = item.strip()
        if model and model not in models:
            models.append(model)
    return models


def _call_groq_generate_sections(analysis_data: Dict[str, Any], api_key: str, model: str) -> Dict[str, str]:
    compact = _compact_analysis_for_prompt(analysis_data)
    payload = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 1800,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert software code quality analyst. "
                    "Generate a professional, natural, human-readable report from structured static analysis metrics. "
                    "Return STRICT JSON only with keys: "
                    "summary, overview, quality, code_smells, technical_debt, complexity, design_patterns. "
                    "Each value must be Markdown-friendly text. Do not wrap JSON in code fences."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Create a dynamic NLP explanation report for this analysis data. "
                    "Explain what scores mean, severity of problems, and concrete improvements.\n\n"

                    "IMPORTANT:\n"
                    "For the design_patterns section ONLY, use this exact format:\n"
                    "The predicted design pattern category is <category>. "
                    "The suggested pattern is <pattern>, which <short explanation>. "
                    "The code can benefit from using design patterns to improve its structure and maintainability.\n\n"

                    "Keep all other sections unchanged and professional.\n\n"

                    + json.dumps(compact, ensure_ascii=True)
                )
            },
        ],
    }

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=GROQ_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    parsed = response.json()
    content = parsed["choices"][0]["message"]["content"]
    sections = _extract_json(content)

    required = ["summary", "overview", "quality", "code_smells", "technical_debt", "complexity", "design_patterns"]
    for key in required:
        if key not in sections:
            raise ValueError(f"Groq response missing key: {key}")
        if not isinstance(sections[key], str):
            sections[key] = str(sections[key])
    return {k: sections[k] for k in required}


def generate_nlp_report(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return _fallback_report(analysis_data, "GROQ_API_KEY is not set")

    errors: List[str] = []
    for model in _candidate_models():
        try:
            sections = _call_groq_generate_sections(analysis_data, api_key, model)
            full_report = _build_full_report(sections)
            return {
                **sections,
                "full_report": full_report,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "generation_source": "groq",
                "model": model,
            }
        except (requests.RequestException, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{model}: {str(exc)}")

    return _fallback_report(analysis_data, "Groq request failed for all models: " + " | ".join(errors))
