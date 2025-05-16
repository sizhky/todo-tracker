import sys
from typer import Typer

from ..core.db import create_db_and_tables

cli = Typer()
create_db_and_tables()

if len(sys.argv) == 1:
    sys.argv.append("tw")
