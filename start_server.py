#!/usr/bin/env python3
"""
Startup script for the Customer Retention Agent FastAPI service.
This script runs the FastAPI server with proper configuration for the ADK agent.
"""

import uvicorn
import os
from dotenv import load_dotenv
from main import app
from services.scheduler_job import startScheduler
import threading


# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI server with ADK agent integration"""
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "9000"))  # Changed to 9000
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"\n==>Starting Customer Retention Agent API server...")
    print(f"\n==>Host: {host}")
    print(f"\n==>Port: {port}")
    print(f"\n==>Reload: {reload}")
    print(f"\n==>MONGO_URI: {os.getenv('MONGO_URI')}")
    print(f"\n==>CUSTOMER_API_URL: {os.getenv('CUSTOMER_API_URL')}")
    print(f"\n==>MILVUS_URI: {os.getenv('MILVUS_URI')}")
    
    print(f"\n==>API Documentation: http://{host}:{port}/docs")
    print(f"\n==>Chat Endpoint: http://{host}:{port}/api/chat")
    print(f"\n==>Health Check: http://{host}:{port}/api/chat/health")
    print(f"\n==>Finally starting the scheduler")
    threading.Thread(target=startScheduler, daemon=True).start()


    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
