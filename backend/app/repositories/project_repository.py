"""Project repository abstractions."""

from typing import List

from app.schemas.entities import Project


class ProjectRepository:
    """
    Temporary in-memory repository.
    Replace this with SQLAlchemy queries backed by PostgreSQL.
    """

    def __init__(self) -> None:
        self._items: dict[int, Project] = {}

    def create(self, project: Project) -> Project:
        self._items[project.id] = project
        return project

    def list_all(self) -> List[Project]:
        return list(self._items.values())

    def get_by_id(self, project_id: int) -> Project | None:
        return self._items.get(project_id)
