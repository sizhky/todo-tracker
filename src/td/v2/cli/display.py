import curses
from typing_extensions import Annotated
from torch_snippets import AD
from typer import Argument
from .__pre_init__ import _cli
from .sector import sector_crud, _list_sectors

from ..models.nodes import NodeRead


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
        children = sector_crud.crud.get_children(NodeRead(id=node_id))
        children = sorted(children, key=lambda x: 0 if x.title == "_" else 1)
        if not children:
            return title, node.meta if node.meta != "{}" else None
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
    def live_display(stdscr):
        stdscr.clear()
        data = fetch(sector=sector)
        lines = data.to_string().splitlines()
        for i, line in enumerate(lines):
            stdscr.addstr(i, 0, line)
        stdscr.refresh()
        stdscr.getch()

    curses.wrapper(live_display)
