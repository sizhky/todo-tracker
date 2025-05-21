"""Main application for the Textual UI v2."""

from torch_snippets import AD
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree
from textual.widgets._tree import TreeNode
from textual.binding import Binding, BindingType

from td.v2.cli.display import fetch
from td.v2.cli import CRUDS, NodeStatus


def infer_node_text(key, value) -> str:
    if value.status == NodeStatus.completed:
        return f"[green]{key}[/]"
    elif key.startswith("*"):
        return f"[blue]{key.strip('*')}[/]"
    else:
        return key


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


class Todos(Tree):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("h", "collapse_and_cursor_parent", "Cursor to parent", show=False),
        Binding("H", "cursor_parent", "Cursor to parent", show=False),
        Binding("l", "expand_and_move_down", "Expand and move down", show=False),
        Binding("L", "cursor_down", "Move down", show=False),
        Binding(
            "K",
            "cursor_previous_sibling",
            "Cursor to previous sibling",
            show=False,
        ),
        Binding(
            "J",
            "cursor_next_sibling",
            "Cursor to next sibling",
            show=False,
        ),
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("tab", "toggle_node", "Toggle", show=False),
        Binding(
            "shift+space", "toggle_expand_all", "Expand or collapse all", show=False
        ),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("0", "cursor_top", "Cursor to top", show=False),
        Binding("G", "cursor_page_bottom", "Cursor to Bottom of Page", show=False),
        Binding("x", "toggle_critical", "Mark as Critical", show=False),
        Binding("shift+tab", "recursive_toggle_all", "Expand/Collapse All", show=False),
        Binding("z", "mark_complete", "Expand/Collapse All", show=False),
    ]

    def action_mark_complete(self) -> None:
        node = self.cursor_node
        crud = CRUDS.get(node.data.type).crud
        from torch_snippets import writelines

        writelines([str(node)], "/tmp/critical.txt", "w")
        crud.toggle_complete(node.data)

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
        crud = CRUDS.get(node.data.type).crud
        crud.toggle_critical(node.data)

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
        self.root.data = AD(id="root")
        self.root.expand()
        add_children(self.root, todos)
        return self


class MainArea(Static):
    def compose(self) -> ComposeResult:
        self._tree = Todos.from_AD(fetch(as_dataframe=False))
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
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]
    main_area = MainArea()

    async def on_mount(self) -> None:
        self.theme = "dracula"
        self.set_interval(1.0, self.refresh_data)

    async def refresh_data(self) -> None:
        new_data = fetch(as_dataframe=False)
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
