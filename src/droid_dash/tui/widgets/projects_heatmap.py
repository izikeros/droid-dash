"""Projects heatmap widget showing token usage per project over time."""

from __future__ import annotations

from datetime import date, timedelta

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget


class ProjectsHeatmap(Widget):
    """Heatmap showing daily token usage per project."""

    DEFAULT_CSS = """
    ProjectsHeatmap {
        height: auto;
        padding: 0 1;
    }
    """

    INTENSITY_CHARS = " ░▒▓█"
    INTENSITY_COLORS = [
        "grey23",
        "dark_cyan",
        "cyan",
        "bright_cyan",
        "cyan1",
    ]

    def __init__(
        self,
        data: dict[str, dict[date, int]],
        days: int = 60,
        max_projects: int = 15,
        title: str = "Projects Heatmap",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize ProjectsHeatmap.

        Args:
            data: Dict mapping project_name -> {date -> tokens}.
            days: Number of days to display.
            max_projects: Maximum number of projects to show.
            title: Panel title.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.data = data
        self.days = days
        self.max_projects = max_projects
        self.heatmap_title = title

    def render(self) -> RenderableType:
        today = date.today()
        start_date = today - timedelta(days=self.days - 1)

        # Get date range
        dates = [start_date + timedelta(days=i) for i in range(self.days)]

        # Sort projects by total tokens descending
        project_totals = {
            proj: sum(daily.values())
            for proj, daily in self.data.items()
        }
        sorted_projects = sorted(
            project_totals.keys(),
            key=lambda p: project_totals[p],
            reverse=True,
        )[:self.max_projects]

        if not sorted_projects:
            return Panel(
                Text("No project data available", style="dim"),
                title=self.heatmap_title,
                border_style="blue",
            )

        # Find global max for intensity scaling
        global_max = 1
        for proj in sorted_projects:
            for d in dates:
                tokens = self.data.get(proj, {}).get(d, 0)
                if tokens > global_max:
                    global_max = tokens

        # Calculate project name column width
        name_width = 12

        # Build header row with month labels
        lines = []
        header = self._build_month_row(dates, name_width)
        lines.append(header)

        # Build row for each project
        for proj in sorted_projects:
            line = Text()
            # Truncate/pad project name
            display_name = proj[:name_width].ljust(name_width)
            line.append(display_name + " ", style="bold")

            # Add cell for each day
            proj_data = self.data.get(proj, {})
            for d in dates:
                tokens = proj_data.get(d, 0)
                intensity = self._get_intensity(tokens, global_max)
                char = self.INTENSITY_CHARS[intensity]
                color = self.INTENSITY_COLORS[intensity]
                line.append(char, style=color)

            lines.append(line)

        # Add legend
        lines.append(Text())
        lines.append(self._build_legend(name_width))

        content = Text("\n").join(lines)
        return Panel(content, title=self.heatmap_title, border_style="blue")

    def _get_intensity(self, tokens: int, max_tokens: int) -> int:
        """Map token count to intensity level (0-4)."""
        if tokens == 0:
            return 0
        if max_tokens <= 0:
            return 4 if tokens > 0 else 0
        ratio = tokens / max_tokens
        if ratio <= 0.25:
            return 1
        elif ratio <= 0.50:
            return 2
        elif ratio <= 0.75:
            return 3
        return 4

    def _build_month_row(self, dates: list[date], name_width: int) -> Text:
        """Build header row with month labels."""
        row = Text(" " * (name_width + 1))
        last_month = None

        for d in dates:
            if d.month != last_month:
                month_abbr = d.strftime("%b")
                row.append(month_abbr[0], style="dim bold")
                last_month = d.month
            else:
                row.append(" ", style="dim")

        return row

    def _build_legend(self, name_width: int) -> Text:
        """Build legend row."""
        legend = Text(" " * name_width + " Less ", style="dim")
        for i in range(5):
            legend.append(self.INTENSITY_CHARS[i], style=self.INTENSITY_COLORS[i])
        legend.append(" More", style="dim")
        return legend
