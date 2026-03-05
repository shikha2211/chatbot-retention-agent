import os
import uvicorn
from fastapi import FastAPI
# Use absolute imports for the background logic
# from customer_mcp_server.mcp_functions import McpFetchCustomerInfo, McpHealthCheckTool
# from customer_mcp_server.customer_service import customer_data_wrapper
from customer_mcp_server.tools_api import router as tools_router

MCP_PORT = os.getenv('MCP_PORT')

# 1. Initialize the FastAPI app
# This is the "app" variable uvicorn is looking for
app = FastAPI(title="Customer Retention Browser API")

# 2. Include the router from your tools_api.py
app.include_router(tools_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Browser API is running. Access /docs for interactive testing."
    }

if __name__ == "__main__":
    # This block allows running via 'python -m customer_mcp_server.main'
    uvicorn.run(app, host="127.0.0.1", port=MCP_PORT)
