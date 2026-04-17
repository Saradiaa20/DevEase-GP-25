"""Primary schema entities used by authentication and project APIs."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    DEVELOPER = "developer"
    TEAM_LEAD = "team_lead"


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    role: UserRole = UserRole.DEVELOPER
    created_at: Optional[datetime] = None
    is_active: bool = True


class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AnalysisResult(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    file_name: str
    file_path: Optional[str] = None
    analysis_data: Dict[str, Any]
    created_at: Optional[datetime] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.DEVELOPER


class UserLogin(BaseModel):
    username: str
    password: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
