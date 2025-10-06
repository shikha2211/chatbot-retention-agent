from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import portfolio, chatbot_endpoint

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
