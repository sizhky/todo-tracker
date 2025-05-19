from torch_snippets import AD

from .__pre_init__ import cli
from .sector import sector_crud

from ..models.nodes import NodeRead


def fetch(id=None, as_dataframe=True):
    """
    Test command to check if the CLI is working.
    """
    o = AD()
    sectors = sector_crud.crud._read_all()
    ids = [s.id for s in sectors] if id is None else [id]

    def build_tree(node_id):
        node = sector_crud.crud._read(NodeRead(id=node_id))
        title = f"{node.title} + {str(node.id)[:8]}"
        children = sector_crud.crud.get_children(NodeRead(id=node_id))
        if not children:
            return title, None
        subtree = AD()
        for child in children:
            child_title, child_tree = build_tree(child.id)
            subtree[child_title] = child_tree
        return title, subtree

    for node_id in ids:
        title, tree = build_tree(node_id)
        o[title] = tree
    if as_dataframe:
        return o
        o = o.flatten_and_make_dataframe()
        o.fillna("_", inplace=True)
        o.columns = ["SECTOR", "AREA", "PROJECT", "SECTION", "TASK", "_"]
        o.set_index(["SECTOR", "AREA", "PROJECT", "SECTION"], inplace=True)
        return o
    return o


@cli.command("tw")
def watch_tasks():
    print(fetch())
    return
    import time
    from datetime import datetime

    try:
        # Hide cursor for cleaner display
        print("\033[?25l", end="", flush=True)

        # Save the initial position
        print("\033[s", end="", flush=True)

        # Get initial task data and measure its height
        initial_tasks = str(fetch())
        line_count = len(initial_tasks.split("\n")) + 2  # +2 for header lines

        first_run = True

        while True:
            if first_run:
                first_run = False
            else:
                # Return to saved position
                print("\033[u", end="", flush=True)

            # Get updated tasks
            tasks_data = str(fetch())

            # Display timestamp and tasks
            now = datetime.now().strftime("%H:%M:%S")
            print(f"Tasks as of {now} (Press Ctrl+C to exit)")
            print(tasks_data)

            # Clear any remaining lines from previous output
            for _ in range(line_count):
                # Move down a line and clear to the end of the line
                print("\n\033[K", end="", flush=True)

            # Update line count for next iteration
            line_count = len(str(tasks_data).split("\n")) + 2

            # Go back up to the saved position
            print(f"\033[{line_count}A", end="", flush=True)

            # Wait before refresh
            time.sleep(1)

    except KeyboardInterrupt:
        # Move past the output before exiting
        print(f"\033[{line_count}B", end="", flush=True)
        # Show cursor again before exiting
        print("\033[?25h", end="", flush=True)
        return
    finally:
        # Ensure cursor is visible even if there's an error
        print("\033[?25h", end="", flush=True)
