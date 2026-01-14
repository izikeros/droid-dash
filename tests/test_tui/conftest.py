"""Shared fixtures for TUI tests."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from droid_dash.tui.app import FactoryDashboardApp

# Path to test sessions data
TEST_SESSIONS_DIR = Path(__file__).parent.parent.parent / "test_sessions"


@pytest.fixture
def test_sessions_dir():
    """Return path to test sessions directory."""
    return str(TEST_SESSIONS_DIR)


@pytest.fixture
def app(test_sessions_dir):
    """Create a test app instance."""
    return FactoryDashboardApp(sessions_dir=test_sessions_dir)
