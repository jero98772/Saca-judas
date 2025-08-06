from mcp.server.fastmcp import FastMCP
mcp = FastMCP("StatefulServer",port=8080)

@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# Run server with streamable_http transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")