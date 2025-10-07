# tools.py (apps/llm/src/app/adk/tools.py)
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv  # Import load_dotenv
from typing import Any, Dict
from google.adk.tools import google_search
from models import  CustomerProfile
from services.query_zilliz_milvus_service import query_zilliz_milvus_service

load_dotenv()  # Load environment variables

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CUSTOMER_API_URL = os.getenv('CUSTOMER_API_URL')
RAG_API_URL = os.getenv('RAG_API_URL')
print(f'CUSTOMER_API_UR {CUSTOMER_API_URL}')
print(f'RAG_API_URL {RAG_API_URL}')

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
                results = query_zilliz_milvus_service(customerData)
                return results
        
        except Exception as e:
                print(f"\n\n===>ERROR: Error while RAG call for strategies: {str(e)}")
                # Return a fallback response instead of None
                return {"error": f"Service unavailable: {str(e)}", "strategies": []}
