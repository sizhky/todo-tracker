from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tasky MCP Server")

# from .cli import list_tasks as list_tasks_cli
from td.__pre_init__ import cli

commands = cli.registered_commands
for command in commands:
    func = command.callback
    func._source = "mcp"
    mcp.tool()(func)


if __name__ == "__main__":
    mcp.run()
