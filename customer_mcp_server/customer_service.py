import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Any, Dict
import re
from mcp_functions import McpFetchCustomerInfo

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_customer_id_from_text(text: str) -> str:
    """
    Extract customer ID from natural language text using OpenAI.
    Falls back to regex pattern matching if OpenAI extraction fails.
    
    Args:
        text: Natural language text containing customer ID enquiry
        
    Returns:
        Extracted customer ID or empty string if not found
    """
    try:
        # Try LLM extraction first
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts customer IDs from text. Extract the customer ID from the following text and return only the customer ID, nothing else. If no customer ID is found, return 'NOT_FOUND'."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        customer_id = response.choices[0].message.content.strip()
        if customer_id and customer_id != "NOT_FOUND":
            print(f"\n\n===>Extracted customer ID via LLM: {customer_id}")
            return customer_id
            
    except Exception as e:
        print(f"\n\n===>LLM extraction failed: {e}. Falling back to regex...")

    # Regex fallback: Look for common customer ID patterns (CUST_XXXX, ID:XXXX, etc.)
    patterns = [
        r'CUST[_-]?\d{4,}',  # CUST_0008, CUST-0008, CUST0008
        r'customer\s*(?:id|ID)[\s:=]+([A-Za-z0-9_-]+)',  # customer ID: CUST_0008
        r'ID[\s:=]+([A-Za-z0-9_-]+)',  # ID: CUST_0008
        r'customer\s*(?:number|id)\s+([A-Za-z0-9_-]+)',  # customer id 0008
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_id = match.group(0) if match.lastindex is None else match.group(1)
            print(f"\n\n===>Extracted customer ID via regex: {extracted_id}")
            return extracted_id
    
    print(f"\n\n===>Could not extract customer ID from text: {text}")
    return ""


async def customer_data_wrapper(text: str) -> Dict[str, Any]:
    """
    Wrapper function that accepts natural language text enquiring about a customer,
    extracts the customer ID, and fetches customer data via MCP client.
    
    Args:
        text: Natural language text containing customer ID enquiry (e.g., "Tell me about customer CUST_0008")
        
    Returns:
        Customer data dictionary or error dict
    """
    try:
        print(f'\n\n===>inside customer_data_wrapper with text: {text}')
        
        # Extract customer ID from text
        customer_id = extract_customer_id_from_text(text)
        
        if not customer_id:
            return {"error": "Could not extract customer ID from the provided text"}
        
        # Fetch customer data via MCP client
        return await McpFetchCustomerInfo(customer_id)
        
    except Exception as e:
        print(f"\n\n===>ERROR: Error in customer_data_wrapper: {str(e)}")
        return {"error": f"Error processing request: {str(e)}"}
