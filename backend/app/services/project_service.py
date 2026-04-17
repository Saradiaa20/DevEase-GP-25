"""Project-related business logic."""

from datetime import datetime

from app.repositories.project_repository import ProjectRepository
from app.schemas.entities import Project, ProjectCreate


class ProjectService:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self.project_repository = project_repository
        self._counter = 1

    def create_project(self, payload: ProjectCreate, owner_id: int) -> Project:
        project = Project(
            id=self._counter,
            name=payload.name,
            description=payload.description,
            owner_id=owner_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self._counter += 1
        return self.project_repository.create(project)
