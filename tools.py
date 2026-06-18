# tools.py (apps/llm/src/app/adk/tools.py)
import requests
import os
from openai import OpenAI, api_key
from dotenv import load_dotenv  # Import load_dotenv
from typing import Any, Dict
from google.adk.tools import google_search
from models import CustomerProfile
from services.query_zilliz_milvus_service import query_zilliz_milvus_service

load_dotenv()  # Load environment variables

# Extract the key safely into a standalone variable
openai_key_string = os.getenv("OPENAI_API_KEY")

# Pass it to your client constructor
client = OpenAI(api_key=openai_key_string)

print("OPENAI_API_KEY in tools.py present:", bool(openai_key_string))

CUSTOMER_API_URL = os.getenv('CUSTOMER_API_URL')
RAG_API_URL = os.getenv('RAG_API_URL')
IMPLEMENTATION_AGENT_URL = os.getenv('IMPLEMENTATION_AGENT_URL', '').rstrip('/')

async def CustomerDataTool(customer_id: str) -> Dict[str, Any]:
        """Fetches customer details"""
        try:
                print(f'\n\n===>inside CustomerDataTool customerId is: {customer_id}')
                url = f"{CUSTOMER_API_URL}/{customer_id}"
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad responses
                jsonoutput = response.json()
        
                if isinstance(jsonoutput, dict):
                        print(f'\n\n===>Customer details for customerId is: {customer_id} is {jsonoutput}')
                        return jsonoutput
                else:
                        print(f"\n\n===>ERROR: Unexpected response format for customerId: {customer_id}")
                        return {}
        except requests.exceptions.RequestException as e:
                print(f"\n\n===>ERROR: Error fetching customer details: {e}")
                return {}


async def AllCustomersDataTool() -> Dict[str, Any]:
        """Fetches all customers data when no specific customer_id is provided"""
        try:
                print(f'\n\n===>inside AllCustomersDataTool - fetching all customers')
                url = f"{CUSTOMER_API_URL}"  # No customer_id appended
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad responses
                jsonoutput = response.json()
        
                if isinstance(jsonoutput, (list, dict)):
                        print(f'\n\n===>All customers data retrieved successfully - count: {len(jsonoutput) if isinstance(jsonoutput, list) else "unknown"}')
                        return jsonoutput
                else:
                        print(f"\n\n===>ERROR: Unexpected response format for all customers")
                        return {}
        except requests.exceptions.RequestException as e:
                print(f"\n\n===>ERROR: Error fetching all customers data: {e}")
                return {}


async def StrategyRetrievalToolBackup(customerData: CustomerProfile) -> dict:
        """Retrieves RAG-based strategies"""
        try:
                print(f'\n\n===>inside StrategyRetrievalTool context is: {customerData}')
                response = requests.post(f"{RAG_API_URL}",json = customerData)
                print("\n\n===>StrategyRetrievalTool:Status Code:", response.status_code)
                print("\n\n===>StrategyRetrievalTool:Response JSON:", response.json())
                return response.json()
        except requests.exceptions.RequestException as e:
                print(f"\n\n===>ERROR : Error while RAG call for strategies : {e}")
                return None


async def StrategyRetrievalTool(customerData: CustomerProfile) -> dict:
        """Retrieves RAG-based strategies"""
        try:
                print(f'\n\n===>inside new StrategyRetrievalTool context is: {customerData}')
                # FIX: Check if it's a Pydantic model or already a dict
                if hasattr(customerData, 'model_dump'):
                     customer_dict = customerData.model_dump()
                elif isinstance(customerData, dict):
                     customer_dict = customerData
                else:
                     # Fallback if it's some other type
                     customer_dict = dict(customerData)
                 # Now pass the clean dictionary to Milvus service     
                results = query_zilliz_milvus_service(customer_dict)
                return results
        
        except Exception as e:
                print(f"\n\n===>ERROR: Error while RAG call for strategies: {str(e)}")
                # Return a fallback response instead of None
                return {"error": f"Service unavailable: {str(e)}", "strategies": []}

def health_check_tool() -> dict:
    return {"status": "healthy"}
# [TODO:] remove later
async def ImplementStrategyTool(
    customer_id: str,
    retention_strategy_id: str,
    rm_id: str = "",
    strategy_name: str = "",
) -> Dict[str, Any]:
    """Calls the Implementation Agent with customerId, retentionStrategyId, and rmId."""
    customer_id = (customer_id or "").strip().upper()
    retention_strategy_id = (retention_strategy_id or "").strip().upper()
    rm_id = (rm_id or "").strip().upper()

    print(f"\n\n===>ImplementStrategyTool: customer={customer_id}, strategy={retention_strategy_id}, rm={rm_id}, name={strategy_name}")

    if not IMPLEMENTATION_AGENT_URL:
        print("\n\n===>ImplementStrategyTool: IMPLEMENTATION_AGENT_URL not set, skipping call")
        return {"status": "success", "message": f"Strategy {retention_strategy_id} queued for customer {customer_id} (impl agent not configured)."}

    payload = {
        "customerId": customer_id,
        "retentionStrategyId": retention_strategy_id,
        "rmId": rm_id,
        "strategyName": strategy_name or None,
    }
    try:
        resp = requests.post(IMPLEMENTATION_AGENT_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"\n\n===>ERROR: ImplementStrategyTool call failed: {e}")
        return {"status": "error", "message": str(e)}
