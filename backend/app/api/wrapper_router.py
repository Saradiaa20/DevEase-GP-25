"""
wrapper_router.py
Wrapper Generator — Step 3: FastAPI router.

Exposes:
  POST /api/wrapper/analyze/file     — multipart file upload
  POST /api/wrapper/analyze/content  — raw code string in JSON body
  GET  /api/wrapper/health           — sanity check

Mount in backend/app/main.py with:
    from wrapper_router import router as wrapper_router
    app.include_router(wrapper_router)
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from pydantic import BaseModel

# ── Make sure backend/ is on sys.path so local imports work when this
#    router is imported from backend/app/main.py ──────────────────────────────
_backend_dir = Path(__file__).resolve().parent          # backend/
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.ml.wrapper_detector import detect_unsafe_patterns, patterns_to_dict
from app.services.ai.wrapper_groq import WrapperSuggestionGenerator
from app.services.file_handler import FileHandler   # already in this project


router = APIRouter(prefix="/api/wrapper", tags=["Wrapper Generator"])


# ─── Pydantic models ─────────────────────────────────────────────────────────

class WrapperContentRequest(BaseModel):
    content:  str
    language: Optional[str] = None   # "Python" | "Java" | None → auto-detect


class WrapperResponse(BaseModel):
    success:        bool
    language:       str
    patterns_found: int
    patterns:       list
    suggestions:    list
    message:        str


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _detect_language(code: str, filename: str = "") -> str:
    ext = Path(filename).suffix.lower()
    if ext in (".py", ".pyw"):  return "Python"
    if ext == ".java":          return "Java"
    if "public class" in code or "public static void main" in code:
        return "Java"
    return "Python"


def _run(code: str, language: str) -> WrapperResponse:
    """Core pipeline: detect → suggest → respond."""
    patterns = detect_unsafe_patterns(code, language)

    if not patterns:
        return WrapperResponse(
            success=True,
            language=language,
            patterns_found=0,
            patterns=[],
            suggestions=[],
            message="No unsafe patterns detected. Your code looks safe!",
        )

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "GROQ_API_KEY is not configured on the server. "
                "Add it to backend/.env and make sure load_dotenv() is called."
            ),
        )

    gen         = WrapperSuggestionGenerator(api_key=groq_key)
    suggestions = gen.generate_all_suggestions(patterns, code)

    return WrapperResponse(
        success=True,
        language=language,
        patterns_found=len(patterns),
        patterns=patterns_to_dict(patterns),
        suggestions=suggestions,
        message=(
            f"Found {len(patterns)} unsafe pattern(s). "
            f"Generated {len(suggestions)} suggestion(s)."
        ),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/analyze/file", response_model=WrapperResponse)
async def analyze_file_for_wrappers(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Upload a .py or .java file and receive unsafe-pattern detections + suggestions."""
    ext = Path(file.filename).suffix.lower()
    if ext not in FileHandler.SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    await file.seek(0)
    raw = await file.read()

    try:
        code = raw.decode("utf-8")
    except UnicodeDecodeError:
        code = raw.decode("latin-1", errors="replace")

    if not code.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    language = _detect_language(code, file.filename)

    try:
        return _run(code, language)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@router.post("/analyze/content", response_model=WrapperResponse)
async def analyze_content_for_wrappers(
    request: WrapperContentRequest,
    authorization: Optional[str] = Header(None),
):
    """Paste code directly and receive unsafe-pattern detections + suggestions."""
    if not request.content or not request.content.strip():
        raise HTTPException(status_code=400, detail="No code content provided.")

    language = request.language or _detect_language(request.content)

    try:
        return _run(request.content, language)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@router.get("/health")
async def wrapper_health():
    """Quick health check for the Wrapper Generator feature."""
    return {
        "feature":         "Wrapper Generator",
        "status":          "ok",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
    }
