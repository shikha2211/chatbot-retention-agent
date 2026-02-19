# from .mcp_functions import McpFetchCustomerInfo,McpHealthCheckTool
# from .customer_service import customer_data_wrapper


# def register_mcp_tools(mcp):
#     mcp.tool(name="health_check")(McpHealthCheckTool)

#     async def customer_data_by_id(customer_id: str):
#         return await McpFetchCustomerInfo(customer_id)

#     async def customer_data_text(text: str):
#         return await customer_data_wrapper(text)

#     mcp.tool(name="customer_data")(customer_data_by_id)
#     mcp.tool(name="customer_data_text")(customer_data_text)

from mcp.server.fastmcp import FastMCP
# Use absolute imports to ensure ADK can find them
from mcp_functions import McpFetchCustomerInfo, McpHealthCheckTool
from customer_service import customer_data_wrapper

mcp = FastMCP("Customer Retention Server")

# Register your existing tools
mcp.tool(name="health_check")(McpHealthCheckTool)

@mcp.tool()
async def customer_data_by_id(customer_id: str):
    """Fetch customer info by their ID."""
    return await McpFetchCustomerInfo(customer_id)

@mcp.tool()
async def customer_data_text(text: str):
    """Fetch customer info using a natural language query."""
    return await customer_data_wrapper(text)

if __name__ == "__main__":
    # FastMCP starts its own event loop here
    mcp.run(transport="stdio")

