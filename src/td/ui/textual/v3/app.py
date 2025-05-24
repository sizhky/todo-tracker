"""Main application for the Textual UI v2."""

from torch_snippets import AD, tryy
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree
from textual.widgets._tree import TreeNode
from textual.binding import Binding, BindingType
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, TextArea
from textual.screen import ModalScreen

from td.v3 import NodeCrud, NodeStatus, NodeCreate, NodeType


def infer_node_text(key, value) -> str:
    if value.status == NodeStatus.completed:
        key = f"{key} ✓"
    elif key.startswith("*"):
        key = f"{key} ✱"
    # else:
    #     return key

    # Gradient-based color assignment from purple to teal for hierarchy levels
    gradient_colors = ["#e40303", "#ff8c00", "#ffed00", "#008026", "#004dff", "#750787"]

    type_to_index = {
        NodeType.sector: 0,
        NodeType.area: 1,
        NodeType.project: 2,
        NodeType.section: 3,
        NodeType.task: 4,
        NodeType.subtask: 5,
    }

    color = gradient_colors[type_to_index.get(value.type, 0)]
    return f"[{color}]{key}[/]"


def add_children(item: TreeNode, subtree: AD, expand_children=False) -> None:
    for key, value in subtree.items():
        if key == "__node":
            continue
        if isinstance(value, AD):
            _value = value.get("__node")
            # __node = subtree.get("__node")
            child = item.add(infer_node_text(key, _value), data=_value)
            # child = item.add(f'{key} + {str(__node.id)[:8]}', data=__node)
            if expand_children:
                child.expand()
            add_children(child, value)
        else:
            child = item.add_leaf(infer_node_text(key, value), data=value)


class AddTaskPopup(ModalScreen):
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            placeholder = str(self.placeholder)
            yield TextArea(placeholder, id="show_path")
            yield Input(placeholder="", id="task_input")
            with Horizontal(classes="task-buttons"):
                yield Button("Add / Enter", id="add_button", variant="success")
                yield Button("Cancel / Escape", id="cancel_button", variant="error")

    def on_mount(self):
        self.query_one("#task_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        task_input = self.query_one("#task_input", Input).value
        self.dismiss(task_input if event.button.id == "add_button" else None)

    def action_submit(self):
        self.on_button_pressed(Button.Pressed(self.query_one("#add_button", Button)))

    def action_cancel(self):
        self.on_button_pressed(Button.Pressed(self.query_one("#cancel_button", Button)))


class Todos(Tree):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("h", "collapse_and_cursor_parent", "🐍 Cursor to Parent", show=False),
        Binding("H", "cursor_parent", "🐍 Cursor to Parent", show=False),
        Binding(
            "l", "expand_and_move_down", "🐍 Expand and Move to First Child", show=False
        ),
        Binding("L", "cursor_down", "🐍 Move down", show=False),
        Binding(
            "K",
            "cursor_previous_sibling",
            "🐍 Cursor to previous sibling",
            show=False,
        ),
        Binding(
            "J",
            "cursor_next_sibling",
            "🐍 Cursor to next sibling",
            show=False,
        ),
        Binding("tab", "toggle_node", "🐍 Toggle", show=False),
        Binding("k", "cursor_up", "🐍 Cursor Up", show=False),
        Binding("j", "cursor_down", "🐍 Cursor Down", show=False),
        Binding("0", "cursor_top", "🐍 Cursor to Top of Page", show=False),
        Binding("G", "cursor_page_bottom", "🐍 Cursor to Bottom of Page", show=False),
        Binding("x", "toggle_critical", "🐍 Mark as Critical", show=False),
        Binding(
            "shift+tab",
            "recursive_toggle_all",
            "🐍 Expand/Collapse All Children Recursively",
            show=False,
        ),
        Binding("z", "mark_complete", "🐍 Mark a task as complete", show=False),
        Binding("n", "add_new_task", "🐍 Add New Task", show=False),
        Binding("<", "promote_node", "🐍 Promote Node", show=False),
        Binding("m", "action_move_node", "🐍 Move Node", show=False),
    ]
    crud = NodeCrud()

    def action_move_node(self) -> None:
        node = self.cursor_node.data
        if node.id == "root":
            return
        self.crud._update_node(node)

    def action_promote_node(self) -> None:
        node = self.cursor_node.data
        if node.id == "root":
            return
        self.crud.promote_node(node)

    async def action_add_new_task(self) -> None:
        node = self.cursor_node.data
        if node.type == NodeType.subtask:
            # pop up saying "Cannot add task under a subtask"
            self.app.notify("Cannot add task under a subtask", title="Error")
            return
        path = f"{node.path}/{node.title}"

        @tryy
        def _write(task_text):
            if "/" in task_text:
                _path = path + "/" + "/".join(task_text.strip("/").split("/")[:-1])
                task_text = task_text.strip("/").split("/")[-1]
            else:
                _path = path
            _ = self.crud._create_node(
                NodeCreate(
                    title=task_text,
                    path=_path,
                )
            )

        popup = AddTaskPopup()
        _path_parts = path.strip("/").split("/")
        from torch_snippets import writelines

        writelines([_path_parts, path, node], "/tmp/tmp.txt", "w")
        _path = {}

        if _path_parts == [""]:
            _path = "root node"
            eg = (
                "sector for a new sector\n"
                "sector/area for a new area\n"
                "sector/area/project for a new project\n"
                "sector/area/project/section for a new section\n"
                "sector/area/project/section/task for a new task\n"
                "sector/area/project/section/task/subtask for a new subtask"
            )
            items = "sector, area, project, section and task"
        elif len(_path_parts) > 0:
            _path["sector"] = _path_parts[0]
            eg = (
                "area for a new area\n"
                "area/project for a new project\n"
                "area/project/section for a new section\n"
                "area/project/section/task for a new task\n"
                "area/project/section/task/subtask for a new subtask"
            )
            items = "area, project, section and task"
        if len(_path_parts) > 1:
            _path["area"] = _path_parts[1]
            eg = (
                "project for a new project\n"
                "project/section for a new section\n"
                "project/section/task for a new task\n"
                "project/section/task/subtask for a new subtask"
            )
            items = "project, section and task"
        if len(_path_parts) > 2:
            _path["project"] = _path_parts[2]
            eg = (
                "section for a new section\n"
                "section/task for a new task\n"
                "section/task/subtask for a new subtask"
            )
            items = "section and task"
        if len(_path_parts) > 3:
            _path["section"] = _path_parts[3]
            eg = "task for a new task\ntask/subtask for a new subtask"
            items = "task"
        if len(_path_parts) > 4:
            _path["task"] = _path_parts[4]
            eg = "task/subtask for a new subtask"

        popup.placeholder = (
            f"Add item under {_path}\n"
            f"(Use / to auto create intermediate {items})\n"
            f"E.g.,\n{eg}\n"
        )
        await self.app.push_screen(popup, _write)

    def action_mark_complete(self) -> None:
        node = self.cursor_node
        self.crud.toggle_complete(node.data)

    def action_recursive_toggle_all(self) -> None:
        node = self.cursor_node
        if not node or not node.allow_expand:
            return

        def toggle_recursively(n: TreeNode, expand: bool) -> None:
            if expand:
                n.expand()
            else:
                n.collapse()
            for child in n.children:
                toggle_recursively(child, expand)

        expand = not node.is_expanded
        toggle_recursively(node, expand)

    def action_toggle_critical(self) -> None:
        node = self.cursor_node
        self.crud.toggle_critical(node.data)

    def action_cursor_page_bottom(self) -> None:
        node = self.cursor_node
        self.action_cursor_down()
        new_node = self.cursor_node
        while new_node != node:
            node = new_node
            self.action_cursor_down()
            new_node = self.cursor_node

    def action_cursor_top(self) -> None:
        for _ in range(10):
            self.action_cursor_parent()

    def action_expand_and_move_down(self) -> None:
        node = self.cursor_node
        if node and not node.is_expanded and node.allow_expand:
            self.action_toggle_node()
            self.action_cursor_down()
        elif node and node.is_expanded and node.allow_expand:
            self.action_cursor_down()

    def action_collapse_and_cursor_parent(self) -> None:
        node = self.cursor_node
        self.action_cursor_parent()
        node = self.cursor_node
        if node and node.parent and node.is_expanded:
            self.action_toggle_node()

    def __init__(self, title: str):
        super().__init__(title)

    @classmethod
    def from_AD(cls, todos: AD):
        self = cls("Todos")
        self.root.data = AD(id="root", path="", title="", type="root")
        self.root.expand()
        add_children(self.root, todos)
        return self


