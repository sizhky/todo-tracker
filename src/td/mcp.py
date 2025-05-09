from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tasky MCP Server")

# from .cli import list_tasks as list_tasks_cli
from td.cli import cli

commands = cli.registered_commands
for command in commands:
    func = command.callback
    func.from_mcp = True
    mcp.tool()(func)


# @mcp.tool()
# def list_tasks() -> str:
#     """List all tasks using the imported CLI function."""
#     return list_tasks_cli(as_json=True)


if __name__ == "__main__":
    mcp.run()
