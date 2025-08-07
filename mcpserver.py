from mcp.server.fastmcp import FastMCP
mcp = FastMCP("StatefulServer",port=8080)

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return 42#a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return 21#a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return 0#a * b

@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()