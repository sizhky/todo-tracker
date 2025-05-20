from torch_snippets import AD

from .__pre_init__ import cli
from .sector import sector_crud

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


def fetch_all_paths():
    o = _fetch()
    o = o.flatten_and_make_dataframe()
    o = o.apply(
        lambda x: "/".join(
            x.dropna().astype(str).map(lambda x: x.split(" + ")[0])[:-1]
        ),
        axis=1,
    )
    return o


def fetch(id=None, sector=None, as_dataframe=True):
    o = _fetch(id=id, sector=sector)
    if as_dataframe:
        o = o.flatten_and_make_dataframe()
        o.fillna("_", inplace=True)
        o = o.map(lambda x: x.split(" + ")[0])
        o.columns = ["SECTOR", "AREA", "PROJECT", "SECTION", "TASK", "_"]
        o.set_index(["SECTOR", "AREA", "PROJECT", "SECTION"], inplace=True)
        if sector is not None:
            o = o.loc[sector]
        return o
    return o


@cli.command("tw")
def watch_tasks(sector=None):
    print(fetch(sector=sector))
    return
