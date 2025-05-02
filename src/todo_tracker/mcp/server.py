from mcp.server.fastmcp import FastMCP
from todo_tracker.tasks import cli as task_cli
from typing import Optional

mcp = FastMCP("Tasky MCP Server")
print("Starting MCP server...")

@mcp.tool()
def add_task(title: str, description: Optional[str] = None) -> str:
    """Add a new task using the imported CLI function."""
    # Call the CLI function directly
    return task_cli.add(title=title, description=description)

@mcp.tool()
def list_tasks() -> str:
    """List all tasks using the imported CLI function."""
    return task_cli.list(from_mcp=True)

@mcp.tool()
def update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> str:
    """Update a task using the imported CLI function."""
    return task_cli.update(task_id=task_id, title=title, description=description, status=status)

@mcp.tool()
def finish_task(task_id: int) -> str:
    """Mark a task as completed using the imported CLI function."""
    return task_cli.finish(task_id=task_id)

@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task using the imported CLI function."""
    return task_cli.delete(task_id=task_id)

if __name__ == "__main__":
    mcp.run()
