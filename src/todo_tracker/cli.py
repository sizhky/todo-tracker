from typer import Typer
from torch_snippets import readlines
from torch_snippets.paths import current_file_dir

from .tasks import tasks_cli

cli = Typer()
cli.add_typer(tasks_cli, name="task")

@cli.command()
def version():
    v = readlines(f'{current_file_dir(__file__)}/version', silent=True)[0]
    print(v)

@cli.command()
def health():
    print("OK")

if __name__ == "__main__":
    cli()