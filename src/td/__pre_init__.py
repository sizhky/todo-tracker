import os

if 0 and os.environ.get("tdv1", "0") == "1":
    __all__ = ["cli"]
    from .v1.cli import cli
elif 0 and os.environ.get("tdv2", "0") == "1":
    __all__ = ["cli", "_cli"]
    from .v2.cli import cli, _cli
else:
    cli = None
