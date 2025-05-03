"""Entry point for the Todo Tracker application."""
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Button

class Thing(App):
    def compose(self):
        yield "Hello"
        yield Button("Task 2")
        yield Button("Task 3")

def main():
    app = Thing()
    app.run()

if __name__ == "__main__":
    main()
