"""
Entry point for the Textual UI v2.
"""

from .app import TodoAppV2


def main():
    """Run the Todo Tracker Textual UI v2."""
    app = TodoAppV2()
    app.run()


if __name__ == "__main__":
    main()
