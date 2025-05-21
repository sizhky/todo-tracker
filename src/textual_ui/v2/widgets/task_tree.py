"""
Task Tree widget for displaying hierarchical tasks.
"""

from textual.widgets import Tree
from textual.widgets.tree import TreeNode
from textual import on, events

from td.v2.cli.display import fetch
from td.v2.cli.task import task_crud


class TaskTree(Tree):
    """A tree widget to display hierarchical tasks."""

    def __init__(self, sector=None, *args, **kwargs):
        # Default label for the tree
        label = kwargs.pop("label", "Tasks")
        super().__init__(label, *args, **kwargs)
        self.sector = sector
        self.task_node_map = {}  # Maps tree nodes to task IDs

    def on_mount(self) -> None:
        """Set up the tree when the widget is mounted."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh the task data."""
        self.clear()
        self.task_node_map = {}

        if not self.sector:
            self.root.label = "No sector selected"
            return

        # Set the root node label
        self.root.label = f"{self.sector.capitalize()} Tasks"
        self.root.expand()

        # Get the task data as a hierarchical dataframe
        df = fetch(sector=self.sector)

        # If the dataframe is empty, show a message
        if df.empty:
            empty_node = self.root.add("No tasks found")
            return

        # Process the dataframe hierarchically
        self._build_tree_from_dataframe(df)

    def _build_tree_from_dataframe(self, df):
        """Build a tree from a hierarchical dataframe."""
        # Group by the index levels
        if isinstance(df.index, str):
            # Handle the case when sector filtering returns a series
            task_name = df["TASK"] if "TASK" in df else str(df)
            task_id = self._extract_id_from_task_name(task_name)
            node = self.root.add(task_name)
            self.task_node_map[node] = task_id
            return

        if df.index.nlevels == 1:
            # Only tasks are present (no hierarchical structure)
            for task_idx in df.index:
                task_name = df.loc[task_idx, "TASK"]
                task_id = self._extract_id_from_task_name(task_name)
                node = self.root.add(f"📝 {task_name}")
                self.task_node_map[node] = task_id
        else:
            # Get all unique values at the first level of the index
            top_level_groups = df.index.get_level_values(0).unique()

            # For each group, create a node and process its children
            for group in top_level_groups:
                group_df = df.xs(group, level=0)
                group_node = self.root.add(f"📁 {group}")
                group_node.expand()

                # Process children recursively
                self._process_group(group_node, group_df)

    def _process_group(self, parent_node, df):
        """Process a group (area, project, etc.) and its children."""
        if df.index.nlevels == 1:
            # These are leaf nodes (tasks)
            for idx in df.index:
                task_name = df.loc[idx, "TASK"]
                task_id = self._extract_id_from_task_name(task_name)
                node = parent_node.add(f"📝 {task_name}")
                self.task_node_map[node] = task_id
        else:
            # These are intermediate nodes (areas, projects, sections)
            level_icon = "📂" if df.index.nlevels > 2 else "📋"
            groups = df.index.get_level_values(0).unique()
            for group in groups:
                group_df = df.xs(group, level=0)
                group_node = parent_node.add(f"{level_icon} {group}")
                group_node.expand()
                self._process_group(group_node, group_df)

    def _extract_id_from_task_name(self, task_name):
        """Extract the task ID from the task name if it contains an ID."""
        if not isinstance(task_name, str):
            return None

        # The fetch function includes task IDs in the format "name + id"
        parts = task_name.split(" + ")
        if len(parts) > 1:
            return parts[1]
        return None

    def toggle_selected_task(self):
        """Toggle the status of the selected task."""
        selected_node = self.cursor_node
        if selected_node in self.task_node_map:
            task_id = self.task_node_map[selected_node]
            if task_id:
                # Toggle the task's status
                success = task_crud.toggle(id=task_id)

                # Update the task label to show the change
                if success:
                    label = selected_node.label
                    if "✅" in label:
                        new_label = label.replace("✅", "📝")
                    else:
                        new_label = label.replace("📝", "✅")
                    selected_node.label = new_label

                # Refresh the tree
                self.refresh_data()
                # Toggle the task status
                task_crud.toggle_status(task_id)
                self.refresh_data()
                self.notify("Task status toggled", severity="information")
        else:
            self.notify(
                "No task selected or this item is not a task", severity="warning"
            )

    @on(Tree.NodeSelected)
    def handle_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection event."""
        # You can add additional behavior when a node is selected
        pass
