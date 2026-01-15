"""Project grouping logic for session analytics."""

from __future__ import annotations

from collections import defaultdict

from .models import Project, ProjectGroup, Session


class ProjectGrouper:
    """Groups sessions by project and project group."""

    def __init__(self, sessions: list[Session]):
        self.sessions = sessions
        self._projects: dict[str, Project] = {}
        self._groups: dict[str, ProjectGroup] = {}
        self._build_hierarchy()

    def _sort_key(self, session: Session) -> tuple:
        """Create a sortable key for sessions, handling None timestamps."""
        if session.timestamp:
            return (1, session.timestamp)
        return (0, session.id)

    def _build_hierarchy(self) -> None:
        """Build project and group hierarchy from sessions."""
        project_sessions: dict[
            tuple[str, str, str], list[Session]
        ] = defaultdict(list)

        for session in self.sessions:
            key = (session.project_path, session.project_name, session.project_group)
            project_sessions[key].append(session)

        for (path, name, group), sessions in project_sessions.items():
            project = Project(
                name=name,
                path=path,
                group=group,
                sessions=sorted(sessions, key=self._sort_key, reverse=True),
            )
            self._projects[path] = project

            if group not in self._groups:
                self._groups[group] = ProjectGroup(name=group)
            self._groups[group].projects.append(project)

        for group in self._groups.values():
            group.projects.sort(key=lambda p: p.session_count, reverse=True)

    def get_all_groups(self) -> list[ProjectGroup]:
        """Get all project groups sorted by session count."""
        return sorted(
            self._groups.values(), key=lambda g: g.session_count, reverse=True
        )

    def get_group(self, name: str) -> ProjectGroup | None:
        """Get a specific project group by name."""
        return self._groups.get(name)

    def get_all_projects(self) -> list[Project]:
        """Get all projects sorted by session count."""
        return sorted(
            self._projects.values(), key=lambda p: p.session_count, reverse=True
        )

    def get_project(self, path: str) -> Project | None:
        """Get a specific project by path."""
        return self._projects.get(path)

    def get_projects_in_group(self, group_name: str) -> list[Project]:
        """Get all projects in a specific group."""
        group = self._groups.get(group_name)
        return group.projects if group else []

    def get_group_names(self) -> list[str]:
        """Get list of all group names."""
        return sorted(self._groups.keys())
