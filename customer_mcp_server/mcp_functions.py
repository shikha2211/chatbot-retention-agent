import requests
import os
import logging
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_API_URL = os.getenv('CUSTOMER_API_URL')

async def McpFetchCustomerInfo(customer_id: str) -> Dict[str, Any]:
    """
    Fetch customer info directly from the customer API.
    This avoids circular dependency by directly calling the API
    instead of routing through the MCP HTTP endpoint.
    """
    try:
        print(f'\n\n===>inside McpFetchCustomerInfo customerId is: {customer_id}')
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
        logging.error(f"Error fetching customer data: {e}")
        return {}


async def McpHealthCheckTool() -> Dict[str, Any]:
    """
    Health check for MCP service.
    """
    try:
        return {"status": "healthy"}
    except Exception as e:
        logging.error(f"Error calling MCP health check: {e}")
        return {"status": "unhealthy", "error": str(e)}
