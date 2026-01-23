"""Aggregation logic for session statistics."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any

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

    def get_daily_stats(self) -> dict[str, Any]:
        """Calculate daily usage statistics including medians and peak days."""
        daily_tokens: dict[date, int] = defaultdict(int)
        daily_time: dict[date, int] = defaultdict(int)

        for session in self.sessions:
            if session.timestamp:
                d = session.timestamp.date()
                daily_tokens[d] += session.tokens.total_tokens
                daily_time[d] += session.active_time_ms

        if not daily_tokens:
            return {
                "median_daily_tokens": 0,
                "median_daily_time_ms": 0,
                "peak_token_day": None,
                "peak_time_day": None,
            }

        # Calculate medians
        token_values = sorted(daily_tokens.values())
        time_values = sorted(daily_time.values())
        n_tokens = len(token_values)
        n_time = len(time_values)

        if n_tokens % 2 == 0:
            median_tokens = (
                token_values[n_tokens // 2 - 1] + token_values[n_tokens // 2]
            ) // 2
        else:
            median_tokens = token_values[n_tokens // 2]

        if n_time % 2 == 0:
            median_time = (
                time_values[n_time // 2 - 1] + time_values[n_time // 2]
            ) // 2
        else:
            median_time = time_values[n_time // 2]

        # Find peak days
        peak_token_day = max(daily_tokens.items(), key=lambda x: x[1])
        peak_time_day = max(daily_time.items(), key=lambda x: x[1])

        return {
            "median_daily_tokens": median_tokens,
            "median_daily_time_ms": median_time,
            "peak_token_day": peak_token_day,
            "peak_time_day": peak_time_day,
        }

    def get_weekly_stats(self) -> dict[str, Any]:
        """Calculate weekly usage statistics."""
        weekly_tokens: dict[tuple[int, int], int] = defaultdict(int)
        weekly_time: dict[tuple[int, int], int] = defaultdict(int)

        for session in self.sessions:
            if session.timestamp:
                iso_cal = session.timestamp.isocalendar()
                week_key = (iso_cal.year, iso_cal.week)
                weekly_tokens[week_key] += session.tokens.total_tokens
                weekly_time[week_key] += session.active_time_ms

        if not weekly_tokens:
            return {
                "avg_weekly_tokens": 0,
                "avg_weekly_time_ms": 0,
                "peak_week": None,
                "num_weeks": 0,
            }

        avg_weekly_tokens = sum(weekly_tokens.values()) // len(weekly_tokens)
        avg_weekly_time = sum(weekly_time.values()) // len(weekly_time)
        peak_week = max(weekly_tokens.items(), key=lambda x: x[1])

        return {
            "avg_weekly_tokens": avg_weekly_tokens,
            "avg_weekly_time_ms": avg_weekly_time,
            "peak_week": peak_week,
            "num_weeks": len(weekly_tokens),
        }

    def get_monthly_stats(self) -> dict[str, Any]:
        """Calculate monthly usage statistics."""
        monthly_tokens: dict[tuple[int, int], int] = defaultdict(int)
        monthly_time: dict[tuple[int, int], int] = defaultdict(int)

        for session in self.sessions:
            if session.timestamp:
                month_key = (session.timestamp.year, session.timestamp.month)
                monthly_tokens[month_key] += session.tokens.total_tokens
                monthly_time[month_key] += session.active_time_ms

        if not monthly_tokens:
            return {
                "avg_monthly_tokens": 0,
                "avg_monthly_time_ms": 0,
                "peak_month": None,
                "num_months": 0,
            }

        avg_monthly_tokens = sum(monthly_tokens.values()) // len(monthly_tokens)
        avg_monthly_time = sum(monthly_time.values()) // len(monthly_time)
        peak_month = max(monthly_tokens.items(), key=lambda x: x[1])

        return {
            "avg_monthly_tokens": avg_monthly_tokens,
            "avg_monthly_time_ms": avg_monthly_time,
            "peak_month": peak_month,
            "num_months": len(monthly_tokens),
        }

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

    def get_daily_totals(self) -> tuple[dict[date, int], dict[date, int]]:
        """Get daily token totals and active time totals.

        Returns:
            Tuple of (daily_tokens, daily_time_ms) dictionaries.
        """
        daily_tokens: dict[date, int] = defaultdict(int)
        daily_time: dict[date, int] = defaultdict(int)

        for session in self.sessions:
            if session.timestamp:
                d = session.timestamp.date()
                daily_tokens[d] += session.tokens.total_tokens
                daily_time[d] += session.active_time_ms

        return dict(daily_tokens), dict(daily_time)

    def get_daily_tokens_by_project(self, day: date) -> list[tuple[str, int]]:
        """Get token usage for a specific day grouped by project.

        Args:
            day: The date to get stats for.

        Returns:
            List of (project_name, tokens) tuples sorted by tokens descending.
        """
        project_tokens: dict[str, int] = defaultdict(int)

        for session in self.sessions:
            if session.timestamp and session.timestamp.date() == day:
                project_tokens[session.project_name] += session.tokens.total_tokens

        return sorted(project_tokens.items(), key=lambda x: x[1], reverse=True)

    def get_dates_with_activity(self) -> list[date]:
        """Get list of dates that have session activity, sorted descending."""
        dates = set()
        for session in self.sessions:
            if session.timestamp:
                dates.add(session.timestamp.date())
        return sorted(dates, reverse=True)

    def get_project_daily_tokens(self) -> dict[str, dict[date, int]]:
        """Get daily token usage per project.

        Returns:
            Dict mapping project_name -> {date -> tokens}, with projects sorted
            by total tokens descending.
        """
        by_project: dict[str, dict[date, int]] = defaultdict(lambda: defaultdict(int))

        for session in self.sessions:
            if session.timestamp:
                d = session.timestamp.date()
                by_project[session.project_name][d] += session.tokens.total_tokens

        # Sort projects by total tokens desc, preserving order in returned dict
        totals = {
            proj: sum(day_map.values())
            for proj, day_map in by_project.items()
        }
        sorted_projects = sorted(totals.keys(), key=lambda p: totals[p], reverse=True)

        result: dict[str, dict[date, int]] = {}
        for proj in sorted_projects:
            result[proj] = dict(by_project[proj])
        return result
