from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict
from .mcp_functions import McpFetchCustomerInfo
from .customer_service import customer_data_wrapper

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.get("/health")
async def health():
    from tools import health_check_tool
    return health_check_tool()


@router.get("/customer/{customer_id}")
async def customer_data(customer_id: str):
    # Fetch via MCP client
    try:
        return await McpFetchCustomerInfo(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customer/query")
async def customer_query(request: Request):
    payload = await request.json()
    text = payload.get("text") if isinstance(payload, dict) else None
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body")
    try:
        return await customer_data_wrapper(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
