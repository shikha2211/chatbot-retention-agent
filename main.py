import os
import json
import tempfile
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ==================================================================================
# 1. CRITICAL VERCEL ENTRY BOOTSTRAP (Must run BEFORE any local imports)
# ==================================================================================
load_dotenv()

# Force Vertex AI parameters globally into system memory
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["vertexai"] = "True"
os.environ["project"] = os.environ.get("GOOGLE_CLOUD_PROJECT", "snappy-mark-499214-f0")
os.environ["location"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# Write the credentials JSON string to a physical /tmp file on the serverless disk
credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if credentials_json:
    try:
        temp_dir = tempfile.gettempdir()
        temp_cred_path = os.path.join(temp_dir, "gcp_service_account_token.json")
        
        parsed_creds = json.loads(credentials_json)
        
        with open(temp_cred_path, "w") as f:
            json.dump(parsed_creds, f)
            
        # Point the Google Core SDK directly to the physical file on the serverless instance
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path
        print(f"✅ Vercel Entry Point: Credentials written successfully to: {temp_cred_path}")
        
    except Exception as e:
        print(f"⚠️ Vercel Entry Point Credentials Parsing Error: {e}")

# ==================================================================================
# 2. LOCAL ROUTER IMPORTS (Now safe to load since credentials are bound to disk)
# ==================================================================================
from api import portfolio, chatbot_endpoint, query_zilliz_milvus_api, autonomous_agent

app = FastAPI(
    title="Retention Agent API",
    description="Backend services for the Retention Agent Chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(portfolio.router, prefix="/api")
app.include_router(chatbot_endpoint.router, prefix="/api")
app.include_router(query_zilliz_milvus_api.router, prefix="/api")
app.include_router(autonomous_agent.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Retention Agent API is running"}
