"""
Main application file for the Textual UI v2.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Select, Static
from textual.binding import Binding

from .widgets.task_tree import TaskTree
from .widgets.task_view import TaskView
from td.v2.cli.sector import _list_sectors


class TodoAppV2(App):
    """A Textual app to manage tasks using hierarchical data."""

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("t", "toggle_selected", "Toggle Task", show=True),
    ]

    CSS_PATH = "styles/app.tcss"
    TITLE = "Todo Tracker V2"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sectors = _list_sectors()
        self.current_sector = self.sectors[0] if self.sectors else None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        # Main layout container
        with Container(id="main"):
            # Top section with sector selector
            with Horizontal(id="top-section"):
                yield Static("Sector:", id="sector-label")
                sectors = [(sector, sector) for sector in self.sectors]
                yield Select(
                    options=sectors, id="sector-select", value=self.current_sector
                )

            # Task area with tree view and task details
            with Horizontal(id="task-area"):
                # Left panel with tree view
                with Vertical(id="left-panel"):
                    yield TaskTree(self.current_sector, id="task-tree")

                # Right panel with task details
                with Vertical(id="right-panel"):
                    yield TaskView(id="task-view")

        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle sector selection change."""
        self.current_sector = event.value
        task_tree = self.query_one(TaskTree)
        task_tree.sector = self.current_sector
        task_tree.refresh_data()

        # Reset the task view
        task_view = self.query_one(TaskView)
        task_view.update_empty_view()

    def action_refresh(self) -> None:
        """Refresh the task tree."""
        task_tree = self.query_one(TaskTree)
        task_tree.refresh_data()

        # Reset the task view
        task_view = self.query_one(TaskView)
        task_view.update_empty_view()

    def action_toggle_selected(self) -> None:
        """Toggle the selected task's status."""
        task_tree = self.query_one(TaskTree)
        task_tree.toggle_selected_task()

    def on_tree_node_selected(self, event) -> None:
        """Handle tree node selection."""
        task_tree = self.query_one(TaskTree)
        selected_node = event.node

        if selected_node in task_tree.task_node_map:
            task_id = task_tree.task_node_map[selected_node]
            if task_id:
                # Update the task view
                task_view = self.query_one(TaskView)
                task_view.update_task(task_id)

    def on_task_view_task_toggled(self, event) -> None:
        """Handle task toggled from the task view."""
        task_tree = self.query_one(TaskTree)
        task_tree.refresh_data()

    def on_task_view_task_deleted(self, event) -> None:
        """Handle task deleted from the task view."""
        task_tree = self.query_one(TaskTree)
        task_tree.refresh_data()
