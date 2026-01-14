"""Tests for session parser."""

import json
import tempfile
from pathlib import Path

from droid_dash.core.models import TokenUsage
from droid_dash.core.parser import SessionParser


class TestSessionParser:
    """Tests for SessionParser."""

    def test_parser_initialization_default_path(self):
        """Test parser initializes with default path."""
        parser = SessionParser()
        assert parser.sessions_dir is not None

    def test_parser_initialization_custom_path(self):
        """Test parser initializes with custom path."""
        parser = SessionParser("/custom/path")
        assert parser.sessions_dir == Path("/custom/path")

    def test_parse_empty_directory(self):
        """Test parsing empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = SessionParser(tmpdir)
            sessions = parser.parse_all_sessions()
            assert sessions == []

    def test_parse_session_with_settings_json(self):
        """Test parsing a session with .settings.json file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project directory structure
            project_dir = Path(tmpdir) / "-Users-test-projects-work-myproject"
            project_dir.mkdir()

            # Create session-123.settings.json in project dir (not subdirectory)
            settings = {
                "model": "claude-sonnet-4-20250514",
                "autonomyMode": "supervised",
                "tokenUsage": {
                    "inputTokens": 1000,
                    "outputTokens": 500,
                    "cacheCreationTokens": 200,
                    "cacheReadTokens": 300,
                    "thinkingTokens": 50,
                },
                "assistantActiveTimeMs": 60000,
            }
            (project_dir / "session-123.settings.json").write_text(json.dumps(settings))

            # Create session-123.jsonl with session_start
            jsonl_content = (
                json.dumps(
                    {
                        "type": "session_start",
                        "cwd": "/Users/test/project",
                        "timestamp": "2025-01-14T10:00:00Z",
                    }
                )
                + "\n"
            )
            jsonl_content += (
                json.dumps(
                    {
                        "type": "user",
                        "message": {"content": "Hello"},
                        "timestamp": "2025-01-14T10:01:00Z",
                    }
                )
                + "\n"
            )
            (project_dir / "session-123.jsonl").write_text(jsonl_content)

            # Parse
            parser = SessionParser(tmpdir)
            sessions = parser.parse_all_sessions()

            assert len(sessions) == 1
            session = sessions[0]
            assert session.id == "session-123"
            assert session.model == "claude-sonnet-4-20250514"
            assert session.tokens.input_tokens == 1000
            assert session.tokens.output_tokens == 500
            assert session.cwd == "/Users/test/project"

    def test_parse_extracts_project_info(self):
        """Test that project path and group are extracted correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project directory structure
            project_dir = Path(tmpdir) / "-Users-demo-projects-work-api"
            project_dir.mkdir()

            # Create session file directly in project dir
            settings = {"model": "claude-sonnet-4-20250514"}
            (project_dir / "session-456.settings.json").write_text(json.dumps(settings))

            parser = SessionParser(tmpdir)
            sessions = parser.parse_all_sessions()

            assert len(sessions) == 1
            session = sessions[0]
            assert session.project_group == "work"


class TestTokenUsage:
    """Tests for TokenUsage model."""

    def test_total_tokens(self):
        """Test total tokens calculation."""
        tokens = TokenUsage(
            input_tokens=100,
            output_tokens=200,
            cache_creation_tokens=50,
            cache_read_tokens=150,
            thinking_tokens=25,
        )

        assert tokens.total_tokens == 525

    def test_cache_hit_ratio(self):
        """Test cache hit ratio calculation."""
        tokens = TokenUsage(
            input_tokens=100,
            output_tokens=200,
            cache_creation_tokens=100,
            cache_read_tokens=400,
            thinking_tokens=0,
        )

        # cache_read / (cache_read + cache_creation) = 400 / 500 = 0.8
        assert tokens.cache_hit_ratio == 0.8

    def test_cache_hit_ratio_zero_cache(self):
        """Test cache hit ratio with no cache usage."""
        tokens = TokenUsage(
            input_tokens=100,
            output_tokens=200,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            thinking_tokens=0,
        )

        assert tokens.cache_hit_ratio == 0.0


class TestFavorites:
    """Tests for favorites functionality."""

    def test_load_favorites_empty(self):
        """Test loading favorites from empty/nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = SessionParser(tmpdir)
            # No .favorites file exists, _favorites should be empty set
            assert parser._favorites == set()

    def test_save_and_load_favorites(self):
        """Test saving and loading favorites."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = SessionParser(tmpdir)

            # Add favorites
            parser.toggle_favorite("session-1")
            parser.toggle_favorite("session-2")

            # Reload and check
            parser2 = SessionParser(tmpdir)
            assert "session-1" in parser2._favorites
            assert "session-2" in parser2._favorites

    def test_toggle_favorite_removes(self):
        """Test that toggling favorite twice removes it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = SessionParser(tmpdir)

            parser.toggle_favorite("session-1")
            assert "session-1" in parser._favorites

            parser.toggle_favorite("session-1")
            assert "session-1" not in parser._favorites
