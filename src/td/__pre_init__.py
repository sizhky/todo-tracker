import os

if os.environ.get("tdv1", "0") == "1":
    __all__ = ["cli"]
    from .v1.cli import cli
else:
    __all__ = ["cli", "_cli"]
    from .v2.cli import cli, _cli
