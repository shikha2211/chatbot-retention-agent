import uvicorn
import json
import os
import sys
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tools import CustomerDataTool, StrategyRetrievalTool, ImplementStrategyTool
from common import create_retention_agent
# Import the MCP Bridge classes
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_toolset import SseConnectionParams
from dotenv import load_dotenv
from google.genai import types
from agent_prompt import instructionsForAgent
import warnings
import logging

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

SESSION_ID = "sesson-223222"
USER_ID = "Lalit1122"
APP_NAME = "Retention_Agent"

# Load .env from customer-mcp-server
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'customer-mcp-server', '.env')
load_dotenv(dotenv_path=env_path)

# Import FF_MCP_ENABLED from .env file
ff_mcp_value = os.getenv("FF_MCP_ENABLED", "False").strip()
FF_MCP_ENABLED = ff_mcp_value.lower() in ['true', '1', 'yes'] if ff_mcp_value else False

# --- FIX START: Configure global environments for ADK / Google SDK requirements ---
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["vertexai"] = "True"  # ADK framework looks for this specific lowercase parameter
os.environ["project"] = os.environ.get("GOOGLE_CLOUD_PROJECT", "snappy-mark-499214-f0")
os.environ["location"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
# ----------------------------------------------------------------------------------

# FIX: Parse the raw Vercel JSON text string if a local file path isn't being used
credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if credentials_json:
    try:
        # Create a temporary file path that stays accessible during runtime
        temp_dir = tempfile.gettempdir()
        temp_cred_path = os.path.join(temp_dir, "gcp_service_account_token.json")
        
        # Load and cleanly format the string structure
        parsed_creds = json.loads(credentials_json)
        
        with open(temp_cred_path, "w") as f:
            json.dump(parsed_creds, f)
            
        # Point the Google Core SDK directly to the physical file on disk
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path
        print(f"✅ Production ADC File written successfully to: {temp_cred_path}")
        
    except Exception as e:
        print(f"⚠️ Production Credentials Parsing Error: {e}")
else:
    # Local Development fallback tracking
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️ WARNING: No Google credentials variables detected.")

MODEL_GEMINI_2_0_FLASH = "gemini-2.5-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

# Register all tools the agent may call, including implementation tool
agent_tools = [CustomerDataTool, StrategyRetrievalTool, ImplementStrategyTool]

# Create a dynamic instruction set
final_instructions = instructionsForAgent

# 3. Conditionally add the MCP Toolset
if FF_MCP_ENABLED:
    print("MCP Mode: Enabled. Connecting to customer_mcp_server...", file=sys.stderr)
    
    final_instructions += (
        "\n\nIMPORTANT: You have access to specialized MCP (Model Context Protocol) tools. "
        "Always prefer using 'customer_data_by_id', 'customer_data_text', or 'system_health_status' "
        "over any other similar tools when FF_MCP_ENABLED is true."
    )
    mcp_connection = SseConnectionParams(
        url="http://localhost:8000/sse"  # The SSE endpoint of your MCP server
    )
    # Wrap the connection in a toolset and add to the list
    mcp_toolset = McpToolset(connection_params=mcp_connection)
    print("mcp_toolset initialized:", mcp_toolset)
    agent_tools.append(mcp_toolset)
else:
    print("Local Mode: MCP tools are disabled.", file=sys.stderr)

# 4. Initialize the Agent with the dynamic tool list
# CHANGE: Reverted to your standard arguments. Underlying ADK reads the injected os.environ values.
root_agent = create_retention_agent(
    tools=agent_tools,
    instruction=final_instructions,
    description="This agent invokes MCP tools for customer data and strategy retrieval",
    model=AGENT_MODEL
)

# FIXED DEBUG LOGIC: Handles both function-based tools and MCP object tools
tool_names = []
for t in root_agent.tools:
    if hasattr(t, 'name'):
        tool_names.append(t.name)
    elif hasattr(t, '__name__'):
        tool_names.append(t.__name__)
    else:
        tool_names.append(str(t))

print(f"DEBUG: Agent has access to tools: {tool_names}")

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

   # Start the server
if __name__ == "__main__":
    print("\n🚀 Starting FastApi Backend Server...")
    print("📍 Host: http://127.0.0.1:8000")
    print("📝 Interactive API Documentation available at: http://127.0.0\n")
    
    # This block triggers the active loop that keeps your terminal session alive
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=9000, 
        reload=True
    )