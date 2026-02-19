import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from tools import CustomerDataTool, StrategyRetrievalTool
# from mcp_client.mcp_functions import McpFetchCustomerInfo
# from mcp_client.customer_service import customer_data_wrapper
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

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

# Build the agent using MCP-backed tools
root_agent = LlmAgent(
    name="retention_agent",
    model=AGENT_MODEL,
    description="This agent invokes MCP tools for customer data and strategy retrieval",
    instruction=instructionsForAgent,
    tools=[CustomerDataTool, StrategyRetrievalTool],
    # tools=[CustomerDataTool, StrategyRetrievalTool, McpFetchCustomerInfo, customer_data_wrapper],
)

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

inferred_app_name = getattr(root_agent, "__module__", "").split(".")[0] or APP_NAME
runner = Runner(agent=root_agent, app_name=inferred_app_name, session_service=session_service)

# Move mcp related code to separate folder
# No need for mcp endpoint of StrategyRetrievalTool
# agent to mcp communication