class MainArea(Static):
    def compose(self) -> ComposeResult:
        n = NodeCrud()
        self._tree = Todos.from_AD(n.tree)
        yield self._tree

    def update_data(self, new_data):
        expanded_labels = self._collect_expanded_labels(self._tree.root)
        self._tree.clear()
        add_children(self._tree.root, new_data)
        self._restore_expanded_state(self._tree.root, expanded_labels)

    def _collect_expanded_labels(self, node):
        expanded = set()
        if (
            node.allow_expand
            and node.is_expanded
            and node.data
            and hasattr(node.data, "id")
        ):
            expanded.add(str(node.data.id))
        for child in node.children:
            expanded.update(self._collect_expanded_labels(child))
        return expanded

    def _restore_expanded_state(self, node, expanded_labels):
        if (
            node.allow_expand
            and node.data
            and hasattr(node.data, "id")
            and str(node.data.id) in expanded_labels
        ):
            node.expand()
        for child in node.children:
            self._restore_expanded_state(child, expanded_labels)


class TodoAppV2(App):
    CSS_PATH = "css/base.tcss"
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]
    main_area = MainArea()
    n = NodeCrud()

    async def on_mount(self) -> None:
        self.theme = "dracula"
        self.set_interval(1.0, self.refresh_data)

    async def on_ready(self) -> None:
        self.action_show_help_panel()

    async def refresh_data(self) -> None:
        new_data = self.n.tree
        self.main_area.update_data(new_data)

    def action_toggle_dark(self) -> None:
        if self.theme == "dracula":
            self.theme = "textual-light"
        else:
            self.theme = "dracula"

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.main_area
        yield Footer()


# Entry point for the textual UI v2 app
def main():
    TodoAppV2().run()


if __name__ == "__main__":
    main()
