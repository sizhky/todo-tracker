from todo_tracker.tasks import TaskManager
from todo_tracker.tasks.models import TaskStatus
from textual.widgets import DataTable
from textual import on
import rich

class TaskList(DataTable):
    """A widget to display tasks in a table format."""

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("ctrl+k", "toggle_selected", "Toggle Status"),
        ("d", "debug_info", "Debug Info"),  # New binding for debugging
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
        self.task_row_map = {}
        self.debug_mode = True

    def on_mount(self) -> None:
        """Set up the table when the widget is mounted."""
        super().on_mount()
        
        # Add columns with fixed widths
        self.add_column("ID", width=12)
        self.add_column("Task", width=40)
        self.add_column("Status", width=35)
        self.populate_tasks()
        
    def populate_tasks(self):
        """Load tasks into the table and update the task_row_map."""
        self.task_row_map = {}
        tasks = self.task_manager.list_tasks()
        
        # Clear existing rows
        self.clear()
        
        # Add tasks and build the mapping
        for i, task in enumerate(tasks):
            if task.status == TaskStatus.COMPLETED:
                continue
            self.add_row(task.id, task.title, task.status)
            self.task_row_map[i] = task.id

    def action_refresh(self) -> None:
        """Refresh the task list."""
        self.populate_tasks()
        
    @on(DataTable.CellSelected)
    def on_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle cell selection events to toggle task status."""
        if self.debug_mode:
            self.debug_event("CellSelected", event)
            
        # Get the row index from the event
        row_index = event.coordinate.row
        if row_index is not None and row_index in self.task_row_map:
            task_id = self.task_row_map[row_index]
            self.toggle_task_status(task_id)
    
    @on(DataTable.CellHighlighted)
    def on_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Debug handler for cell highlight events."""
        if self.debug_mode:
            self.debug_event("CellHighlighted", event)
    
    def debug_event(self, event_name, event):
        """Print debug information for an event."""
        debug_info = f"EVENT: {event_name}\n"
        debug_info += f"  - coordinate: {event.coordinate}\n"
        debug_info += f"  - row_index: {event.coordinate.row}\n"
        debug_info += f"  - column_index: {event.coordinate.column}\n"
        debug_info += f"  - task_row_map: {self.task_row_map}\n"
        
        # For CellSelected specifically, show more details
        if hasattr(event, 'value'):
            debug_info += f"  - value: {event.value}\n"
        
        # Print to the console (will show in terminal)
        rich.print(debug_info)
        
        # Also show as a notification in the UI
        self.notify(f"Debug: {event_name} at {event.coordinate}")
    
    def action_debug_info(self) -> None:
        """Show current debug information."""
        debug_info = f"Current cursor: {self.cursor_coordinate}\n"
        debug_info += f"Task map: {self.task_row_map}\n"
        debug_info += f"Debug mode: {self.debug_mode}"
        self.notify(debug_info)
        rich.print(debug_info)
    
    def toggle_task_status(self, task_id: int) -> None:
        """Toggle the status of a task between pending and completed."""
        task = self.task_manager.get_task(task_id)
        if task:
            # Toggle between completed and pending
            new_status = (
                TaskStatus.PENDING if task.status == TaskStatus.COMPLETED 
                else TaskStatus.COMPLETED
            )
            self.task_manager.update_task(task_id, status=new_status)
            
            # Show notification that task was updated
            self.notify(f"Task {task_id} status changed to {new_status.value}")
            
            # Refresh the list
            self.action_refresh()
            
    def action_toggle_selected(self) -> None:
        """Toggle the status of the currently selected task (spacebar shortcut)."""
        row_index = self.cursor_coordinate.row
        if row_index is not None and row_index in self.task_row_map:
            task_id = self.task_row_map[row_index]
            self.toggle_task_status(task_id)