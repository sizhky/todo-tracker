"""Main application for the Textual UI v2."""

from torch_snippets import AD
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree
from textual.binding import Binding, BindingType

from td.v2.cli.display import fetch


def add_children(item: str, subtree: AD, expand_children=False) -> None:
    for key, value in subtree.items():
        if isinstance(value, AD):
            child = item.add(key.split(" + ")[0])
            if expand_children:
                child.expand()
            add_children(child, value)
        elif value is None:
            child = item.add_leaf(key.split(" + ")[0])


class Todos(Tree):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("h", "collapse_and_cursor_parent", "Cursor to parent", show=True),
        Binding("H", "cursor_parent", "Cursor to parent", show=True),
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
        Binding("space", "toggle_node", "Toggle", show=False),
        Binding(
            "shift+space", "toggle_expand_all", "Expand or collapse all", show=False
        ),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]

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
        self.root.expand()
        add_children(self.root, todos)
        return self


class MainArea(Static):
    def compose(self) -> ComposeResult:
        yield Todos.from_AD(fetch(as_dataframe=False))


class TodoAppV2(App):
    CSS_PATH = "css/base.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]
    main_area = MainArea()

    def on_mount(self, event):
        self.theme = "dracula"

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
