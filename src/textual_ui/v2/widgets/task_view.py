"""
Task View widget for displaying detailed task information.
"""

from textual.widgets import Static, Button, Input, Label
from textual.containers import Horizontal, Vertical
from textual import on, events

from td.v2.cli.display import fetch
from td.v2.cli.task import task_crud


class TaskView(Vertical):
    """A widget to display detailed information about a selected task."""

    DEFAULT_CSS = """
    TaskView {
        height: 100%;
        width: 100%;
        border: solid green;
        padding: 1;
    }
    
    #task-title {
        text-style: bold;
        content-align: center middle;
        height: 3;
        background: $boost;
        padding: 1;
    }
    
    #task-details {
        margin: 1 0;
        height: auto;
    }
    
    #task-actions {
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 1;
    }
    
    .detail-item {
        margin-bottom: 1;
    }
    
    .label {
        width: 30%;
        text-style: bold;
    }
    
    .value {
        width: 70%;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id = None
        self.task_data = None
        self.detail_widgets = {}  # Store widgets by field name

    def compose(self):
        """Create child widgets for the task view."""
        yield Static("No task selected", id="task-title")

        with Vertical(id="task-details"):
            yield Static("Select a task to view its details.", id="task-info-message")

        with Horizontal(id="task-actions"):
            yield Button("Toggle Status", id="toggle-button", disabled=True)
            yield Button("Edit Task", id="edit-button", disabled=True)
            yield Button("Delete Task", id="delete-button", disabled=True)

    def update_task(self, task_id):
        """Update the task view with the task details."""
        self.task_id = task_id

        if not task_id:
            self.update_empty_view()
            return

        # Fetch the task data
        task = task_crud.read(id=task_id)
        if not task:
            self.update_empty_view()
            return

        self.task_data = task

        # Update the title
        title_widget = self.query_one("#task-title", Static)
        status_icon = "✅" if task.is_done else "📝"
        title_widget.update(f"{status_icon} {task.title}")

        # Update the details container
        details_container = self.query_one("#task-details", Vertical)

        # Clear previous detail message if it exists
        try:
            message = self.query_one("#task-info-message", Static)
            message.remove()
        except Exception:
            pass

        # Update or create detail rows
        self._update_or_create_detail_row("ID", task.id)
        self._update_or_create_detail_row(
            "Status", "Complete" if task.is_done else "Incomplete"
        )

        if task.meta:
            self._update_or_create_detail_row("Metadata", str(task.meta))
        elif "Metadata" in self.detail_widgets:
            # Remove metadata row if it exists but task has no metadata
            self.detail_widgets["Metadata"]["container"].remove()
            del self.detail_widgets["Metadata"]

        # Enable action buttons
        self.query_one("#toggle-button", Button).disabled = False
        self.query_one("#edit-button", Button).disabled = False
        self.query_one("#delete-button", Button).disabled = False

    def update_empty_view(self):
        """Reset the view when no task is selected."""
        # Update the title
        title_widget = self.query_one("#task-title", Static)
        title_widget.update("No task selected")

        # Remove all detail rows
        for field_name, widgets in self.detail_widgets.items():
            if widgets["container"].parent:
                widgets["container"].remove()
        self.detail_widgets = {}

        # Update details container
        details_container = self.query_one("#task-details", Vertical)

        # Check if task-info-message exists
        try:
            message = self.query_one("#task-info-message", Static)
            message.update("Select a task to view its details.")
        except Exception:
            # If it doesn't exist, create it
            details_container.mount(
                Static("Select a task to view its details.", id="task-info-message")
            )

        # Disable action buttons
        self.query_one("#toggle-button", Button).disabled = True
        self.query_one("#edit-button", Button).disabled = True
        self.query_one("#delete-button", Button).disabled = True

    def _update_or_create_detail_row(self, label, value):
        """Update an existing detail row or create a new one."""
        details_container = self.query_one("#task-details", Vertical)

        if label in self.detail_widgets:
            # Update existing widgets
            self.detail_widgets[label]["value"].update(str(value))
        else:
            # Create new detail row
            container = Horizontal(classes="detail-item")
            label_widget = Static(f"{label}:", classes="label")
            value_widget = Static(str(value), classes="value")

            container.mount(label_widget)
            container.mount(value_widget)
            details_container.mount(container)

            # Store references to the widgets
            self.detail_widgets[label] = {
                "container": container,
                "label": label_widget,
                "value": value_widget,
            }

    def _add_detail_row(self, container, label, value):
        """Legacy method for backward compatibility."""
        self._update_or_create_detail_row(label, value)

    @on(Button.Pressed, "#toggle-button")
    def handle_toggle(self):
        """Handle the toggle button press."""
        if self.task_id:
            success = task_crud.toggle(id=self.task_id)
            if success and self.task_data:
                # Update the view
                self.update_task(self.task_id)
                # Inform the parent to refresh the tree
                self.post_message(TaskView.TaskToggled(self.task_id))

    @on(Button.Pressed, "#delete-button")
    def handle_delete(self):
        """Handle the delete button press."""
        if self.task_id:
            success = task_crud.delete(id=self.task_id)
            if success:
                # Reset the view
                self.update_empty_view()
                # Inform the parent to refresh the tree
                self.post_message(TaskView.TaskDeleted(self.task_id))

    class TaskToggled(events.Message):
        """Event sent when a task is toggled."""

        def __init__(self, task_id):
            super().__init__()
            self.task_id = task_id

    class TaskDeleted(events.Message):
        """Event sent when a task is deleted."""

        def __init__(self, task_id):
            super().__init__()
            self.task_id = task_id
