"""Entry point for the Todo Tracker application."""

from src.textual_ui.app import TodoApp


def main():
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
