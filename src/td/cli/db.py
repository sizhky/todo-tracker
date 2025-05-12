import os
from pathlib import Path
import typer
from typing_extensions import Annotated

from .__pre_init__ import cli

from ..core.settings import ACTIVE_DB_LINK_PATH, DB_DIR, ACTIVE_DB_LINK_FILENAME

@cli.command(name="db.a", help="Print the path the active database symlink points to.")
def database_active():
    """
    Prints the actual database file the application is configured to use via a symlink.
    """
    symlink_path = ACTIVE_DB_LINK_PATH
    if not symlink_path.exists():
        typer.echo(f"Error: The active database link '{symlink_path}' does not exist.", err=True)
        typer.echo("Use 'td dset <name>' to set an active database.")
        raise typer.Exit(code=1)

    if not symlink_path.is_symlink():
        typer.echo(f"Error: '{symlink_path}' is not a symbolic link. It should be.", err=True)
        typer.echo(f"The application expects '{ACTIVE_DB_LINK_PATH}' to be a symlink to an actual database file.")
        typer.echo("Please remove or rename it and use 'td dset <name>'.")
        raise typer.Exit(code=1)

    # Path.resolve() gives the absolute path of the symlink's target
    target_path = symlink_path.resolve()
    typer.echo(f"Active database link: '{symlink_path}'")
    typer.echo(f" -> Points to: '{target_path}'")
    if not target_path.exists():
        typer.echo(f"Warning: The target file '{target_path}' does not currently exist. It may be created on next use.", err=True)
    return target_path


def _all_dbs():
    """
    Returns a list of all database files in the data directory.
    """
    all_dbs = []
    for item in DB_DIR.iterdir():
        if item.is_file() and item.name.endswith(".db") and item.name != ACTIVE_DB_LINK_FILENAME:
            all_dbs.append(item)
    from torch_snippets import stems
    o = stems(all_dbs)
    return o

@cli.command(name="db.l", help="List available databases and show the active one.")
def list_databases():
    """
    Lists all actual database files (*.db) in the data directory
    and indicates which one is currently active via the symlink.
    """
    typer.echo(f"Available databases in '{DB_DIR}':")
    symlink_path = ACTIVE_DB_LINK_PATH
    
    current_target_resolved_path = None
    is_symlink_valid = False

    if symlink_path.exists() and symlink_path.is_symlink():
        try:
            current_target_resolved_path = symlink_path.resolve()
            is_symlink_valid = True # Valid symlink, even if target might not exist yet
        except FileNotFoundError: # Symlink is broken
            typer.echo(f"Warning: Active database link '{symlink_path}' is broken.", err=True)
            try:
                # Show what it was supposed to point to
                broken_target_name = Path(os.readlink(symlink_path)).name
                typer.echo(f"         It was pointing to '{broken_target_name}'.", err=True)
            except OSError:
                pass # Could not read link
        except OSError:
            typer.echo(f"Warning: Could not fully resolve symlink '{symlink_path}'.", err=True)


    found_dbs = False
    all_dbs = []
    for item in DB_DIR.iterdir():
        if item.is_file() and item.name.endswith(".db") and item.name != ACTIVE_DB_LINK_FILENAME:
            all_dbs.append(item)
    if not all_dbs:
        typer.echo("No user-created .db files found (e.g., 'main.db', 'dev.db').")
        return
    
    # Sort the database files by name
    for item in sorted(DB_DIR.iterdir()): # Sort for consistent listing
        # List actual .db files, not the symlink itself if it's also named .db
        if item.is_file() and item.name.endswith(".db") and item.name != ACTIVE_DB_LINK_FILENAME:
            found_dbs = True
            marker = ""
            if is_symlink_valid and current_target_resolved_path and item.resolve() == current_target_resolved_path:
                marker = " (active)"
            typer.echo(f"- {item.name}{marker}")

    if not found_dbs:
        typer.echo("No user-created .db files found (e.g., 'main.db', 'dev.db').")

    if not symlink_path.exists():
         typer.echo(f"\nNote: The active database link '{ACTIVE_DB_LINK_FILENAME}' does not exist. Use 'td dset <name>'.")
    elif not symlink_path.is_symlink():
        typer.echo(f"\nWarning: '{ACTIVE_DB_LINK_FILENAME}' exists but is not a symlink. Cannot determine active DB via symlink.", err=True)
    elif is_symlink_valid and current_target_resolved_path:
        typer.echo(f"\nThe active database link '{ACTIVE_DB_LINK_FILENAME}' currently points to '{current_target_resolved_path.name}'.")
    elif not is_symlink_valid and symlink_path.exists() and symlink_path.is_symlink(): # Broken link case
        pass # Warning already printed
    from torch_snippets import stems
    return stems(all_dbs)

