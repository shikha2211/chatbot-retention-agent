import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv  # Import load_dotenv
from tools import CustomerDataTool, StrategyRetrievalTool, AllCustomersDataTool
from common import create_retention_agent
from agent_prompt import instructionsForAgent
import warnings

# Ignore all warnings

warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)

SESSION_ID = "sesson-223222"
USER_ID = "Lalit1122"
APP_NAME = "Retention_Agent"

load_dotenv()  # Load environment variables

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

root_agent = create_retention_agent(
    tools=[CustomerDataTool, StrategyRetrievalTool, AllCustomersDataTool],
    instruction=instructionsForAgent,
    description="This agent specializes in Providing customer details and retention strategies based on user query",
    model=AGENT_MODEL
    )

# expose the above agent as a fast api endpoint POST /retention-agent/query
# Deploy on some cloud
# Session and Memory managemment 
# Guardrails 

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
