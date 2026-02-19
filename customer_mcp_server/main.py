from fastmcp import FastMCP
from .mcp_functions import McpFetchCustomerInfo, McpHealthCheckTool
from .customer_service import customer_data_wrapper

# Create MCP server instance
mcp = FastMCP(
    "customer_mcp_server",
)

# Register tools using decorators
@mcp.tool()
async def health_check() -> dict:
    """Health check for MCP service."""
    return await McpHealthCheckTool()

@mcp.tool()
async def customer_data(customer_id: str) -> dict:
    """Fetch customer data by ID."""
    return await McpFetchCustomerInfo(customer_id)

@mcp.tool()
async def customer_data_text(text: str) -> dict:
    """Extract customer ID from text and fetch customer data."""
    return await customer_data_wrapper(text)


if __name__ == "__main__":
    print("Starting Customer MCP Server...")
    print("Server URL: http://0.0.0.0:3333")
    print("\nTo connect from ADK agents, use:")
    print("  from adk_agent import create_agent")
    print("  agent = create_agent(server_url='http://localhost:3333/sse')")
    print()

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=3333
    )
