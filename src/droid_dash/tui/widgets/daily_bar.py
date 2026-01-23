"""Vertical bar chart widget for daily data visualization."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget


class DailyBarChart(Widget):
    """Vertical bar chart showing daily values over time."""

    DEFAULT_CSS = """
    DailyBarChart {
        height: auto;
        padding: 0 1;
        margin: 1 0;
    }
    """

    BAR_CHARS = " ▁▂▃▄▅▆▇█"

    def __init__(
        self,
        data: dict[date, int],
        title: str = "Daily Activity",
        days: int = 30,
        bar_color: str = "cyan",
        value_formatter: Callable[[int], str] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize DailyBarChart.

        Args:
            data: Dictionary mapping dates to values.
            title: Chart title.
            days: Number of days to display.
            bar_color: Color for the bars.
            value_formatter: Optional function to format values for display.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.data = data
        self.chart_title = title
        self.days = days
        self.bar_color = bar_color
        self.value_formatter = value_formatter or self._default_formatter

    def _default_formatter(self, value: int) -> str:
        """Default value formatter."""
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return str(value)

    def render(self) -> RenderableType:
        today = date.today()
        start_date = today - timedelta(days=self.days - 1)

        # Collect values for the date range
        values = []
        dates = []
        for i in range(self.days):
            d = start_date + timedelta(days=i)
            dates.append(d)
            values.append(self.data.get(d, 0))

        max_value = max(values) if values and max(values) > 0 else 1

        # Build the bar chart (single row of varying height characters)
        bar_line = Text()
        for value in values:
            if value == 0:
                char_idx = 0
            else:
                # Map value to character index (1-8)
                ratio = value / max_value
                char_idx = min(int(ratio * 8) + 1, 8)
            bar_line.append(self.BAR_CHARS[char_idx], style=self.bar_color)

        # Build x-axis with month labels
        x_axis = self._build_x_axis(dates)

        # Build summary line
        total = sum(values)
        avg = total // len(values) if values else 0
        peak_idx = values.index(max(values)) if values else 0
        peak_date = dates[peak_idx] if dates else today

        summary = Text()
        summary.append("Total: ", style="dim")
        summary.append(self.value_formatter(total), style="bold")
        summary.append("  Avg: ", style="dim")
        summary.append(self.value_formatter(avg))
        summary.append("  Peak: ", style="dim")
        summary.append(f"{peak_date.strftime('%b %d')} ({self.value_formatter(max(values))})")

        lines = [bar_line, x_axis, Text(), summary]
        content = Text("\n").join(lines)

        return Panel(content, title=self.chart_title, border_style="blue")

    def _build_x_axis(self, dates: list[date]) -> Text:
        """Build x-axis with month labels at month boundaries."""
        axis = Text()
        last_month = None

        for i, d in enumerate(dates):
            if d.month != last_month:
                # Start of new month - show abbreviated month name
                month_abbr = d.strftime("%b")
                if i + len(month_abbr) <= len(dates):
                    axis.append(month_abbr[0], style="dim bold")
                    last_month = d.month
                else:
                    axis.append(" ", style="dim")
                    last_month = d.month
            else:
                axis.append("·", style="grey37")

        return axis
