#!/usr/bin/env python3
"""Take screenshots of each tab for README documentation."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from droid_dash.tui.app import FactoryDashboardApp

SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
TEST_SESSIONS_DIR = Path(__file__).parent.parent / "test_sessions"


async def take_screenshots():
    """Take screenshots of each tab."""
    app = FactoryDashboardApp(sessions_dir=str(TEST_SESSIONS_DIR))

    async with app.run_test(size=(120, 40)) as pilot:
        # Wait for app to load
        await pilot.pause()

        # Screenshot 1: Overview tab (default)
        await pilot.press("1")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "overview.svg"))
        print("Saved overview.svg")

        # Screenshot 2: Groups tab
        await pilot.press("2")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "groups.svg"))
        print("Saved groups.svg")

        # Screenshot 3: Projects tab
        await pilot.press("3")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "projects.svg"))
        print("Saved projects.svg")

        # Screenshot 4: Sessions tab
        await pilot.press("4")
        await pilot.pause()
        # Select first row to show prompts panel
        await pilot.press("down")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "sessions.svg"))
        print("Saved sessions.svg")

        # Screenshot 5: Favorites tab
        await pilot.press("5")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "favorites.svg"))
        print("Saved favorites.svg")

        # Screenshot 6: Settings tab
        await pilot.press("6")
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "settings.svg"))
        print("Saved settings.svg")

        # Screenshot 7: Light mode (toggle dark mode)
        await pilot.press("1")  # Back to overview
        await pilot.pause()
        await pilot.press("d")  # Toggle dark mode
        await pilot.pause()
        app.save_screenshot(str(SCREENSHOTS_DIR / "overview-light.svg"))
        print("Saved overview-light.svg")


if __name__ == "__main__":
    asyncio.run(take_screenshots())
