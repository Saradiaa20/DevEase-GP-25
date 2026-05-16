"""
Groq-powered full-file code fixer.

Takes the original source plus the static analysis result and asks the model to
return a complete corrected file.
"""

# import json
import os
# import re
from typing import Any, Dict, List, Optional
from groq import Groq

_SYSTEM = """
You are DevEase's Fixed Code generator, an expert Python and Java software engineer specializing in code repair, refactoring, maintainability, and safe optimization.

Your job:

1. Read the complete original source code.
2. Read the provided static analysis findings.
3. Generate a fully improved and corrected version of the same file.

MAIN GOAL:
Improve the code as much as reasonably possible while preserving the intended functionality and overall behavior.
Do not change the intended program behavior unless necessary to fix a clear bug or runtime error.
Preserve outputs, logic flow, and return values whenever possible.
Prefer minimal safe fixes over aggressive refactoring.

Prioritize fixing:
- runtime crashes
- unsafe mutations during iteration
- broad exception handling
- resource leaks
- invalid conditions
- dangerous random operations

IMPORTANT PRINCIPLES:

* Preserve intended behavior whenever reasonably possible.
* Prioritize correctness, readability, maintainability, safety, and clean code practices.
* Fix both explicitly detected issues and obvious problems visible directly in the source code.
* Apply safe refactoring where beneficial.
* Prefer production-ready, clean, professional code.
* Prefer maintainable, modular, and clean software structures inspired by good software engineering principles and suitable design patterns when safe and appropriate.

ALLOWED IMPROVEMENTS:

* Fix crashes and runtime errors.
* Fix unsafe patterns and obvious bugs.
* Improve exception handling.
* Improve naming, readability, and maintainability.
* Refactor repetitive or unnecessarily complex logic.
* Replace unsafe or outdated patterns with safer alternatives.
* Remove dead code and redundant conditions when safe.
* Improve file handling and resource management.
* Improve logging and error reporting.
* Improve loop structures and condition clarity when behavior is preserved.
* Replace dangerous anti-patterns with safer implementations.

BE CAREFUL WITH:

* Randomized behavior.
* Return values.
* External side effects.
* File operations.
* Timing-sensitive logic.
* Public APIs and function signatures.

DO NOT:

* Introduce unrelated new features.
* Rewrite the application architecture.
* Remove important existing functionality.
* Invent missing business logic.
* Change the programming language.
* Return partial snippets or patches.

WHEN UNSURE:

* Prefer the safest reasonable improvement.
* Avoid destructive assumptions.
* Preserve the original intent of the code.

OUTPUT REQUIREMENTS:

*Return only the complete fixed source code.
*Do not include explanations.
*Do not include markdown fences.

"""



def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _compact_analysis(analysis_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Keep the prompt focused and avoid sending duplicate heavy payloads."""
    if not analysis_data:
        return {}

    technical_debt = analysis_data.get("technical_debt") or {}
    quality_score = analysis_data.get("quality_score") or {}
    wrapper_generator = analysis_data.get("wrapper_generator") or {}

    return {
        "language": analysis_data.get("language"),
        "code_smells": _as_list(analysis_data.get("code_smells")),
        "quality_score": {
            "overall_score": quality_score.get("overall_score"),
            "maintainability": quality_score.get("maintainability"),
            "readability": quality_score.get("readability"),
            "complexity": quality_score.get("complexity"),
            "documentation": quality_score.get("documentation"),
            "issues": _as_list(quality_score.get("issues"))[:8],
            "recommendations": _as_list(quality_score.get("recommendations"))[:8],
        },
        "technical_debt": {
            "total_debt_score": technical_debt.get("total_debt_score"),
            "debt_level": technical_debt.get("debt_level"),
            "estimated_hours": technical_debt.get("estimated_hours"),
            "priority_issues": _as_list(technical_debt.get("priority_issues"))[:8],
            "recommendations": _as_list(technical_debt.get("recommendations"))[:8],
        },
        "wrapper_generator": {
            "patterns_found": wrapper_generator.get("patterns_found", 0),
            "patterns": _as_list(wrapper_generator.get("patterns"))[:10],
            "suggestions": _as_list(wrapper_generator.get("suggestions"))[:10],
            "message": wrapper_generator.get("message"),
        },
    }


def _build_user_prompt(
    code_content: str,
    language: str,
    analysis_data: Optional[Dict[str, Any]],
    file_name: Optional[str],
) -> str:
    display_name = file_name or "uploaded_source"
    analysis_summary = ""

    if analysis_data:
        code_smells = analysis_data.get("code_smells", [])

        priority_keywords = [
            "runtime",
            "exception",
            "division",
            "mutation",
            "resource",
            "unsafe",
        ]

        filtered_smells = [
            smell for smell in code_smells
            if any(k in str(smell).lower() for k in priority_keywords)
        ]

        top_smells = filtered_smells[:5] or code_smells[:5]
        if top_smells:
            analysis_summary = "\nSTATIC ANALYSIS FINDINGS:\n"

            for issue in top_smells:
                analysis_summary += f"- {issue}\n"
    return f"""\
File name: {display_name}
Language: {language}

ORIGINAL SOURCE CODE:
```{language.lower()}
{code_content}
```
{analysis_summary}

Generate a fully improved and corrected version of this source code.
Fix bugs, unsafe patterns, crashes, bad practices, and maintainability issues while preserving intended functionality.

Return only the complete fixed source code.
Do not include explanations.
Do not include markdown fences.
"""


# def _parse_json_object(raw: str) -> Dict[str, Any]:
#     try:
#         return json.loads(raw)
#     except json.JSONDecodeError:
#         match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
#         if match:
#             return json.loads(match.group(0))
#         raise


class FixedCodeGenerator:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GROQ_API_KEY_FIXER") or os.getenv("GROQ_API_KEY")
        if not key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. Add it to backend/.env or your environment."
            )
        self._client = Groq(api_key=key)
        self._model = "llama-3.1-8b-instant"

    def generate_fixed_code(
        self,
        code_content: str,
        language: str,
        analysis_data: Optional[Dict[str, Any]] = None,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        chat = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": _build_user_prompt(
                        code_content=code_content,
                        language=language,
                        analysis_data=analysis_data,
                        file_name=file_name,
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=3000,
            # response_format={"type": "json_object"},
        )

        # raw = chat.choices[0].message.content or "{}"
        # result = _parse_json_object(raw)

        # fixed_code = result.get("fixed_code")

        # if not isinstance(fixed_code, str) or not fixed_code.strip():
        #     raise ValueError("Groq response did not include fixed_code.")
        fixed_code = (chat.choices[0].message.content or "").strip()

        if not fixed_code:
            raise ValueError("Groq response was empty.")
        return {
          "fixed_code": fixed_code + "\n",
            "summary": "Generated fixed source code.",
            "confidence": "medium",
            "model": self._model,

        }