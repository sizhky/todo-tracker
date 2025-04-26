from todo_tracker.tasks import TaskManager
from textual.widgets import DataTable

class TaskList(DataTable):
    """A widget to display tasks in a table format."""

    BINDINGS = [
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, task_manager: TaskManager, *args, **kwargs):
        super().__init__(
            show_header=True,
            show_row_labels=True,
            cursor_type="row",
            *args,
            **kwargs
        )
        self.task_manager = task_manager

    def on_mount(self) -> None:
        """Set up the table when the widget is mounted."""
        super().on_mount()
        
        # Add columns with fixed widths
        self.add_column("ID", width=12)
        self.add_column("Task", width=40)
        self.add_column("Status", width=35)
        self.populate_tasks()
        
    def populate_tasks(self):
        tasks = self.task_manager.list_tasks()
        tasks = [
            (t.id, t.title, t.status)
            for t in tasks
        ]
        self.add_rows(tasks)

    def action_refresh(self) -> None:
        """Refresh the task list."""
        self.clear()
        self.populate_tasks()