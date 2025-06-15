import curses
from typing_extensions import Annotated
from torch_snippets import AD
from typer import Argument
from .__pre_init__ import _cli
from .sector import sector_crud, _list_sectors

from ..models.nodes import NodeRead, NodeType, NodeStatus, SCHEMA_OUT_MAPPING


def truncate_meta(meta):
    """
    Truncate the meta string to a maximum of 20 characters.
    """
    if meta in [None, "{}"]:
        return None
    if len(meta) > 20:
        return meta[:20] + "..."
    return meta


def _fetch(id=None, sector=None, filters=None):
    """
    Test command to check if the CLI is working.
    """
    o = AD()
    sectors = sector_crud.crud._read_all()
    ids = [s.id for s in sectors] if id is None else [id]
    if sector is not None:
        ids = [s.id for s in sectors if s.title == sector]

    def build_tree(node_id):
        node = sector_crud.crud._read(NodeRead(id=node_id))
        node = SCHEMA_OUT_MAPPING[node.type](**node.model_dump())
        children = sector_crud.crud.get_children(NodeRead(id=node_id))
        children = sorted(children, key=lambda x: 0 if x.title == "_" else 1)

        # Apply filters if provided
        if filters:
            # Filter completed tasks older than specified time
            if (
                "hide_completed_older_than" in filters
                and node.status == NodeStatus.completed
            ):
                if (
                    hasattr(node, "updated_at")
                    and node.updated_at < filters["hide_completed_older_than"]
                ):
                    return None, None

        if not children:
            return node, node

        subtree = AD()
        subtree["__node"] = node
        for child in children:
            child_node, child_tree = build_tree(child.id)
            if child_node is not None:  # Only add if node wasn't filtered out
                subtree[child_node.title] = child_tree

        return node, subtree

    for node_id in ids:
        node, tree = build_tree(node_id)
        if node is not None:  # Only add if node wasn't filtered out
            o[node.title] = tree
            o["__node"] = node
    return o


def fetch_all_paths(incomplete: str):
    o = _fetch()
    o.drop("__node")
    o = o.flatten_and_make_dataframe()
    o = o.apply(
        lambda x: "/".join(
            x.dropna().astype(str).map(lambda x: x.split(" + ")[0])[:-1]
        ),
        axis=1,
    ).tolist()
    if incomplete:
        o = [_o for _o in o if incomplete in _o]
    return o


def fetch(id=None, sector=None, as_dataframe=True, filters=None):
    # Default filter for hiding completed tasks older than 5 minutes
    if filters is None:
        from datetime import datetime, timedelta, timezone

        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        five_minutes_ago = current_time - timedelta(minutes=1)
        filters = {"hide_completed_older_than": five_minutes_ago}

    o = _fetch(id=id, sector=sector, filters=filters)
    if as_dataframe:
        o.drop("__node")
        o = o.map(lambda x: truncate_meta(x.meta) if hasattr(x, "meta") else x)
        o = o.flatten_and_make_dataframe()
        o.fillna("_", inplace=True)
        o = o.map(lambda x: x.split(" + ")[0])
        o.columns = ["SECTOR", "AREA", "PROJECT", "SECTION", "TASK", "_"][
            : len(o.columns)
        ]
        o.set_index(
            ["SECTOR", "AREA", "PROJECT", "SECTION"][: len(o.columns) - 1], inplace=True
        )
        if sector is not None:
            o = o.loc[sector]
        return o
    return o


@_cli.command("x")
def watch_tasks(
    sector: Annotated[str | None, Argument(autocompletion=_list_sectors)],
):
    import time

    def live_display(stdscr):
        curses.curs_set(0)  # Hide the cursor
        curses.use_default_colors()
        stdscr.nodelay(True)  # Make getch non-blocking

        while True:
            stdscr.clear()
            data = fetch(sector=sector)
            lines = data.to_string().splitlines()
            line_size = max(len(line) for line in lines)
            stdscr.addstr(1, 5, f"{sector.capitalize()} - {len(data)} tasks")
            for i, line in enumerate(lines, start=2):
                if i == 4:
                    stdscr.addstr(i, 5, "-" * line_size)
                if i >= 4:
                    i += 1
                stdscr.addstr(i, 5, line)
            stdscr.refresh()

            # Wait up to 0.1s for a key press; exit if 'q' is pressed
            for _ in range(50):  # 50 x 0.1s = 5s total
                key = stdscr.getch()
                if key in [ord("q"), ord("x")]:
                    return
                time.sleep(0.1)

    curses.wrapper(live_display)
