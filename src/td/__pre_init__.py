__all__ = ["cli"]

import os

if os.environ.get("tdv1", "0") == "1":
    from .v1.cli import cli
else:
    from .v2.cli import cli
