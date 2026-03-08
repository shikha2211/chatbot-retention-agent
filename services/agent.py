import os
import sys
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tools import CustomerDataTool, StrategyRetrievalTool
from common import create_retention_agent
# Import the MCP Bridge classes
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams
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

load_dotenv()
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
FF_MCP_ENABLED = os.getenv('FF_MCP_ENABLED', 'false').lower() == 'true'

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

agent_tools = [CustomerDataTool, StrategyRetrievalTool]

# Create a dynamic instruction set
final_instructions = instructionsForAgent

# 3. Conditionally add the MCP Toolset
if not FF_MCP_ENABLED:
    print("MCP Mode: Enabled. Connecting to customer_mcp_server...", file=sys.stderr)
    
    final_instructions += (
        "\n\nIMPORTANT: You have access to specialized MCP (Model Context Protocol) tools. "
        "Always prefer using 'customer_data_by_id', 'customer_data_text', or 'system_health_status' "
        "over any other similar tools when FF_MCP_ENABLED is true."
    )

    mcp_connection = StdioConnectionParams(
        server_params={
            "command": "python3",
            "args": ["mcp_tools.py"],
            # Since agent.py is now in /services, we go up and into the tool folder
            "cwd": os.path.join(os.path.dirname(__file__), "..", "customer_mcp_server"),
            # Ensure the tool process can see the root package
            "env": {"PYTHONPATH": "."}
        }
    )
    # Wrap the connection in a toolset and add to the list
    mcp_toolset = McpToolset(connection_params=mcp_connection)
    print ("mcp_toolset", mcp_toolset)
    agent_tools.append(mcp_toolset)
else:
    print("Local Mode: MCP tools are disabled.", file=sys.stderr)

# 4. Initialize the Agent with the dynamic tool list
root_agent = create_retention_agent(
    tools=agent_tools,
    instruction=final_instructions,
    description="This agent invokes MCP tools for customer data and strategy retrieval",
    model="gemini-2.0-flash"
    )

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

