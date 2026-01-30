"""
Database models for user authentication and project management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    DEVELOPER = "developer"
    TEAM_LEAD = "team_lead"

class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    username: str
    email: EmailStr
    role: UserRole = UserRole.DEVELOPER
    created_at: Optional[datetime] = None
    is_active: bool = True

class Project(BaseModel):
    """Project model"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AnalysisResult(BaseModel):
    """Analysis result model"""
    id: Optional[int] = None
    project_id: Optional[int] = None
    file_name: str
    file_path: Optional[str] = None
    analysis_data: Dict[str, Any]
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.DEVELOPER

class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str

class ProjectCreate(BaseModel):
    """Project creation model"""
    name: str
    description: Optional[str] = None

class Token(BaseModel):
    """Authentication token model"""
    access_token: str
    token_type: str = "bearer"
