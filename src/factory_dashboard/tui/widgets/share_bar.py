"""Share bar chart widget for showing distribution between groups."""

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.widget import Widget

# Color palette for groups
COLORS = ["cyan", "green", "yellow", "magenta", "blue", "red", "white"]


class ShareBar(Widget):
    """Horizontal bar chart showing share/distribution between groups."""

    DEFAULT_CSS = """
    ShareBar {
        height: auto;
        padding: 0 1;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        items: list[tuple[str, float, str]],
        title: str = "Share",
        bar_width: int = 25,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize ShareBar.

        Args:
            items: List of (name, value, formatted_value) tuples.
                   value is used for calculating percentages.
                   formatted_value is displayed (e.g., "124.0M", "$386.77").
            title: Panel title.
            bar_width: Width of the bar in characters.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.items = items
        self.bar_title = title
        self.bar_width = bar_width

    def render(self) -> RenderableType:
        total = sum(item[1] for item in self.items) or 1

        table = Table.grid(padding=(0, 1))
        table.add_column(width=12, justify="left")  # Name
        table.add_column(width=self.bar_width + 2)  # Bar
        table.add_column(width=7, justify="right")  # Percentage
        table.add_column(width=12, justify="right")  # Value

        for idx, (name, value, formatted_value) in enumerate(self.items):
            color = COLORS[idx % len(COLORS)]
            pct = (value / total) * 100
            bar_filled = int((value / total) * self.bar_width)
            bar = f"[{color}]{'█' * bar_filled}{'░' * (self.bar_width - bar_filled)}[/]"
            table.add_row(name, bar, f"{pct:.1f}%", formatted_value)

        return Panel(table, title=self.bar_title, border_style="blue")
