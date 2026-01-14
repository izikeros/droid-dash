"""Parser for Factory.ai session files."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from .models import Session, TokenUsage, UserPrompt


class SessionParser:
    """Parses Factory.ai session data from .settings.json and .jsonl files."""

    def __init__(self, sessions_dir: str | None = None):
        if sessions_dir is None:
            sessions_dir = os.path.expanduser("~/.factory/sessions")
        self.sessions_dir = Path(sessions_dir)
        self._favorites: set[str] = set()
        self._load_favorites()

    def _load_favorites(self) -> None:
        """Load favorite session IDs from .favorites file."""
        favorites_file = self.sessions_dir / ".favorites"
        if favorites_file.exists():
            try:
                with open(favorites_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._favorites = set(data)
            except (OSError, json.JSONDecodeError):
                pass

    def save_favorites(self) -> bool:
        """Save favorites to .favorites file."""
        favorites_file = self.sessions_dir / ".favorites"
        try:
            with open(favorites_file, "w") as f:
                json.dump(list(self._favorites), f, indent=2)
            return True
        except OSError:
            return False

    def toggle_favorite(self, session_id: str) -> bool:
        """Toggle favorite status for a session. Returns new status."""
        if session_id in self._favorites:
            self._favorites.discard(session_id)
            is_favorite = False
        else:
            self._favorites.add(session_id)
            is_favorite = True
        self.save_favorites()
        return is_favorite

    def parse_all_sessions(self) -> list[Session]:
        """Parse all sessions from the sessions directory."""
        sessions = []
        if not self.sessions_dir.exists():
            return sessions

        for project_dir in self.sessions_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith("."):
                continue

            for settings_file in project_dir.glob("*.settings.json"):
                session = self._parse_session(settings_file, project_dir.name)
                if session:
                    sessions.append(session)

        return sessions

    def _parse_session(
        self, settings_path: Path, project_dir_name: str
    ) -> Session | None:
        """Parse a single session from its settings file."""
        try:
            with open(settings_path) as f:
                settings = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        session_id = settings_path.stem.replace(".settings", "")
        jsonl_path = settings_path.parent / f"{session_id}.jsonl"

        project_path, project_name, project_group = self._parse_project_info(
            project_dir_name
        )
        title, timestamp, message_count, user_prompt_count, cwd = self._parse_jsonl(
            jsonl_path
        )

        token_usage = settings.get("tokenUsage", {})
        tokens = TokenUsage(
            input_tokens=token_usage.get("inputTokens", 0),
            output_tokens=token_usage.get("outputTokens", 0),
            cache_creation_tokens=token_usage.get("cacheCreationTokens", 0),
            cache_read_tokens=token_usage.get("cacheReadTokens", 0),
            thinking_tokens=token_usage.get("thinkingTokens", 0),
        )

        return Session(
            id=session_id,
            project_path=project_path,
            project_name=project_name,
            project_group=project_group,
            title=title,
            timestamp=timestamp,
            model=settings.get("model", "unknown"),
            autonomy_mode=settings.get("autonomyMode", "unknown"),
            active_time_ms=settings.get("assistantActiveTimeMs", 0),
            tokens=tokens,
            message_count=message_count,
            user_prompt_count=user_prompt_count,
            is_favorite=session_id in self._favorites,
            cwd=cwd,
        )

    def _parse_project_info(self, project_dir_name: str) -> tuple[str, str, str]:
        """Extract project path, name, and group from directory name.

        Directory names are encoded paths like:
        -Users-Krystian.Safjan-projects-eyproj-atlas_qa
        -Users-Krystian.Safjan-projects-priv-blog
        """
        path = project_dir_name.replace("-", "/")
        if path.startswith("/"):
            path = path[1:]

        parts = path.split("/")
        project_name = parts[-1] if parts else "unknown"

        project_group = "other"
        if "projects" in parts:
            proj_idx = parts.index("projects")
            if proj_idx + 1 < len(parts):
                project_group = parts[proj_idx + 1]

        return "/" + path, project_name, project_group

    def _normalize_title(self, title: str | None) -> str:
        """Normalize title, returning 'Untitled Session' for empty/invalid titles."""
        if not title or not title.strip():
            return "Untitled Session"
        return title.strip()[:80]

    def _is_user_prompt(self, entry: dict) -> bool:
        """Check if a message entry contains an actual user prompt (not system/tool)."""
        if entry.get("type") != "message":
            return False

        msg = entry.get("message", {})
        if msg.get("role") != "user":
            return False

        content = msg.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Skip system reminders and very short texts
                if text.startswith(("<system-reminder>", "<system")):
                    continue
                if len(text.strip()) > 10:
                    return True
            elif item.get("type") == "tool_result":
                # Tool results are not user prompts
                continue

        return False

    def _extract_user_prompt_text(self, entry: dict) -> str | None:
        """Extract the actual user prompt text from a message entry."""
        msg = entry.get("message", {})
        content = msg.get("content", [])

        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Skip system reminders
                if text.startswith(("<system-reminder>", "<system")):
                    continue
                if len(text.strip()) > 10:
                    return text.strip()

        return None

    def _parse_jsonl(
        self, jsonl_path: Path
    ) -> tuple[str, datetime | None, int, int, str | None]:
        """Parse session title, timestamp, message count, user prompt count, and cwd from jsonl file."""
        title = "Untitled Session"
        timestamp = None
        message_count = 0
        user_prompt_count = 0
        cwd = None

        if not jsonl_path.exists():
            return title, timestamp, message_count, user_prompt_count, cwd

        try:
            with open(jsonl_path) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_type = entry.get("type")

                        if entry_type == "session_start":
                            # Prefer sessionTitle if available, otherwise fallback to title
                            raw_title = entry.get("sessionTitle") or entry.get("title")
                            title = self._normalize_title(raw_title)
                            cwd = entry.get("cwd")

                        elif entry_type == "message":
                            message_count += 1
                            if timestamp is None:
                                ts_str = entry.get("timestamp")
                                if ts_str:
                                    timestamp = self._parse_timestamp(ts_str)

                            # Count user prompts
                            if self._is_user_prompt(entry):
                                user_prompt_count += 1
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass

        return title, timestamp, message_count, user_prompt_count, cwd

    def get_session_prompts(self, session_id: str) -> list[UserPrompt]:
        """Extract all user prompts from a session.

        Returns a list of UserPrompt objects with the actual user messages.
        """
        jsonl_path = self.find_session_jsonl_path(session_id)
        if not jsonl_path:
            return []

        prompts = []
        index = 0

        try:
            with open(jsonl_path) as f:
                for line in f:
                    try:
                        entry = json.loads(line)

                        if self._is_user_prompt(entry):
                            text = self._extract_user_prompt_text(entry)
                            if text:
                                index += 1
                                ts_str = entry.get("timestamp")
                                timestamp = (
                                    self._parse_timestamp(ts_str) if ts_str else None
                                )

                                prompts.append(
                                    UserPrompt(
                                        index=index,
                                        timestamp=timestamp,
                                        text=text,
                                        char_count=len(text),
                                    )
                                )
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass

        return prompts

    def find_session_jsonl_path(self, session_id: str) -> Path | None:
        """Find the .jsonl file path for a given session ID."""
        if not self.sessions_dir.exists():
            return None

        for project_dir in self.sessions_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith("."):
                continue

            jsonl_path = project_dir / f"{session_id}.jsonl"
            if jsonl_path.exists():
                return jsonl_path

        return None

    def update_session_title(self, session_id: str, new_title: str) -> bool:
        """Update session title in the .jsonl file.

        Returns True if successful, False otherwise.
        """
        jsonl_path = self.find_session_jsonl_path(session_id)
        if not jsonl_path:
            return False

        new_title = self._normalize_title(new_title)

        try:
            with open(jsonl_path) as f:
                lines = f.readlines()

            if not lines:
                return False

            # Parse and update the first line (session_start)
            first_entry = json.loads(lines[0])
            if first_entry.get("type") != "session_start":
                return False

            # Update both title and sessionTitle to ensure consistency in Droid TUI
            first_entry["title"] = new_title
            if "sessionTitle" in first_entry:
                first_entry["sessionTitle"] = new_title

            lines[0] = json.dumps(first_entry) + "\n"

            with open(jsonl_path, "w") as f:
                f.writelines(lines)

            return True
        except (OSError, json.JSONDecodeError):
            return False

    def _parse_timestamp(self, ts_str: str) -> datetime | None:
        """Parse ISO timestamp string."""
        try:
            ts_str = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            return None
