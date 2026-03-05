import sys
from mcp.server.fastmcp import FastMCP
# Use absolute imports to ensure ADK can find them
from mcp_functions import McpFetchCustomerInfo, McpHealthCheckTool
from customer_service import customer_data_wrapper

mcp = FastMCP("Customer Retention Server")

# Register your existing tools
@mcp.tool()
async def system_health_status():
    """
    Check if the customer database and MCP services are functioning correctly.
    Use this if the user asks about system status or connectivity.
    """
    return await McpHealthCheckTool()

@mcp.tool()
async def customer_data_by_id(customer_id: str):
    """
    USE THIS ONLY when you have a specific numeric or alphanumeric Customer ID.
    Example: '12345', 'CUST-99'.
    """
    return await McpFetchCustomerInfo(customer_id)

@mcp.tool()
async def customer_data_text(text: str):
    """
    USE THIS for natural language searches or complex queries where no ID is present.
    Example: 'Find customers who haven't paid in 3 months' or 'Show me Jane Doe'.
    """
    return await customer_data_wrapper(text)


if __name__ == "__main__":
    print("🚀 Customer MCP Server (Stdio) is starting...", file=sys.stderr)
    # FastMCP starts its own event loop here
    mcp.run(transport="stdio")

