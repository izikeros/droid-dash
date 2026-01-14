---
name: textual-tui-development
description: Build Textual-based TUI applications with reactive patterns, DataTable widgets, modal dialogs, tabbed interfaces, and custom widgets. Use when implementing terminal user interfaces in Python.
---

# Textual TUI Development

## When to Use

- Building terminal user interfaces with Python
- Creating dashboards, data explorers, or interactive CLI tools
- Implementing reactive UI patterns with live updates
- Working with DataTable, tabs, modals, or custom widgets

## Instructions

### 1. App Structure

```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, DataTable, TabbedContent, TabPane

class MyApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Dark mode"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield TabbedContent(...)
        yield Footer()
```

### 2. Reactive Patterns

Use reactive variables to trigger UI updates:

```python
from textual.reactive import reactive

class MyScreen(Screen):
    selected_item: reactive[str | None] = reactive(None)
    
    def watch_selected_item(self, value: str | None) -> None:
        self._update_details_panel()
```

### 3. DataTable Best Practices

```python
table = DataTable(cursor_type="row")  # Required for row selection
table.add_columns("Name", "Value", "Status")
table.add_row("item1", "100", "active", key="row_1")

def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    row_key = event.row_key.value
```

### 4. Modal Dialogs

```python
class ConfirmDialog(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Are you sure?"),
            Button("Yes", id="yes", variant="primary"),
            Button("No", id="no"),
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
```

### 5. CSS Styling

```python
CSS = """
#my-container { height: 1fr; }  /* Use 1fr instead of 100% */
DataTable { height: 1fr; }
"""
```

## Common Pitfalls

1. **Row selection not working**: Add `cursor_type="row"` to DataTable
2. **Height issues**: Use `height: 1fr` instead of `height: 100%`
3. **Markup errors**: Use `markup=False` when displaying user content
4. **Widget queries**: Use `self.screen.query_one()` in screen context

## Verification

- Run `pytest tests/test_tui/` for TUI tests
- Use `pytest-textual-snapshot` for visual regression tests
