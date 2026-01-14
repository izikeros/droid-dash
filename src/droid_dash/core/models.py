"""Data models for Factory.ai session analytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TokenUsage:
    """Token usage statistics for a session."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    thinking_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
            + self.thinking_tokens
        )

    @property
    def cache_hit_ratio(self) -> float:
        """Ratio of cache reads to total cache operations."""
        total_cache = self.cache_creation_tokens + self.cache_read_tokens
        if total_cache == 0:
            return 0.0
        return self.cache_read_tokens / total_cache

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_creation_tokens=self.cache_creation_tokens
            + other.cache_creation_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            thinking_tokens=self.thinking_tokens + other.thinking_tokens,
        )


@dataclass
class UserPrompt:
    """Represents a single user prompt from a session."""

    index: int
    timestamp: datetime | None
    text: str
    char_count: int


@dataclass
class Session:
    """Represents a single Factory.ai session."""

    id: str
    project_path: str
    project_name: str
    project_group: str
    title: str
    timestamp: datetime | None
    model: str
    autonomy_mode: str
    active_time_ms: int
    tokens: TokenUsage
    message_count: int = 0
    user_prompt_count: int = 0
    is_favorite: bool = False
    cwd: str | None = None  # Original working directory from session_start

    @property
    def active_time_minutes(self) -> float:
        return self.active_time_ms / 60000

    @property
    def active_time_hours(self) -> float:
        return self.active_time_ms / 3600000


@dataclass
class Project:
    """Represents a project with aggregated session stats."""

    name: str
    path: str
    group: str
    sessions: list[Session] = field(default_factory=list)

    @property
    def session_count(self) -> int:
        return len(self.sessions)

    @property
    def total_tokens(self) -> TokenUsage:
        result = TokenUsage()
        for session in self.sessions:
            result = result + session.tokens
        return result

    @property
    def total_active_time_ms(self) -> int:
        return sum(s.active_time_ms for s in self.sessions)

    @property
    def first_session_date(self) -> datetime | None:
        dates = [s.timestamp for s in self.sessions if s.timestamp]
        return min(dates) if dates else None

    @property
    def last_session_date(self) -> datetime | None:
        dates = [s.timestamp for s in self.sessions if s.timestamp]
        return max(dates) if dates else None


@dataclass
class ProjectGroup:
    """Represents a group of projects (e.g., 'eyproj', 'priv')."""

    name: str
    projects: list[Project] = field(default_factory=list)

    @property
    def session_count(self) -> int:
        return sum(p.session_count for p in self.projects)

    @property
    def project_count(self) -> int:
        return len(self.projects)

    @property
    def total_tokens(self) -> TokenUsage:
        result = TokenUsage()
        for project in self.projects:
            result = result + project.total_tokens
        return result

    @property
    def total_active_time_ms(self) -> int:
        return sum(p.total_active_time_ms for p in self.projects)


@dataclass
class DashboardStats:
    """Overall dashboard statistics."""

    total_sessions: int
    total_tokens: TokenUsage
    total_active_time_ms: int
    project_groups: list[ProjectGroup]
    projects: list[Project]
    sessions: list[Session]
    date_range: tuple[datetime | None, datetime | None]
    model_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def total_active_hours(self) -> float:
        return self.total_active_time_ms / 3600000
