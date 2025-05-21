import curses
from typing_extensions import Annotated
from torch_snippets import AD
from typer import Argument
from .__pre_init__ import _cli
from .sector import sector_crud, _list_sectors

from ..models.nodes import NodeRead


def trucate_meta(meta):
    """
    Truncate the meta string to a maximum of 20 characters.
    """
    if meta in [None, "{}"]:
        return None
    if len(meta) > 20:
        return meta[:20] + "..."
    return meta


def _fetch(id=None, sector=None):
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
        title = f"{node.title} + {str(node.id)[:8]}"
        title = node.title
        children = sector_crud.crud.get_children(NodeRead(id=node_id))
        children = sorted(children, key=lambda x: 0 if x.title == "_" else 1)
        if not children:
            return title, trucate_meta(node.meta)
        subtree = AD()
        for child in children:
            child_title, child_tree = build_tree(child.id)
            subtree[child_title] = child_tree
        return title, subtree

    for node_id in ids:
        title, tree = build_tree(node_id)
        o[title] = tree
    return o


def fetch_all_paths(incomplete: str):
    o = _fetch()
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


def fetch(id=None, sector=None, as_dataframe=True):
    o = _fetch(id=id, sector=sector)
    if as_dataframe:
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
