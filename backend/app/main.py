"""
FastAPI Backend for DevEase Code Complexity Analysis
Provides REST API endpoints for code analysis
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import modules
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from parsing import ASTParser
from file_handler import FileHandler
from feature_router import FeatureRouter
from app.models import (
    User, UserCreate, UserLogin, Project, ProjectCreate, 
    AnalysisResult, Token, UserRole
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    decode_token, check_permission, USERS_DB, PROJECTS_DB
)

app = FastAPI(
    title="DevEase API",
    description="Code Complexity Analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
parser = ASTParser()
file_handler = FileHandler()
feature_router = FeatureRouter()

# Security
security = HTTPBearer()

# Simple user counter (for demo - use database in production)
user_counter = 1
project_counter = 1
analysis_counter = 1

# Request/Response models
class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None

class FileAnalysisRequest(BaseModel):
    file_path: Optional[str] = None
    content: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DevEase API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "register": "/api/auth/register",
                "login": "/api/auth/login"
            },
            "projects": {
                "create": "/api/projects",
                "list": "/api/projects",
                "get": "/api/projects/{project_id}"
            },
            "analysis": {
                "analyze_file": "/api/analyze/file",
                "analyze_content": "/api/analyze/content",
                "analyze_path": "/api/analyze/{file_path}",
                "technical_debt": "/api/analysis/technical-debt"
            },
            "info": {
                "health": "/api/health",
                "supported_extensions": "/api/supported-extensions"
            }
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DevEase API",
        "version": "1.0.0"
    }


@app.get("/api/supported-extensions")
async def get_supported_extensions():
    """Get list of supported file extensions"""
    return {
        "supported_extensions": FileHandler.SUPPORTED_EXTENSIONS,
        "languages": {
            ".py": "Python",
            ".java": "Java",
            ".js": "JavaScript",
            ".cpp": "C++",
            ".cs": "C#",
            ".php": "PHP"
        }
    }

# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    global user_counter
    
    # Check if user exists
    if user_data.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=user_counter,
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    USERS_DB[user_data.username] = {
        "user": new_user,
        "password_hash": hashed_password
    }
    
    user_counter += 1
    return new_user

@app.post("/api/auth/login", response_model=Token)
async def login_user(credentials: UserLogin):
    """Login user and get access token"""
    user_data = USERS_DB.get(credentials.username)
    
    if not user_data or not verify_password(credentials.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not user_data["user"].is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": credentials.username, "role": user_data["user"].role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_data = USERS_DB.get(username)
    if user_data is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user_data["user"]

# ==================== Project Management Endpoints ====================

@app.post("/api/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project (Team Lead only)"""
    global project_counter
    
    if current_user.role != UserRole.TEAM_LEAD:
        raise HTTPException(status_code=403, detail="Only Team Leads can create projects")
    
    new_project = Project(
        id=project_counter,
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    PROJECTS_DB[project_counter] = new_project
    project_counter += 1
    
    return new_project

@app.get("/api/projects", response_model=List[Project])
async def list_projects(current_user: User = Depends(get_current_user)):
    """List projects (Developers see their projects, Team Leads see all)"""
    if current_user.role == UserRole.TEAM_LEAD:
        return list(PROJECTS_DB.values())
    else:
        # Developers see projects they own or are assigned to
        return [p for p in PROJECTS_DB.values() if p.owner_id == current_user.id]

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project = PROJECTS_DB.get(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    if current_user.role != UserRole.TEAM_LEAD and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project

# ==================== Enhanced Analysis Endpoints ====================

@app.post("/api/analyze/file", response_model=AnalysisResponse)
async def analyze_file_endpoint(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Analyze a code file uploaded via multipart/form-data
    Now uses FeatureRouter for complete analysis pipeline
    """
    try:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in FileHandler.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(FileHandler.SUPPORTED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Use FeatureRouter for complete analysis
            result = feature_router.analyze_code(file_path=tmp_path)
            
            # Store analysis result if project_id provided
            if project_id and current_user:
                global analysis_counter
                analysis_result = AnalysisResult(
                    id=analysis_counter,
                    project_id=project_id,
                    file_name=file.filename,
                    file_path=tmp_path,
                    analysis_data=result,
                    created_at=datetime.utcnow()
                )
                analysis_counter += 1
                # In production, save to database
            
            return AnalysisResponse(
                success=True,
                data=result,
                message="Analysis completed successfully"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/content", response_model=AnalysisResponse)
async def analyze_content_endpoint(
    request: FileAnalysisRequest,
    project_id: Optional[int] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Analyze code content provided directly in the request body
    Now uses FeatureRouter for complete analysis pipeline
    """
    try:
        if request.file_path:
            # Analyze from file path
            if not os.path.exists(request.file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            result = feature_router.analyze_code(file_path=request.file_path)
            
        elif request.content:
            # Analyze from content string
            result = feature_router.analyze_code(code_content=request.content)
        else:
            raise HTTPException(status_code=400, detail="Either file_path or content must be provided")
        
        return AnalysisResponse(
            success=True,
            data=result,
            message="Analysis completed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analyze/{file_path:path}", response_model=AnalysisResponse)
async def analyze_file_by_path(
    file_path: str,
    authorization: Optional[str] = Header(None)
):
    """
    Analyze a file by providing its path
    Now uses FeatureRouter for complete analysis pipeline
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        result = feature_router.analyze_code(file_path=file_path)
        
        return AnalysisResponse(
            success=True,
            data=result,
            message="Analysis completed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analysis/technical-debt")
async def get_technical_debt_summary(
    project_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get technical debt summary for a project"""
    # In production, aggregate from database
    # For now, return sample structure
    return {
        "message": "Technical debt summary endpoint",
        "note": "Aggregate technical debt from all project analyses"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
