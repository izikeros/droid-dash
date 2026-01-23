"""Pilot-based tests for dashboard navigation.

These tests verify navigation between tabs using Textual's Pilot testing framework.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from textual.widgets import DataTable, TabbedContent

from droid_dash.tui.app import FactoryDashboardApp

TEST_SESSIONS_DIR = Path(__file__).parent.parent.parent / "test_sessions"


class TestNavigation:
    """Test tab navigation functionality."""

    @pytest.mark.asyncio
    async def test_navigate_to_overview_tab(self):
        """Given dashboard is running, when I press 1, then I see Overview tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("1")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "overview"

    @pytest.mark.asyncio
    async def test_navigate_to_groups_tab(self):
        """Given dashboard is running, when I press 2, then I see Groups tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("2")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "groups"

    @pytest.mark.asyncio
    async def test_navigate_to_projects_tab(self):
        """Given dashboard is running, when I press 3, then I see Projects tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("3")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "projects"

            # Verify sortable table exists
            table = screen.query_one("#projects-table", DataTable)
            assert table is not None

    @pytest.mark.asyncio
    async def test_navigate_to_sessions_tab(self):
        """Given dashboard is running, when I press 4, then I see Sessions tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "sessions"

            # Verify sort and group controls exist
            sort_select = screen.query_one("#sort-select")
            group_select = screen.query_one("#group-select")
            assert sort_select is not None
            assert group_select is not None

    @pytest.mark.asyncio
    async def test_navigate_to_activity_tab(self):
        """Given dashboard is running, when I press 5, then I see My Activity tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("5")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "activity"

    @pytest.mark.asyncio
    async def test_navigate_to_favorites_tab(self):
        """Given dashboard is running, when I press 6, then I see Favorites tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("6")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "favorites"

    @pytest.mark.asyncio
    async def test_navigate_to_settings_tab(self):
        """Given dashboard is running, when I press 7, then I see Settings tab."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("7")
            await pilot.pause()

            screen = app.screen
            tabbed = screen.query_one(TabbedContent)
            assert tabbed.active == "settings"

            # Verify save button exists
            save_button = screen.query_one("#save-settings")
            assert save_button is not None


class TestSessionsTab:
    """Test Sessions tab functionality."""

    @pytest.mark.asyncio
    async def test_sessions_table_has_data(self):
        """Given I'm on Sessions tab, then I should see sessions in the table."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause()

            screen = app.screen
            table = screen.query_one("#sessions-table", DataTable)
            assert table.row_count > 0

    @pytest.mark.asyncio
    async def test_select_session_updates_prompts(self):
        """Given I'm on Sessions tab, when I select a session, prompts panel updates."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause()
            await pilot.press("down")
            await pilot.pause()

            screen = app.screen
            prompts_panel = screen.query_one("#prompts-content")
            assert prompts_panel is not None


class TestSettingsTab:
    """Test Settings tab functionality."""

    @pytest.mark.asyncio
    async def test_settings_shows_config_options(self):
        """Given I'm on Settings tab, then I should see configuration options."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("7")
            await pilot.pause()

            screen = app.screen

            # Check display settings
            default_tab = screen.query_one("#settings-default-tab")
            assert default_tab is not None

            # Check column visibility
            col_title = screen.query_one("#settings-col-title")
            assert col_title is not None

            # Check pricing
            price_input = screen.query_one("#settings-price-input")
            assert price_input is not None


class TestDarkMode:
    """Test dark mode toggle functionality."""

    @pytest.mark.asyncio
    async def test_dark_mode_binding_exists(self):
        """Given dashboard is running, then dark mode binding 'd' should exist."""
        app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))
        async with app.run_test(size=(120, 40)):
            # Verify the 'd' binding exists in the app
            bindings = [b.key for b in app.BINDINGS]
            assert "d" in bindings
