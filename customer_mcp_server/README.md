# Execution Guide: Customer Retention Agent (v1.25.1)

Follow these steps to run and test each component. Separate files are used for Browser testing (HTTP) and AI Agent testing (Stdio) to ensure stability.

---

## 1. Steps to Run the Tools API (For Browser Testing)
This starts the **FastAPI** server, allowing you to hit endpoints directly in your browser or via Swagger docs.

1.  Open a terminal and navigate to the project root: `chatbot-retention-agent/`.
2.  Activate your environment: `source .venv/bin/activate`.
3.  Set the Python Path: `export PYTHONPATH=$(pwd)`.
4.  Run the command:
    ```bash
    python -m uvicorn customer_mcp_server.main:app --host 127.0.0.1 --port 8080 --reload
    ```
5.  **Verification:** The terminal should show `Uvicorn running on http://127.0.0.1:8080`.
6.  **Browser Tests:**
    *   **Interactive Docs (Swagger):** [http://127.0.0.1](http://127.0.0.1)
    *   **Customer Lookup:** [http://127.0.0.1](http://127.0.0.1)
    *   **Health Check:** [http://127.0.0.1](http://127.0.0.1)

---

## 2. Steps to Run the ADK Agent (For AI Chat)
This starts the **Google Agent Development Kit** interface. The agent uses `mcp_tools.py` via **Stdio** (Standard Input/Output), so no separate port is needed for the tools logic.

1.  Open a **new** terminal window and navigate to the project root: `chatbot-retention-agent/`.
2.  Activate your environment: `source .venv/bin/activate`.
3.  Run the command:
    ```bash
    adk web .
    ```
4.  **Verification:** The terminal will show `ADK Web Server started at http://localhost:8000`.
5.  **AI Chat Test:**
    *   Open [http://localhost:8000](http://localhost:8000) in your browser.
    *   Select **customer_retention_agent** from the dropdown.
    *   **Try asking:** *"Who are my top spenders?"* or *"What is the status of customer CUST_0008?"*

---

## Troubleshooting Checklist

*   **Address already in use:** If you see `Errno 48`, run `lsof -ti:8080 | xargs kill -9` to clear the port.
*   **ModuleNotFoundError:** Ensure you ran `export PYTHONPATH=$(pwd)` in the terminal where you are running `uvicorn`.
*   **Cancel Scope Error in ADK:** This usually means a crash in `mcp_tools.py`. Ensure your `agent.py` includes `"env": {"PYTHONPATH": ".."}` in the `StdioConnectionParams` to handle absolute imports.
*   **Not Found (404):** In the browser, ensure you are hitting port **8080**. For the Agent UI, ensure you are hitting port **8000**.

---
