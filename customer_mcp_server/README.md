🧪 MCP Testing Guide: Retention Agent
This project uses the Model Context Protocol (MCP) to decouple the AI Agent from its data sources. The Agent (Port 9000) communicates with the Customer Data Server (Port 8000) via HTTP/SSE.

🛠️ Prerequisites
Python 3.11+ with a virtual environment (.venv) activated.
Node.js installed for the Frontend UI.
All environment variables (.env) configured with GOOGLE_API_KEY
FF_MCP_ENABLED = True in config.py

🚀 The "Terminal Trio" Startup Sequence
To test the full loop, you must start the services in this specific order to ensure the MCP Handshake succeeds.

Terminal 1: The MCP Tool Server (Port 8000)
This provides the data-fetching tools for Gemini.
cd customer_mcp_server
python3 mcp_tools.py

Wait for: Uvicorn running on http://127.0.0.1:8000

Terminal 2: The Agent Backend (Port 9000)
This is the "Brain" that orchestrates Gemini and the MCP Bridge.
# From the root directory
python3 start_server.py 
Wait for: mcp_toolset <google.adk.tools.mcp_tool...> (Confirms HTTP Bridge is active).

Terminal 3: The Chat UI inside chatbot-chat-interface (Port 3000)
npm run start
Access: Open http://localhost:3000 in your browser.


📝 Test Scenarios & Prompts

Test 1: Tool Discovery (The Handshake)
Prompt: "What tools do you currently have access to?"
Verification: The Agent should list customer_data_by_id, customer_data_text, and system_health_status.
Success: This proves the SseConnectionParams bridge is successfully reading the MCP server's manifest.

Test 2: Live CRM Lookup (MCP Tool)
Prompt: "Please fetch all details for CUST_0009"
Backend Log: Look at Terminal 1. You should see Processing request of type CallToolRequest.
Success: The UI displays live Sector, Products, and Churn Risk data from the MockAPI.

Test 3: Multi-Tool Reasoning (MCP + RAG)
Prompt: "Get details for CUST_0010 and then suggest a retention strategy."
Success: The Agent fetches the profile via MCP (Port 8000) and then automatically triggers the StrategyRetrievalTool to provide an AI-driven plan.

⚠️ Troubleshooting
Error	                            Fix
ADK agent not available	            Ensure services/agent.py uses SseConnectionParams pointing to 
                                    http://127.0.0.1.

Connection Refused	                Check if Terminal 1 is running. Ensure no other app is 
                                    using Port 8000.
Empty Response in UI	            Ensure your async for loop in the chat router is capturing 
                                    event.text (the summary Gemini writes after tool execution).
