"""Main Textual application for Factory Dashboard."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from rich.markup import escape
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from ..core import SessionAggregator, SessionParser
from ..core.config import Config, get_config_path_display, load_config, save_config
from ..core.cost import CostEstimator, format_cost
from ..core.models import DashboardStats, Session
from .widgets import ActivityHeatmap, ShareBar, StatsPanel, TokenBar
from .widgets.stats_panel import format_duration, format_tokens

SORT_OPTIONS = [
    ("Date (newest)", "date_desc"),
    ("Date (oldest)", "date_asc"),
    ("Tokens (highest)", "tokens_desc"),
    ("Tokens (lowest)", "tokens_asc"),
    ("Duration (longest)", "duration_desc"),
    ("Duration (shortest)", "duration_asc"),
]

GROUP_OPTIONS = [
    ("No grouping", "none"),
    ("By Project", "project"),
    ("By Group", "group"),
    ("By Model", "model"),
]


class EditTitleScreen(ModalScreen):
    """Modal screen for editing session title."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    CSS = """
    EditTitleScreen {
        align: center middle;
    }

    EditTitleScreen > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }

    EditTitleScreen Input {
        margin: 1 0;
    }

    EditTitleScreen .buttons {
        margin-top: 1;
        align: right middle;
        height: auto;
    }

    EditTitleScreen Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        session_id: str,
        current_title: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.session_id = session_id
        self.current_title = current_title

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("[bold]Edit Session Title[/]")
            yield Input(
                value=self.current_title,
                id="title-input",
                placeholder="Enter session title...",
            )
            with Horizontal(classes="buttons"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Save", variant="primary", id="save-btn")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "save-btn":
            new_title = self.query_one("#title-input", Input).value
            self.dismiss((self.session_id, new_title))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss((self.session_id, event.value))

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        new_title = self.query_one("#title-input", Input).value
        self.dismiss((self.session_id, new_title))


class ConnectSessionScreen(ModalScreen):
    """Modal dialog for confirming session connection."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "connect", "Connect"),
    ]

    CSS = """
    ConnectSessionScreen {
        align: center middle;
    }

    ConnectSessionScreen > Container {
        width: 70;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }

    ConnectSessionScreen .info-row {
        height: auto;
        margin: 0 0 1 0;
    }

    ConnectSessionScreen .info-label {
        width: 12;
        color: $text-muted;
    }

    ConnectSessionScreen .info-value {
        width: 1fr;
    }

    ConnectSessionScreen .warning {
        margin: 1 0;
        color: $warning;
    }

    ConnectSessionScreen .buttons {
        margin-top: 1;
        align: right middle;
        height: auto;
    }

    ConnectSessionScreen Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        session: Session,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.session = session

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("[bold]Connect to Session[/]")

            with Horizontal(classes="info-row"):
                yield Static("Title:", classes="info-label")
                yield Static(self.session.title[:50], classes="info-value")

            with Horizontal(classes="info-row"):
                yield Static("Project:", classes="info-label")
                yield Static(
                    self.session.cwd or self.session.project_name, classes="info-value"
                )

            with Horizontal(classes="info-row"):
                yield Static("Session ID:", classes="info-label")
                yield Static(self.session.id, classes="info-value")

            yield Static(
                "[dim]This will exit the dashboard and resume the session in Droid.[/]",
                classes="warning",
            )

            with Horizontal(classes="buttons"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Connect", variant="primary", id="connect-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "connect-btn":
            self.dismiss(self.session)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_connect(self) -> None:
        self.dismiss(self.session)


class DashboardScreen(Screen):
    """Main dashboard screen with overview statistics."""

    BINDINGS = [
        Binding("1", "switch_tab('overview')", "Overview", show=False),
        Binding("2", "switch_tab('groups')", "Groups", show=False),
        Binding("3", "switch_tab('projects')", "Projects", show=False),
        Binding("4", "switch_tab('sessions')", "Sessions", show=False),
        Binding("5", "switch_tab('favorites')", "Favorites", show=False),
        Binding("6", "switch_tab('settings')", "Settings", show=False),
        Binding("e", "edit_title", "Edit", show=True),
        Binding("f", "toggle_favorite", "Fav", show=True),
        Binding("c", "connect_session", "Connect", show=True),
        Binding("y", "copy_session_id", "Copy ID", show=True),
    ]

    sessions_sort = reactive("tokens_desc")
    sessions_group = reactive("project")
    sessions_hide_empty = reactive(True)

    # Projects table sorting
    projects_sort_column = reactive("tokens")
    projects_sort_reverse = reactive(True)

    def __init__(
        self,
        stats: DashboardStats,
        cost_estimator: CostEstimator,
        config: Config | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.stats = stats
        self.cost_estimator = cost_estimator
        self.config = config or Config()
        self._session_row_map: dict[int, Session] = {}
        self._favorites_row_map: dict[int, Session] = {}

        # Apply config defaults
        self.sessions_sort = self.config.display.default_sort
        self.sessions_group = self.config.display.default_group
        self.sessions_hide_empty = self.config.display.hide_empty_sessions

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to a specific tab."""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = tab_id

    def _is_session_tab_active(self) -> bool:
        """Check if Sessions or Favorites tab is currently active."""
        try:
            tabbed = self.query_one(TabbedContent)
            return tabbed.active in ("sessions", "favorites")
        except Exception:
            return False

    def check_action(self, action: str, parameters: tuple) -> bool | None:
        """Control which actions are available based on current tab."""
        session_actions = (
            "edit_title",
            "toggle_favorite",
            "connect_session",
            "copy_session_id",
        )
        if action in session_actions:
            return self._is_session_tab_active()
        return True

    def action_edit_title(self) -> None:
        """Edit the title of the selected session."""
        try:
            table = self.query_one("#sessions-table", DataTable)
            if table.cursor_row is None:
                return

            session = self._session_row_map.get(table.cursor_row)
            if not session:
                return

            self.app.push_screen(
                EditTitleScreen(session.id, session.title),
                self._handle_title_edit,
            )
        except Exception:
            pass

    def _handle_title_edit(self, result: tuple | None) -> None:
        """Handle the result from the edit title modal."""
        if result is None:
            return

        session_id, new_title = result
        if not new_title.strip():
            return

        app = self.app
        assert hasattr(app, "sessions_dir")  # FactoryDashboardApp attribute
        sessions_dir: str = app.sessions_dir  # type: ignore[attr-defined]
        parser = SessionParser(sessions_dir)
        if parser.update_session_title(session_id, new_title):
            for session in self.stats.sessions:
                if session.id == session_id:
                    session.title = new_title.strip()[:80]
                    break
            self._refresh_sessions_table()

    def action_toggle_favorite(self) -> None:
        """Toggle favorite status of the selected session."""
        session = None

        # Try sessions table first
        try:
            table = self.query_one("#sessions-table", DataTable)
            if table.cursor_row is not None:
                session = self._session_row_map.get(table.cursor_row)
        except Exception:
            pass

        # Try favorites table if no session found
        if not session:
            try:
                table = self.query_one("#favorites-table", DataTable)
                if table.cursor_row is not None:
                    session = self._favorites_row_map.get(table.cursor_row)
            except Exception:
                pass

        if not session:
            return

        app = self.app
        assert hasattr(app, "sessions_dir")  # FactoryDashboardApp attribute
        sessions_dir: str = app.sessions_dir  # type: ignore[attr-defined]
        parser = SessionParser(sessions_dir)
        new_status = parser.toggle_favorite(session.id)
        session.is_favorite = new_status
        self._refresh_sessions_table()
        self._refresh_favorites_table()

    def action_connect_session(self) -> None:
        """Connect to the selected session (exit dashboard and launch Droid)."""
        session = self._get_selected_session()
        if not session:
            return

        self.app.push_screen(
            ConnectSessionScreen(session),
            self._handle_connect,
        )

    def action_copy_session_id(self) -> None:
        """Copy the ID of the selected session to clipboard."""
        session = self._get_selected_session()
        if not session:
            return

        try:
            self.app.clipboard = session.id  # type: ignore[invalid-assignment]
            # Show a brief status message if possible
            # Since we don't have a shared status bar, we can use the prompts header temporarily
            header = self.query_one("#prompts-header", Static)
            original_text = "User Prompts"  # Default header text
            header.update("[green]ID Copied to Clipboard![/]")

            def restore_header():
                header.update(original_text)

            self.set_timer(2.0, restore_header)
        except Exception:
            pass

    def _get_selected_session(self) -> Session | None:
        """Get the currently selected session from either sessions or favorites table."""
        # Try sessions table first
        try:
            table = self.query_one("#sessions-table", DataTable)
            if table.cursor_row is not None:
                session = self._session_row_map.get(table.cursor_row)
                if session:
                    return session
        except Exception:
            pass

        # Try favorites table
        try:
            table = self.query_one("#favorites-table", DataTable)
            if table.cursor_row is not None:
                session = self._favorites_row_map.get(table.cursor_row)
                if session:
                    return session
        except Exception:
            pass

        return None

    def _handle_connect(self, result: Session | None) -> None:
        """Handle the result from the connect session modal."""
        if result is None:
            return

        # Exit the app and pass the session to connect to
        self.app.exit(result)

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            with TabPane("Overview", id="overview"):
                yield from self._compose_overview()
            with TabPane("Groups", id="groups"):
                yield from self._compose_groups()
            with TabPane("Projects", id="projects"):
                yield from self._compose_projects()
            with TabPane("Sessions", id="sessions"):
                yield from self._compose_sessions()
            with TabPane("Favorites", id="favorites"):
                yield from self._compose_favorites()
            with TabPane("Settings", id="settings"):
                yield from self._compose_settings()

        yield Footer()

    def _compose_overview(self) -> ComposeResult:
        with ScrollableContainer():
            total_cost = self.cost_estimator.estimate_total_cost(self.stats.sessions)

            date_range_str = "N/A"
            if self.stats.date_range[0] and self.stats.date_range[1]:
                date_range_str = f"{self.stats.date_range[0].strftime('%Y-%m-%d')} to {self.stats.date_range[1].strftime('%Y-%m-%d')}"

            aggregator = SessionAggregator(self.stats.sessions)
            daily_stats = aggregator.get_daily_stats()

            # Format peak day stats
            peak_token_str = "N/A"
            peak_time_str = "N/A"
            if daily_stats["peak_token_day"]:
                peak_date, peak_tokens = daily_stats["peak_token_day"]
                peak_token_str = f"{peak_date} ({format_tokens(peak_tokens)})"
            if daily_stats["peak_time_day"]:
                peak_date, peak_time = daily_stats["peak_time_day"]
                peak_time_str = f"{peak_date} ({format_duration(peak_time)})"

            with Horizontal(classes="stats-row"):
                yield StatsPanel(
                    "Summary",
                    {
                        "Total Sessions": self.stats.total_sessions,
                        "Total Projects": len(self.stats.projects),
                        "Project Groups": len(self.stats.project_groups),
                        "Active Time": format_duration(self.stats.total_active_time_ms),
                        "Est. Cost": format_cost(total_cost),
                        "Date Range": date_range_str,
                    },
                )
                yield TokenBar(self.stats.total_tokens, title="Token Distribution")

            # Get weekly and monthly stats
            weekly_stats = aggregator.get_weekly_stats()
            monthly_stats = aggregator.get_monthly_stats()

            # Format peak week
            peak_week_str = "N/A"
            if weekly_stats["peak_week"]:
                (year, week), tokens = weekly_stats["peak_week"]
                peak_week_str = f"{year}-W{week:02d} ({format_tokens(tokens)})"

            # Format peak month
            peak_month_str = "N/A"
            if monthly_stats["peak_month"]:
                (year, month), tokens = monthly_stats["peak_month"]
                peak_month_str = f"{year}-{month:02d} ({format_tokens(tokens)})"

            with Horizontal(classes="stats-row"):
                yield StatsPanel(
                    "Daily Usage",
                    {
                        "Median Daily Tokens": format_tokens(
                            daily_stats["median_daily_tokens"]
                        ),
                        "Median Daily Time": format_duration(
                            daily_stats["median_daily_time_ms"]
                        ),
                        "Peak Token Day": peak_token_str,
                        "Peak Time Day": peak_time_str,
                    },
                )
                yield StatsPanel(
                    "Weekly / Monthly",
                    {
                        "Avg Weekly Tokens": format_tokens(
                            weekly_stats["avg_weekly_tokens"]
                        ),
                        "Avg Monthly Tokens": format_tokens(
                            monthly_stats["avg_monthly_tokens"]
                        ),
                        "Peak Week": peak_week_str,
                        "Peak Month": peak_month_str,
                    },
                )

            activity = aggregator.get_activity_by_date()
            yield ActivityHeatmap(activity, weeks=20, title="Activity (Last 20 Weeks)")

            yield Static("[bold]Top Projects by Tokens[/]", classes="section-title")
            yield self._build_top_projects_table()

    def _compose_groups(self) -> ComposeResult:
        with ScrollableContainer():
            yield Static(
                "[bold cyan]Project Group Statistics[/]", classes="section-title"
            )

            table = DataTable()
            table.add_columns(
                "Group",
                "Projects",
                "Sessions",
                "Tokens",
                "Active Time",
                "Est. Cost",
                "Cache Hit",
            )

            sorted_groups = sorted(
                self.stats.project_groups,
                key=lambda g: g.total_tokens.total_tokens,
                reverse=True,
            )

            # Calculate group costs for table and charts
            group_data = []
            for group in sorted_groups:
                group_cost = sum(
                    self.cost_estimator.estimate_session_cost(s)
                    for p in group.projects
                    for s in p.sessions
                )
                group_data.append((group, group_cost))
                table.add_row(
                    group.name,
                    str(group.project_count),
                    str(group.session_count),
                    format_tokens(group.total_tokens.total_tokens),
                    format_duration(group.total_active_time_ms),
                    format_cost(group_cost),
                    f"{group.total_tokens.cache_hit_ratio:.1%}",
                )

            yield table

            # Share charts
            if group_data:
                # Tokens share
                token_items = [
                    (
                        g.name,
                        float(g.total_tokens.total_tokens),
                        format_tokens(g.total_tokens.total_tokens),
                    )
                    for g, _ in group_data
                ]
                yield ShareBar(token_items, title="Token Share by Group")

                # Cost share
                cost_items = [
                    (g.name, cost, format_cost(cost)) for g, cost in group_data
                ]
                yield ShareBar(cost_items, title="Cost Share by Group")

                # Active time share
                time_items = [
                    (
                        g.name,
                        float(g.total_active_time_ms),
                        format_duration(g.total_active_time_ms),
                    )
                    for g, _ in group_data
                ]
                yield ShareBar(time_items, title="Active Time Share by Group")

    def _compose_projects(self) -> ComposeResult:
        with ScrollableContainer():
            yield DataTable(id="projects-table")

    def _compose_sessions(self) -> ComposeResult:
        with Horizontal(classes="sessions-split-view"):
            with Vertical(classes="sessions-list-panel"):
                with Horizontal(classes="controls-row"):
                    yield Static("Sort: ", classes="control-label")
                    yield Select(
                        options=SORT_OPTIONS,
                        value="tokens_desc",
                        id="sort-select",
                        allow_blank=False,
                    )
                    yield Static("  Group: ", classes="control-label")
                    yield Select(
                        options=GROUP_OPTIONS,
                        value="project",
                        id="group-select",
                        allow_blank=False,
                    )
                    yield Static("  ", classes="control-label")
                    yield Checkbox(
                        "Hide empty sessions", value=True, id="hide-empty-checkbox"
                    )

                with ScrollableContainer(classes="sessions-table-container"):
                    yield DataTable(id="sessions-table", cursor_type="row")

            with Vertical(classes="prompts-panel", id="prompts-panel"):
                yield Static(
                    "[bold]Session Prompts[/]",
                    id="prompts-header",
                    classes="prompts-header",
                )
                yield Static(
                    "[dim]Select a session to view prompts[/]",
                    id="prompts-info",
                    classes="prompts-info",
                )
                with ScrollableContainer(
                    id="prompts-container", classes="prompts-container"
                ):
                    yield Static("", id="prompts-content", markup=False)

    def _compose_favorites(self) -> ComposeResult:
        """Compose the favorites tab showing only favorite sessions."""
        with Horizontal(classes="sessions-split-view"):
            with Vertical(classes="sessions-list-panel"):
                yield Static("[bold]Favorite Sessions[/]", classes="section-title")
                with ScrollableContainer(classes="sessions-table-container"):
                    yield DataTable(id="favorites-table", cursor_type="row")

            with Vertical(classes="prompts-panel", id="favorites-prompts-panel"):
                yield Static(
                    "[bold]Session Prompts[/]",
                    id="favorites-prompts-header",
                    classes="prompts-header",
                )
                yield Static(
                    "[dim]Select a session to view prompts[/]",
                    id="favorites-prompts-info",
                    classes="prompts-info",
                )
                with ScrollableContainer(
                    id="favorites-prompts-container", classes="prompts-container"
                ):
                    yield Static("", id="favorites-prompts-content", markup=False)

    def _compose_settings(self) -> ComposeResult:
        """Compose the settings tab."""
        with ScrollableContainer():
            yield Static("[bold]Configuration[/]", classes="section-title")
            yield Static(
                f"[dim]Config file: {get_config_path_display()}[/]",
                classes="config-path",
            )

            # Display Settings
            yield Static("\n[bold]Display Defaults[/]", classes="settings-section")
            with Horizontal(classes="settings-row"):
                yield Label("Default Tab:")
                yield Select(
                    [
                        ("Overview", "overview"),
                        ("Groups", "groups"),
                        ("Projects", "projects"),
                        ("Sessions", "sessions"),
                        ("Favorites", "favorites"),
                    ],
                    value=self.config.display.default_tab,
                    id="settings-default-tab",
                )
            with Horizontal(classes="settings-row"):
                yield Label("Default Sort:")
                yield Select(
                    SORT_OPTIONS,
                    value=self.config.display.default_sort,
                    id="settings-default-sort",
                )
            with Horizontal(classes="settings-row"):
                yield Label("Default Group:")
                yield Select(
                    GROUP_OPTIONS,
                    value=self.config.display.default_group,
                    id="settings-default-group",
                )
            with Horizontal(classes="settings-row"):
                yield Checkbox(
                    "Hide Empty Sessions",
                    self.config.display.hide_empty_sessions,
                    id="settings-hide-empty",
                )
            with Horizontal(classes="settings-row"):
                yield Checkbox(
                    "Dark Mode", self.config.display.dark_mode, id="settings-dark-mode"
                )
            with Horizontal(classes="settings-row"):
                yield Label("Heatmap Weeks:")
                yield Input(
                    str(self.config.display.heatmap_weeks),
                    id="settings-heatmap-weeks",
                    type="integer",
                )

            # Column Visibility
            yield Static("\n[bold]Session Table Columns[/]", classes="settings-section")
            with Horizontal(classes="settings-row"):
                yield Checkbox(
                    "Title", self.config.columns.show_title, id="settings-col-title"
                )
                yield Checkbox(
                    "Date", self.config.columns.show_date, id="settings-col-date"
                )
                yield Checkbox(
                    "Project",
                    self.config.columns.show_project,
                    id="settings-col-project",
                )
                yield Checkbox(
                    "Model", self.config.columns.show_model, id="settings-col-model"
                )
            with Horizontal(classes="settings-row"):
                yield Checkbox(
                    "Tokens", self.config.columns.show_tokens, id="settings-col-tokens"
                )
                yield Checkbox(
                    "Favorites",
                    self.config.columns.show_favorites,
                    id="settings-col-favorites",
                )
                yield Checkbox(
                    "Prompts",
                    self.config.columns.show_prompts,
                    id="settings-col-prompts",
                )
                yield Checkbox(
                    "Duration",
                    self.config.columns.show_duration,
                    id="settings-col-duration",
                )

            # Pricing
            yield Static(
                "\n[bold]Default Pricing (per million tokens)[/]",
                classes="settings-section",
            )
            with Horizontal(classes="settings-row"):
                yield Label("Input:")
                yield Input(
                    str(self.config.default_pricing.input_per_million),
                    id="settings-price-input",
                    type="number",
                )
                yield Label("Output:")
                yield Input(
                    str(self.config.default_pricing.output_per_million),
                    id="settings-price-output",
                    type="number",
                )
            with Horizontal(classes="settings-row"):
                yield Label("Cache Write:")
                yield Input(
                    str(self.config.default_pricing.cache_write_per_million),
                    id="settings-price-cache-write",
                    type="number",
                )
                yield Label("Cache Read:")
                yield Input(
                    str(self.config.default_pricing.cache_read_per_million),
                    id="settings-price-cache-read",
                    type="number",
                )

            # Paths
            yield Static("\n[bold]Paths[/]", classes="settings-section")
            with Horizontal(classes="settings-row"):
                yield Label("Sessions Directory:")
                yield Input(self.config.paths.sessions_dir, id="settings-sessions-dir")

            # Save Button
            yield Static("")
            with Horizontal(classes="settings-row"):
                yield Button(
                    "Save Configuration", id="save-settings", variant="primary"
                )
                yield Static("", id="settings-status")

    def on_mount(self) -> None:
        self._refresh_projects_table()
        self._refresh_sessions_table()
        self._refresh_favorites_table()

    def _refresh_projects_table(self) -> None:
        """Refresh the projects table with current sort settings."""
        try:
            table = self.query_one("#projects-table", DataTable)
        except Exception:
            return

        table.clear(columns=True)

        # Column definitions: (label, sort_key)
        columns = [
            ("Project", "project"),
            ("Group", "group"),
            ("Sessions", "sessions"),
            ("Tokens", "tokens"),
            ("Active Time", "active_time"),
            ("Est. Cost", "cost"),
        ]

        # Add columns with sort indicator
        for label, sort_key in columns:
            if sort_key == self.projects_sort_column:
                arrow = "▼" if self.projects_sort_reverse else "▲"
                header = Text(f"{label} {arrow}", style="bold cyan")
            else:
                header = Text(label)
            table.add_column(header, key=sort_key)

        # Calculate costs for sorting
        project_costs = {
            p.name: sum(
                self.cost_estimator.estimate_session_cost(s) for s in p.sessions
            )
            for p in self.stats.projects
        }

        # Sort projects
        sort_keys = {
            "project": lambda p: p.name.lower(),
            "group": lambda p: p.group.lower(),
            "sessions": lambda p: p.session_count,
            "tokens": lambda p: p.total_tokens.total_tokens,
            "active_time": lambda p: p.total_active_time_ms,
            "cost": lambda p: project_costs.get(p.name, 0),
        }

        sort_fn = sort_keys.get(self.projects_sort_column, sort_keys["tokens"])
        sorted_projects = sorted(
            self.stats.projects, key=sort_fn, reverse=self.projects_sort_reverse
        )

        for project in sorted_projects:
            table.add_row(
                project.name,
                project.group,
                str(project.session_count),
                format_tokens(project.total_tokens.total_tokens),
                format_duration(project.total_active_time_ms),
                format_cost(project_costs[project.name]),
            )

    def _refresh_favorites_table(self) -> None:
        """Refresh the favorites table."""
        try:
            table = self.query_one("#favorites-table", DataTable)
        except Exception:
            return

        table.clear(columns=True)
        table.add_columns(
            "Title", "Date", "Project", "Model", "Tokens", "Prompts", "Duration"
        )

        favorite_sessions = [s for s in self.stats.sessions if s.is_favorite]
        sorted_sessions = sorted(
            favorite_sessions, key=lambda s: s.tokens.total_tokens, reverse=True
        )

        self._favorites_row_map: dict[int, Session] = {}
        for row_idx, session in enumerate(sorted_sessions):
            date_str = (
                session.timestamp.strftime("%Y-%m-%d %H:%M")
                if session.timestamp
                else "N/A"
            )
            title = Text(session.title[:50], style="bold yellow")
            title.justify = "right"
            table.add_row(
                title,
                date_str,
                session.project_name,
                self._short_model(session.model),
                format_tokens(session.tokens.total_tokens),
                str(session.user_prompt_count),
                format_duration(session.active_time_ms),
            )
            self._favorites_row_map[row_idx] = session

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "sort-select":
            self.sessions_sort = event.value  # type: ignore[invalid-assignment]
            self._refresh_sessions_table()
        elif event.select.id == "group-select":
            self.sessions_group = event.value  # type: ignore[invalid-assignment]
            self._refresh_sessions_table()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "hide-empty-checkbox":
            self.sessions_hide_empty = event.value
            self._refresh_sessions_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-settings":
            self._save_settings()

    def _save_settings(self) -> None:
        """Save current settings from form to config file."""
        try:
            # Collect values from form
            # Display settings
            default_tab_select = self.query_one("#settings-default-tab", Select)
            default_sort_select = self.query_one("#settings-default-sort", Select)
            default_group_select = self.query_one("#settings-default-group", Select)
            hide_empty_cb = self.query_one("#settings-hide-empty", Checkbox)
            dark_mode_cb = self.query_one("#settings-dark-mode", Checkbox)
            heatmap_weeks_input = self.query_one("#settings-heatmap-weeks", Input)

            self.config.display.default_tab = str(default_tab_select.value)
            self.config.display.default_sort = str(default_sort_select.value)
            self.config.display.default_group = str(default_group_select.value)
            self.config.display.hide_empty_sessions = hide_empty_cb.value
            self.config.display.dark_mode = dark_mode_cb.value
            self.config.display.heatmap_weeks = int(heatmap_weeks_input.value or 20)

            # Column settings
            self.config.columns.show_title = self.query_one(
                "#settings-col-title", Checkbox
            ).value
            self.config.columns.show_date = self.query_one(
                "#settings-col-date", Checkbox
            ).value
            self.config.columns.show_project = self.query_one(
                "#settings-col-project", Checkbox
            ).value
            self.config.columns.show_model = self.query_one(
                "#settings-col-model", Checkbox
            ).value
            self.config.columns.show_tokens = self.query_one(
                "#settings-col-tokens", Checkbox
            ).value
            self.config.columns.show_favorites = self.query_one(
                "#settings-col-favorites", Checkbox
            ).value
            self.config.columns.show_prompts = self.query_one(
                "#settings-col-prompts", Checkbox
            ).value
            self.config.columns.show_duration = self.query_one(
                "#settings-col-duration", Checkbox
            ).value

            # Pricing settings
            self.config.default_pricing.input_per_million = float(
                self.query_one("#settings-price-input", Input).value or 3.0
            )
            self.config.default_pricing.output_per_million = float(
                self.query_one("#settings-price-output", Input).value or 15.0
            )
            self.config.default_pricing.cache_write_per_million = float(
                self.query_one("#settings-price-cache-write", Input).value or 3.75
            )
            self.config.default_pricing.cache_read_per_million = float(
                self.query_one("#settings-price-cache-read", Input).value or 0.30
            )

            # Paths
            self.config.paths.sessions_dir = self.query_one(
                "#settings-sessions-dir", Input
            ).value

            # Save to file
            if save_config(self.config):
                status = self.query_one("#settings-status", Static)
                status.update("[green]Configuration saved successfully![/]")
            else:
                status = self.query_one("#settings-status", Static)
                status.update("[red]Failed to save configuration[/]")
        except Exception as e:
            status = self.query_one("#settings-status", Static)
            status.update(f"[red]Error: {escape(str(e))}[/]")

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header click for sorting."""
        if event.data_table.id == "projects-table":
            column_key = event.column_key.value
            if column_key == self.projects_sort_column:
                self.projects_sort_reverse = not self.projects_sort_reverse
            else:
                self.projects_sort_column = column_key  # type: ignore[invalid-assignment]
                self.projects_sort_reverse = True
            self._refresh_projects_table()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row selection in sessions or favorites table to show prompts."""
        table_id = event.data_table.id
        if table_id not in ("sessions-table", "favorites-table"):
            return

        row_key = event.row_key
        if row_key is None:
            return

        try:
            row_idx = event.cursor_row
            if table_id == "sessions-table":
                session = self._session_row_map.get(row_idx)
                if session:
                    self._update_prompts_panel(session)
            elif table_id == "favorites-table":
                session = self._favorites_row_map.get(row_idx)
                if session:
                    self._update_favorites_prompts_panel(session)
        except Exception:
            pass

    def _update_favorites_prompts_panel(self, session: Session) -> None:
        """Update the favorites prompts panel with the selected session's prompts."""
        try:
            header = self.query_one("#favorites-prompts-header", Static)
            info = self.query_one("#favorites-prompts-info", Static)
            content = self.query_one("#favorites-prompts-content", Static)
        except Exception:
            return

        header.update(f"[bold]{escape(session.title[:40])}[/]")

        app = self.app
        assert hasattr(app, "sessions_dir")  # FactoryDashboardApp attribute
        sessions_dir: str = app.sessions_dir  # type: ignore[attr-defined]
        parser = SessionParser(sessions_dir)
        prompts = parser.get_session_prompts(session.id)

        if not prompts:
            info.update(
                f"[dim]{escape(session.project_name)} | {session.user_prompt_count} prompts | No content available[/]"
            )
            content.update("")
            return

        date_str = (
            session.timestamp.strftime("%Y-%m-%d %H:%M") if session.timestamp else "N/A"
        )
        info.update(
            f"[dim]{escape(session.project_name)} | {date_str} | {len(prompts)} prompts[/]"
        )

        lines = []
        for prompt in prompts:
            ts = prompt.timestamp.strftime("%H:%M") if prompt.timestamp else "??:??"
            lines.append(f"#{prompt.index} {ts} ({prompt.char_count} chars)")
            lines.append("-" * 40)
            text = prompt.text[:500]
            if len(prompt.text) > 500:
                text += "..."
            lines.append(text)
            lines.append("")

        content.update("\n".join(lines))

    def _update_prompts_panel(self, session: Session) -> None:
        """Update the prompts panel with the selected session's prompts."""
        try:
            header = self.query_one("#prompts-header", Static)
            info = self.query_one("#prompts-info", Static)
            content = self.query_one("#prompts-content", Static)
        except Exception:
            return

        # Update header - escape title to prevent markup errors
        header.update(f"[bold]{escape(session.title[:40])}[/]")

        # Get prompts
        app = self.app
        assert hasattr(app, "sessions_dir")  # FactoryDashboardApp attribute
        sessions_dir: str = app.sessions_dir  # type: ignore[attr-defined]
        parser = SessionParser(sessions_dir)
        prompts = parser.get_session_prompts(session.id)

        if not prompts:
            info.update(
                f"[dim]{escape(session.project_name)} | {session.user_prompt_count} prompts | No content available[/]"
            )
            content.update("")
            return

        # Update info
        date_str = (
            session.timestamp.strftime("%Y-%m-%d %H:%M") if session.timestamp else "N/A"
        )
        info.update(
            f"[dim]{escape(session.project_name)} | {date_str} | {len(prompts)} prompts[/]"
        )

        # Build prompts content - no markup since Static has markup=False
        lines = []
        for prompt in prompts:
            ts = prompt.timestamp.strftime("%H:%M") if prompt.timestamp else "??:??"
            lines.append(f"#{prompt.index} {ts} ({prompt.char_count} chars)")
            lines.append("-" * 40)
            text = prompt.text[:500]
            if len(prompt.text) > 500:
                text += "..."
            lines.append(text)
            lines.append("")

        content.update("\n".join(lines))

    def _sort_sessions(self, sessions: list[Session]) -> list[Session]:
        """Sort sessions based on current sort setting."""
        sort_key = self.sessions_sort

        if sort_key == "date_desc":
            return sorted(
                sessions,
                key=lambda s: s.timestamp or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
        elif sort_key == "date_asc":
            return sorted(
                sessions,
                key=lambda s: s.timestamp or datetime.min.replace(tzinfo=timezone.utc),
            )
        elif sort_key == "tokens_desc":
            return sorted(sessions, key=lambda s: s.tokens.total_tokens, reverse=True)
        elif sort_key == "tokens_asc":
            return sorted(sessions, key=lambda s: s.tokens.total_tokens)
        elif sort_key == "duration_desc":
            return sorted(sessions, key=lambda s: s.active_time_ms, reverse=True)
        elif sort_key == "duration_asc":
            return sorted(sessions, key=lambda s: s.active_time_ms)
        return sessions

    def _is_empty_session(self, session: Session) -> bool:
        """Check if session is empty (new session with no activity)."""
        if session.title in ("New Session", "Untitled Session"):
            return True
        return session.user_prompt_count == 0

    def _filter_sessions(self, sessions: list[Session]) -> list[Session]:
        """Filter sessions based on current filter settings."""
        if self.sessions_hide_empty:
            return [s for s in sessions if not self._is_empty_session(s)]
        return sessions

    def _refresh_sessions_table(self) -> None:
        """Refresh the sessions table with current sort and group settings."""
        try:
            table = self.query_one("#sessions-table", DataTable)
        except Exception:
            return

        table.clear(columns=True)
        self._session_row_map.clear()

        group_by = self.sessions_group
        sessions = self._filter_sessions(self.stats.sessions)
        row_idx = 0

        if group_by == "none":
            table.add_columns(
                "Title",
                "Date",
                "Project",
                "Model",
                "Tokens",
                "★",
                "Prompts",
                "Duration",
            )
            sorted_sessions = self._sort_sessions(sessions)
            for session in sorted_sessions[:100]:
                date_str = (
                    session.timestamp.strftime("%Y-%m-%d %H:%M")
                    if session.timestamp
                    else "N/A"
                )
                fav = "★" if session.is_favorite else ""
                title_text = session.title[:50]
                title = Text(
                    title_text, style="bold yellow" if session.is_favorite else ""
                )
                title.justify = "right"
                table.add_row(
                    title,
                    date_str,
                    session.project_name,
                    self._short_model(session.model),
                    format_tokens(session.tokens.total_tokens),
                    fav,
                    str(session.user_prompt_count),
                    format_duration(session.active_time_ms),
                )
                self._session_row_map[row_idx] = session
                row_idx += 1
        else:
            table.add_columns(
                "Title", "", "Date", "Model", "Tokens", "★", "Prompts", "Duration"
            )
            grouped = self._group_sessions(sessions, group_by)

            for group_name, group_sessions in grouped.items():
                total_tokens = sum(s.tokens.total_tokens for s in group_sessions)
                total_prompts = sum(s.user_prompt_count for s in group_sessions)
                total_duration = sum(s.active_time_ms for s in group_sessions)
                table.add_row(
                    "",
                    f"[bold cyan]{group_name}[/]",
                    f"[dim]{len(group_sessions)} sessions[/]",
                    "",
                    f"[bold]{format_tokens(total_tokens)}[/]",
                    "",
                    f"[bold]{total_prompts}[/]",
                    f"[bold]{format_duration(total_duration)}[/]",
                )
                row_idx += 1  # Group header row (not editable)

                sorted_group = self._sort_sessions(group_sessions)
                for session in sorted_group[:20]:
                    date_str = (
                        session.timestamp.strftime("%Y-%m-%d %H:%M")
                        if session.timestamp
                        else "N/A"
                    )
                    fav = "★" if session.is_favorite else ""
                    title_text = session.title[:40]
                    title = Text(
                        title_text, style="bold yellow" if session.is_favorite else ""
                    )
                    title.justify = "right"
                    table.add_row(
                        title,
                        "  ",
                        date_str,
                        self._short_model(session.model),
                        format_tokens(session.tokens.total_tokens),
                        fav,
                        str(session.user_prompt_count),
                        format_duration(session.active_time_ms),
                    )
                    self._session_row_map[row_idx] = session
                    row_idx += 1
                if len(sorted_group) > 20:
                    table.add_row(
                        "",
                        "",
                        f"[dim]... and {len(sorted_group) - 20} more[/]",
                        "",
                        "",
                        "",
                        "",
                        "",
                    )
                    row_idx += 1

    def _group_sessions(self, sessions: list[Session], group_by: str) -> dict:
        """Group sessions by the specified field."""
        grouped = defaultdict(list)
        for session in sessions:
            if group_by == "project":
                key = session.project_name
            elif group_by == "group":
                key = session.project_group
            elif group_by == "model":
                key = self._short_model(session.model)
            else:
                key = "All"
            grouped[key].append(session)

        return dict(
            sorted(
                grouped.items(),
                key=lambda x: sum(s.tokens.total_tokens for s in x[1]),
                reverse=True,
            )
        )

    def _short_model(self, model: str) -> str:
        """Get shortened model name."""
        if "opus" in model.lower():
            return "Opus"
        elif "sonnet" in model.lower():
            return "Sonnet"
        elif "haiku" in model.lower():
            return "Haiku"
        return model.split("-")[1] if "-" in model else model

    def _build_top_projects_table(self) -> DataTable:
        table = DataTable()
        table.add_columns("Project", "Group", "Sessions", "Tokens", "Cost")

        top_projects = sorted(
            self.stats.projects,
            key=lambda p: p.total_tokens.total_tokens,
            reverse=True,
        )[:10]

        for project in top_projects:
            cost = sum(
                self.cost_estimator.estimate_session_cost(s) for s in project.sessions
            )
            table.add_row(
                project.name,
                project.group,
                str(project.session_count),
                format_tokens(project.total_tokens.total_tokens),
                format_cost(cost),
            )

        return table


class FactoryDashboardApp(App):
    """Factory Dashboard TUI Application."""

    CSS = """
    Screen {
        background: $surface;
    }

    .stats-row {
        height: auto;
        margin: 1 0;
    }

    .stats-row > StatsPanel {
        width: 1fr;
        margin-right: 1;
    }

    .stats-row > TokenBar {
        width: 2fr;
    }

    .section-title {
        margin: 1 0;
        padding: 0 1;
    }

    .group-container {
        margin: 1 0;
        height: auto;
    }

    DataTable {
        height: auto;
        max-height: 30;
        margin: 1 0;
    }

    #sessions-table {
        max-height: 40;
    }

    ActivityHeatmap {
        margin: 1 0;
    }

    ScrollableContainer {
        padding: 0 1;
    }

    .controls-row {
        height: auto;
        margin: 1 0;
        padding: 0 1;
        align: left middle;
    }

    .controls-row > Static {
        width: auto;
        padding: 0 1;
    }

    .controls-row Select {
        width: 25;
    }

    .control-label {
        padding-top: 1;
    }

    TabPane {
        height: 1fr;
    }

    .sessions-split-view {
        height: 1fr;
        min-height: 20;
    }

    .sessions-list-panel {
        width: 2fr;
        height: 1fr;
    }

    .sessions-table-container {
        height: 1fr;
        min-height: 10;
    }

    #sessions-table {
        height: auto;
        min-height: 10;
    }

    .prompts-panel {
        width: 1fr;
        height: 1fr;
        border-left: solid $primary;
        padding: 0 1;
    }

    .prompts-header {
        height: auto;
        padding: 1;
        background: $primary-background;
    }

    .prompts-info {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
    }

    .prompts-container {
        height: 1fr;
    }

    #prompts-content {
        padding: 0 1;
    }

    .settings-section {
        margin: 1 0 0 0;
    }

    .settings-row {
        height: auto;
        margin: 0 0 1 0;
        padding: 0 1;
        align: left middle;
    }

    .settings-row Label {
        width: auto;
        min-width: 15;
        padding-right: 1;
    }

    .settings-row Select {
        width: 25;
    }

    .settings-row Input {
        width: 20;
        margin-right: 2;
    }

    .settings-row Checkbox {
        margin-right: 2;
    }

    .config-path {
        margin: 0 1 1 1;
    }

    #save-settings {
        margin-right: 2;
    }

    #settings-status {
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "toggle_dark", "Dark Mode"),
    ]

    TITLE = "Factory Dashboard"
    SUB_TITLE = "Session Analytics"

    def __init__(self, sessions_dir: str | None = None, config: Config | None = None):
        super().__init__()
        self.config = config or load_config()
        self.sessions_dir = sessions_dir or self.config.get_sessions_dir()
        self.parser: SessionParser | None = None
        self.stats: DashboardStats | None = None
        self.cost_estimator = CostEstimator.from_config(self.config)

    def on_mount(self) -> None:
        if self.config.display.dark_mode:
            self.dark = True
        else:
            self.dark = False
        self._load_data()

    def _load_data(self) -> None:
        self.parser = SessionParser(self.sessions_dir)
        sessions = self.parser.parse_all_sessions()
        aggregator = SessionAggregator(sessions)
        self.stats = aggregator.get_dashboard_stats()
        self.push_screen(DashboardScreen(self.stats, self.cost_estimator, self.config))

    def action_refresh(self) -> None:
        self.pop_screen()
        self._load_data()
