from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer
from textual.binding import Binding

from .widgets.task_list import TaskList
from todo_tracker.tasks.manager import TaskManager


class TodoApp(App):
    """A Textual app to manage tasks."""

    task_manager = TaskManager()
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    TITLE = "Todo Tracker"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(TaskList(self.task_manager), id="main")
        yield Footer()

    def action_refresh(self) -> None:
        """Refresh the task list."""
        task_list = self.query_one(TaskList)
        task_list.action_refresh()
