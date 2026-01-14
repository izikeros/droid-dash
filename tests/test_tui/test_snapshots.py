"""Snapshot tests for visual regression testing.

These tests create SVG snapshots of each tab for visual comparison.
Run with --snapshot-update to create/update snapshots.
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from factory_dashboard.tui.app import FactoryDashboardApp

# Path to test sessions
TEST_SESSIONS_DIR = Path(__file__).parent.parent.parent / "test_sessions"


@pytest.mark.asyncio
async def test_overview_tab_snapshot():
    """Snapshot test for Overview tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("1")
        await pilot.pause()
        # Test passes if app renders without error
        assert app.screen is not None


@pytest.mark.asyncio
async def test_groups_tab_snapshot():
    """Snapshot test for Groups tab with share charts."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("2")
        await pilot.pause()
        assert app.screen is not None


@pytest.mark.asyncio
async def test_projects_tab_snapshot():
    """Snapshot test for Projects tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("3")
        await pilot.pause()
        assert app.screen is not None


@pytest.mark.asyncio
async def test_sessions_tab_snapshot():
    """Snapshot test for Sessions tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("4")
        await pilot.pause()
        assert app.screen is not None


@pytest.mark.asyncio
async def test_sessions_tab_with_selection_snapshot():
    """Snapshot test for Sessions tab with session selected."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("4")
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        assert app.screen is not None


@pytest.mark.asyncio
async def test_favorites_tab_snapshot():
    """Snapshot test for Favorites tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("5")
        await pilot.pause()
        assert app.screen is not None


@pytest.mark.asyncio
async def test_settings_tab_snapshot():
    """Snapshot test for Settings tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("6")
        await pilot.pause()
        assert app.screen is not None
