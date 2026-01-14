"""GitHub-style activity heatmap widget."""

from datetime import date, timedelta

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget


class ActivityHeatmap(Widget):
    """GitHub-style activity heatmap showing session activity by day."""

    DEFAULT_CSS = """
    ActivityHeatmap {
        height: auto;
        padding: 0 1;
    }
    """

    INTENSITY_CHARS = " ░▒▓█"
    INTENSITY_COLORS = [
        "grey23",
        "dark_green",
        "green",
        "bright_green",
        "green1",
    ]

    def __init__(
        self,
        activity: dict,
        weeks: int = 20,
        title: str = "Activity",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.activity = activity
        self.weeks = weeks
        self.heatmap_title = title

    def render(self) -> RenderableType:
        today = date.today()
        start_date = today - timedelta(days=self.weeks * 7)
        start_date = start_date - timedelta(days=start_date.weekday())

        if self.activity:
            max_count = max(len(sessions) for sessions in self.activity.values())
        else:
            max_count = 1

        month_labels = self._get_month_labels(start_date, today)
        day_labels = ["M", " ", "W", " ", "F", " ", "S"]

        lines = []
        lines.append(self._build_month_row(month_labels))

        for dow in range(7):
            line = Text()
            line.append(f"{day_labels[dow]} ", style="dim")

            current = start_date + timedelta(days=dow)
            while current <= today:
                sessions = self.activity.get(current, [])
                intensity = self._get_intensity(len(sessions), max_count)
                char = self.INTENSITY_CHARS[intensity]
                color = self.INTENSITY_COLORS[intensity]
                line.append(char, style=color)
                current += timedelta(days=7)

            lines.append(line)

        legend = self._build_legend()
        lines.append(Text())
        lines.append(legend)

        content = Text("\n").join(lines)
        return Panel(content, title=self.heatmap_title, border_style="blue")

    def _get_intensity(self, count: int, max_count: int) -> int:
        if count == 0:
            return 0
        if max_count <= 1:
            return 4 if count > 0 else 0
        ratio = count / max_count
        if ratio <= 0.25:
            return 1
        elif ratio <= 0.50:
            return 2
        elif ratio <= 0.75:
            return 3
        return 4

    def _get_month_labels(self, start: date, end: date) -> list[tuple[int, str]]:
        """Get month labels with their week positions."""
        labels = []
        current = start
        week = 0
        last_month = None

        while current <= end:
            if current.month != last_month:
                month_name = current.strftime("%b")
                labels.append((week, month_name))
                last_month = current.month
            current += timedelta(days=7)
            week += 1

        return labels

    def _build_month_row(self, labels: list[tuple[int, str]]) -> Text:
        row = Text("  ")
        last_pos = 0
        for pos, label in labels:
            spaces = pos - last_pos
            row.append(" " * spaces)
            row.append(label[:3], style="dim")
            last_pos = pos + 3
        return row

    def _build_legend(self) -> Text:
        legend = Text("  Less ", style="dim")
        for i in range(5):
            legend.append(self.INTENSITY_CHARS[i], style=self.INTENSITY_COLORS[i])
        legend.append(" More", style="dim")
        return legend
