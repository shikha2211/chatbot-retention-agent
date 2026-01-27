from fastmcp import Client
import logging

# MCP client configuration — ensure this matches your running MCP server
MCP_CONFIG = {
    "mcpServers": {
        "local": {
            "url": "http://127.0.0.1:8000/mcp",
            "headers": {}
        }
    }
}

# MCP-backed tool wrappers (these have the same callable names the agent expects)
async def McpCustomerDataTool(customer_id: str):
    logging.info
    client = Client(MCP_CONFIG)
    async with client:
        return await client.call_tool(name="customer_data", arguments={"customer_id": customer_id})

async def McpStrategyRetrievalTool(customerData):
    client = Client(MCP_CONFIG)
    async with client:
        return await client.call_tool(name="strategy_retrieval", arguments={"customerData": customerData})

async def McpHealthCheckTool():
    client = Client(MCP_CONFIG)
    async with client:
        return await client.call_tool(name="health_check", arguments={})