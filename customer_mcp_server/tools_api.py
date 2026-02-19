from fastapi import FastAPI, APIRouter, HTTPException, Request
from customer_mcp_server.mcp_functions import McpFetchCustomerInfo
from customer_mcp_server.customer_service import customer_data_wrapper

app = FastAPI(title="Customer Tools API")

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
    
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "API is alive on 8080"}
    
if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8080)
