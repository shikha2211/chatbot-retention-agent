# Execution Guide: Customer Retention Agent (v1.25.1)

This project uses a modular architecture where the **AI Agent** lives in the `services/` folder and the **MCP Tools** live in the `customer_mcp_server/` folder. A **Feature Flag** is used to toggle MCP functionality.

---

## 🚀 1. Pre-requisites & Configuration

Before running any component, ensure your environment is set up:

1.  **Activate Environment:** `source .venv/bin/activate`
2.  **Set Python Path:** `export PYTHONPATH=$(pwd)`
3.  **Configure Feature Flag:** Open the `.env` file in the root directory and set:
    *   `FF_MCP_ENABLED=true` (To enable MCP tools like customer_data_by_id)
    *   `FF_MCP_ENABLED=false` (To use only local tools)

> **Note:** If you change the `FF_MCP_ENABLED` value, you **must restart** the ADK or Uvicorn server for the changes to take effect.

---

## 🌐 2. Steps to Run the Tools API (Browser Testing)
This starts the **FastAPI** server on Port 8080 for manual verification of customer data.

1.  **Terminal:** Stay in the project root `chatbot-retention-agent/`.
2.  **Run Command:**
    ```bash
    python -m uvicorn customer_mcp_server.main:app --host 127.0.0.1 --port 8080 --reload
    ```
3.  **Browser Tests (Port 8080):**
    *   **Interactive Docs (Swagger):** [http://127.0.0.1](http://127.0.0.1)
    *   **Customer Lookup:** [http://127.0.0.1](http://127.0.0.1)

---

## 🤖 3. Steps to Run the ADK Agent (AI Chat)
This starts the **Google Agent Development Kit** on Port 8000.

1.  **Terminal:** Open a new tab in the project root `chatbot-retention-agent/`.
2.  **Run Command:**
    ```bash
    adk web .
    ```
3.  **AI Chat Test (Port 8000):**
    *   Open [http://localhost:8000](http://localhost:8000) in your browser.
    *   **Dropdown Selection:** Select **`services`** from the agent dropdown.
    *   **Verify MCP:** Look for the log `🛠️ MCP Mode: Enabled` in your terminal.
    *   **Try asking:** *"Who are my top 3 spenders?"* or *"What is the status of customer CUST_0001?"*

---

## 🛠️ Troubleshooting Checklist

*   **"No root_agent found for 'services'":** Ensure your agent code is in `services/agent.py` and the variable is named exactly `root_agent`.
*   **"Address already in use" (Errno 48):** Run `lsof -ti:8080 | xargs kill -9` to clear the port.
*   **"ModuleNotFoundError":** This usually means the `export PYTHONPATH=$(pwd)` was missed in the current terminal session.
*   **"Attempted to exit cancel scope":** This means `mcp_tools.py` crashed. Ensure `agent.py` has the correct `cwd` and `env: {"PYTHONPATH": ".."}` settings.
*   **MCP Tools not appearing:** Ensure `FF_MCP_ENABLED=true` is set in `.env` and you have restarted the `adk web .` command.

---

## Project Structure
```text
chatbot-retention-agent/
├── .env                # Global configuration & Feature Flags
├── services/           # AI Agent (Auto-loaded by ADK)
│   └── agent.py        # Main Agent logic
└── customer_mcp_server/# Tool Provider (Shared by API and Agent)
    ├── main.py         # Entry point for Browser API
    ├── mcp_tools.py    # Entry point for ADK Stdio
    └── mcp_functions.py# Core data logic
