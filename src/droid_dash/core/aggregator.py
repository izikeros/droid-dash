"""Aggregation logic for session statistics."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone

from .grouping import ProjectGrouper
from .models import DashboardStats, Project, Session, TokenUsage

MIN_DATETIME = datetime.min.replace(tzinfo=timezone.utc)


class SessionAggregator:
    """Aggregates session data into statistics."""

    def __init__(self, sessions: list[Session]):
        self.sessions = sessions
        self.grouper = ProjectGrouper(sessions)

    def _session_sort_key(self, session: Session) -> tuple:
        """Create a sortable key for sessions."""
        if session.timestamp:
            ts = session.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return (1, ts)
        return (0, session.id)

    def get_dashboard_stats(self) -> DashboardStats:
        """Get overall dashboard statistics."""
        total_tokens = TokenUsage()
        total_active_time = 0
        model_dist: dict[str, int] = defaultdict(int)

        timestamps = []
        for session in self.sessions:
            total_tokens = total_tokens + session.tokens
            total_active_time += session.active_time_ms
            model_dist[session.model] += 1
            if session.timestamp:
                timestamps.append(session.timestamp)

        date_range = (min(timestamps), max(timestamps)) if timestamps else (None, None)

        return DashboardStats(
            total_sessions=len(self.sessions),
            total_tokens=total_tokens,
            total_active_time_ms=total_active_time,
            project_groups=self.grouper.get_all_groups(),
            projects=self.grouper.get_all_projects(),
            sessions=sorted(
                self.sessions,
                key=self._session_sort_key,
                reverse=True,
            ),
            date_range=date_range,
            model_distribution=dict(model_dist),
        )

    def get_activity_by_date(self) -> dict[date, list[Session]]:
        """Get sessions grouped by date for activity heatmap."""
        by_date: dict[date, list[Session]] = defaultdict(list)
        for session in self.sessions:
            if session.timestamp:
                d = session.timestamp.date()
                by_date[d].append(session)
        return dict(by_date)

    def get_daily_token_usage(self) -> dict[date, TokenUsage]:
        """Get token usage aggregated by date."""
        by_date: dict[date, TokenUsage] = defaultdict(TokenUsage)
        for session in self.sessions:
            if session.timestamp:
                d = session.timestamp.date()
                by_date[d] = by_date[d] + session.tokens
        return dict(by_date)

    def get_sessions_by_model(self) -> dict[str, list[Session]]:
        """Get sessions grouped by model."""
        by_model: dict[str, list[Session]] = defaultdict(list)
        for session in self.sessions:
            by_model[session.model].append(session)
        return dict(by_model)

    def get_top_projects_by_tokens(self, limit: int = 10) -> list[Project]:
        """Get top projects by token usage."""
        projects = self.grouper.get_all_projects()
        return sorted(
            projects,
            key=lambda p: p.total_tokens.total_tokens,
            reverse=True,
        )[:limit]

    def get_top_projects_by_sessions(self, limit: int = 10) -> list[Project]:
        """Get top projects by session count."""
        return self.grouper.get_all_projects()[:limit]

    def filter_sessions(
        self,
        group: str | None = None,
        project: str | None = None,
        model: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Session]:
        """Filter sessions by various criteria."""
        result = self.sessions

        if group:
            result = [s for s in result if s.project_group == group]
        if project:
            result = [s for s in result if s.project_name == project]
        if model:
            result = [s for s in result if s.model == model]
        if start_date:
            result = [
                s for s in result if s.timestamp and s.timestamp.date() >= start_date
            ]
        if end_date:
            result = [
                s for s in result if s.timestamp and s.timestamp.date() <= end_date
            ]

        return result
