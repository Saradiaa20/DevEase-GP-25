"""
FastAPI router for full-file fixed code generation.
"""

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.fixed_code_groq import FixedCodeGenerator


router = APIRouter(prefix="/api/fixed-code", tags=["Fixed Code"])


class FixedCodeRequest(BaseModel):
    code_content: Optional[str] = None
    language: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    file_name: Optional[str] = None


class FixedCodeResponse(BaseModel):
    success: bool
    language: str
    fixed_code: str
    summary: str
    # changes: list
    # warnings: list
    confidence: str
    model: str
    message: str


def _detect_language(code: str, requested_language: Optional[str] = None) -> str:
    if requested_language:
        return requested_language
    if "public class" in code or "public static void main" in code:
        return "Java"
    return "Python"


@router.post("/generate", response_model=FixedCodeResponse)
async def generate_fixed_code(request: FixedCodeRequest):
    analysis_data = request.analysis_data or {}
    code_content = request.code_content or analysis_data.get("code_content")

    if not code_content or not str(code_content).strip():
        raise HTTPException(status_code=400, detail="No source code was provided to fix.")

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail=(
                "GROQ_API_KEY is not configured on the server. "
                "Add it to backend/.env and restart the backend."
            ),
        )

    language = _detect_language(str(code_content), request.language or analysis_data.get("language"))

    try:
        generator = FixedCodeGenerator()
        result = generator.generate_fixed_code(
            code_content=str(code_content),
            language=language,
            analysis_data=analysis_data,
            file_name=request.file_name,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Fixed code generation failed: {exc}")

    return FixedCodeResponse(
        success=True,
        language=language,
        fixed_code=result["fixed_code"],
        summary=result["summary"],
        # changes=result["changes"],
        # warnings=result["warnings"],
        confidence=result["confidence"],
        model=result["model"],
        message="Fixed code generated successfully.",
    )


@router.get("/health")
async def fixed_code_health():
    return {
        "feature": "Fixed Code",
        "status": "ok",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
    }
