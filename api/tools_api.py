from fastapi import APIRouter, HTTPException
from fastmcp import Client
from typing import Any, Dict
from models import CustomerProfile
from tools import (
    CustomerDataTool,
    StrategyRetrievalTool,
    StrategyRetrievalToolBackup,
)
from agent import root_agent
from mcp_functions import McpCustomerDataTool, McpStrategyRetrievalTool

router = APIRouter(prefix="/api/tools", tags=["tools"])

MCP_CONFIG = {
    "mcpServers": {
        "local": {"url": "http://127.0.0.1:8000/mcp", "headers": {}}
    }
}

@router.get("/health")
async def health():
    from tools import health_check_tool
    return health_check_tool()


@router.get("/customer/{customer_id}")
async def customer_data(customer_id: str):
    if McpCustomerDataTool not in root_agent.tools:
        raise HTTPException(status_code=403, detail="McpCustomerDataTool not available in agent")
    return await CustomerDataTool(customer_id)


@router.post("/strategy")
async def strategy(customerData: Dict[str, Any]):
    if McpStrategyRetrievalTool not in root_agent.tools:
        raise HTTPException(status_code=403, detail="McpStrategyRetrievalTool not available in agent")
    try:
        return await StrategyRetrievalTool(customerData)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/backup")
async def strategy_backup(customerData: Dict[str, Any]):
    try:
        return await StrategyRetrievalToolBackup(customerData)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))