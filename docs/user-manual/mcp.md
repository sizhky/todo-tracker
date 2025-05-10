You can run 

```python
make mcp
```

to start a fastmcp based server.

Since the server tools have been auto-generated, all the tools have a one-to-one mapping in terms of behaviour with the cli commands.

You can import the server as shown in the following example

```json
{
  "mcpServers": {
    "Tasky MCP Server": {
      "transport": "stdio",
      "enabled": true,
      "command": "/path/to/todo-tracker/.venv/bin/mcp",
      "args": [
        "run",
        "/path/to/todo-tracker/src/td/mcp.py"
      ],
      "env": {},
      "url": null
    }
  }
}
```

and automate your tasks management using LLMs.