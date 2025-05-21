"""Main application for the Textual UI v2."""

from torch_snippets import AD

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree

from td.v2.cli.display import fetch


def add_children(item: str, subtree: AD) -> None:
    for key, value in subtree.items():
        if isinstance(value, AD):
            child = item.add(key.split(" + ")[0])
            add_children(child, value)
        elif value is None:
            child = item.add_leaf(key.split(" + ")[0])


class Todos(Tree):
    def __init__(self, title: str):
        super().__init__(title)

    @classmethod
    def from_AD(cls, todos: AD):
        self = cls("Todos")
        self.root.expand()
        for sector in todos:
            if "tracker" not in sector:
                continue
            _sector = self.root.add(sector)
            add_children(_sector, todos[sector])
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


if __name__ == "__main__":
    app = TodoAppV2()
    app.run()
