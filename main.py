from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
from api import portfolio, chatbot_endpoint, query_zilliz_milvus_api
from api.tools_api import router as tools_api_router
from mcp_tools import register_mcp_tools

app = FastAPI(
    title="Customer Retention Agent API",
    description="FastAPI service exposing Google ADK agent for customer retention strategies",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["*"] for all origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(portfolio.router, prefix="/api")
app.include_router(chatbot_endpoint.router, prefix="/api")
app.include_router(query_zilliz_milvus_api.router, prefix="/api")
app.include_router(tools_api_router)

mcp = FastMCP.from_fastapi(app=app, host="127.0.0.1", port=8000)

register_mcp_tools(mcp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
