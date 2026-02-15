from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FinSightMCP")

@mcp.tool()
def get_financial_context() -> str:
    return "Market is currently stable with positive trends in tech."

if __name__ == "__main__":
    mcp.run(transport='stdio')