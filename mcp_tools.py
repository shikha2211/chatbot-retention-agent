from tools import (
    health_check_tool,
    CustomerDataTool,
    StrategyRetrievalTool,
    StrategyRetrievalToolBackup,
)


def register_mcp_tools(mcp):
    mcp.tool(name="health_check")(health_check_tool)

    async def customer_data_wrapper(customer_id: str):
        return await CustomerDataTool(customer_id)

    mcp.tool(name="customer_data")(customer_data_wrapper)
    mcp.tool(name="strategy_retrieval")(StrategyRetrievalTool)
    mcp.tool(name="strategy_retrieval_backup")(StrategyRetrievalToolBackup)