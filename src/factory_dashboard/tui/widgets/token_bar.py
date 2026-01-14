"""Token usage bar chart widget."""

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.widget import Widget

from ...core.models import TokenUsage


class TokenBar(Widget):
    """Horizontal bar chart for token usage breakdown."""

    DEFAULT_CSS = """
    TokenBar {
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        tokens: TokenUsage,
        title: str = "Token Usage",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.tokens = tokens
        self.bar_title = title

    def render(self) -> RenderableType:
        total = self.tokens.total_tokens or 1

        table = Table.grid(padding=(0, 1))
        table.add_column(width=15, justify="left")
        table.add_column(width=12, justify="right")
        table.add_column(width=30)
        table.add_column(width=8, justify="right")

        categories = [
            ("Input", self.tokens.input_tokens, "cyan"),
            ("Output", self.tokens.output_tokens, "green"),
            ("Cache Write", self.tokens.cache_creation_tokens, "yellow"),
            ("Cache Read", self.tokens.cache_read_tokens, "magenta"),
            ("Thinking", self.tokens.thinking_tokens, "blue"),
        ]

        for name, count, color in categories:
            if count > 0:
                pct = (count / total) * 100
                bar_width = int((count / total) * 25)
                bar = f"[{color}]{'█' * bar_width}{'░' * (25 - bar_width)}[/]"
                count_str = self._format_count(count)
                table.add_row(name, count_str, bar, f"{pct:.1f}%")

        return Panel(table, title=self.bar_title, border_style="blue")

    def _format_count(self, count: int) -> str:
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)
