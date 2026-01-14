"""Stats panel widget for displaying summary statistics."""

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.widget import Widget


class StatsPanel(Widget):
    """A panel displaying key statistics."""

    DEFAULT_CSS = """
    StatsPanel {
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        title: str,
        stats: dict[str, str | int | float],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.panel_title = title
        self.stats = stats

    def render(self) -> RenderableType:
        table = Table.grid(padding=(0, 2))
        table.add_column(justify="left", style="bold cyan")
        table.add_column(justify="right", style="green")

        for key, value in self.stats.items():
            if isinstance(value, float):
                value = f"{value:.2f}"
            table.add_row(key, str(value))

        return Panel(table, title=self.panel_title, border_style="blue")


def format_tokens(count: int) -> str:
    """Format token count with K/M suffix."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_duration(ms: int) -> str:
    """Format duration in human-readable form."""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
