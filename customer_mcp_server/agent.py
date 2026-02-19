from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
# Import the container we know exists from your previous scan
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams

# In ADK 1.25.1, the 'server_params' field often expects 
# a raw dictionary if the specific class is hard to find.
connection_params = StdioConnectionParams(
    server_params={
        "command": "python",
        "args": ["mcp_tools.py"],
        "cwd": "customer_mcp_server",
        "env": {"PYTHONPATH": ".."} # It tells the background process to look one level up (..) so it can resolve 'from customer_mcp_server import
    }
)

toolset = McpToolset(connection_params=connection_params)

root_agent = LlmAgent(
    name="customer_retention_agent",
    model="gemini-2.0-flash",
    instruction="You are a customer retention specialist.",
    tools=[toolset],
)