@cli.command(name="db.set", help="Set a database as active by updating the symlink.")
def set_database(
    name: Annotated[
        str, typer.Argument(help="Name of the database to activate (e.g., 'dev'). '.db' will be appended.", autocompletion=_all_dbs)
    ]
):
    """
    Sets the specified database as active. This command updates the
    '{ACTIVE_DB_LINK_FILENAME}' symlink in '{DB_DIR}' to point to '<name>.db'.
    """
    if not name or name.isspace():
        typer.echo("Error: Database name cannot be empty.", err=True)
        raise typer.Exit(code=1)
    if ".db" in name.lower():
        typer.echo("Error: Please provide the database name without the '.db' extension. It will be added automatically.", err=True)
        raise typer.Exit(code=1)

    symlink_path = DB_DIR / ACTIVE_DB_LINK_FILENAME
    target_db_filename = f"{name}.db" # This is the name of the actual database file
    target_db_full_path = DB_DIR / target_db_filename

    # Remove existing symlink or file at symlink_path
    if symlink_path.exists():
        if symlink_path.is_symlink() or symlink_path.is_file(): # Allow overwriting a regular file too
            try:
                symlink_path.unlink()
            except OSError as e:
                typer.echo(f"Error removing existing '{symlink_path}': {e}", err=True)
                raise typer.Exit(code=1)
        else:
            typer.echo(f"Error: '{symlink_path}' exists and is not a file or symlink (e.g., it's a directory). Please remove it manually.", err=True)
            raise typer.Exit(code=1)

    try:
        # Create the symlink. os.symlink(source, link_name)
        # source (target_db_filename) is relative to the directory of the link_name (symlink_path)
        os.symlink(target_db_filename, symlink_path)
        
        # Refresh the database engine to use the new database
        from ..core.db import engine
        engine.dispose()
        
        # Create a new engine with the same URL (which now points to the new database via the symlink)
        import importlib
        import sys
        
        # Re-import the db module to refresh the engine
        # This is a more robust way to ensure the engine is recreated with the new database
        if "td.core.db" in sys.modules:
            importlib.reload(sys.modules["td.core.db"])
        
        typer.echo(f"Success! Active database link '{symlink_path.name}' now points to '{target_db_filename}'.")
        typer.echo(f"The application will use '{target_db_full_path}' for all subsequent operations.")
        
        # Create tables in the new database if needed
        from ..core.db import create_db_and_tables
        if not target_db_full_path.exists():
            typer.echo(f"Creating tables in new database '{target_db_full_path}'...")
            create_db_and_tables()
        else:
            typer.echo(f"Using existing database file '{target_db_full_path}'.")
            
    except OSError as e:
        typer.echo(f"Error creating symlink '{symlink_path}' to '{target_db_filename}': {e}", err=True)
        typer.echo("Make sure you have permissions to create symlinks in this directory and that the target name is valid.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


@cli.command(name="db.rm", help="Remove a database.")
def remove_database(
    name: Annotated[str, typer.Argument(help="Name of the database to remove (e.g., 'dev'). '.db' will be appended.", autocompletion=_all_dbs)]
):
    """
    Removes the specified database file from the data directory. 
    And makes default.db the active database.
    """
    from torch_snippets import stem
    if stem(name) == stem(database_active()):
        other_dbs = [x for x in list_databases() if stem(x) != stem(name)]
        typer.echo(f"Error: Cannot remove the active database. Please set another database from ({other_dbs}) as active first.", err=True)
        raise typer.Exit(code=1)

    db_path = DB_DIR / f"{name}.db"
    if not os.path.exists(db_path):
        typer.echo(f"Database '{name}.db' does not exist. Ignoring removal.")
    else:
        os.remove(db_path)

