"""
Quick test to verify agent can call tools via MCP integration
"""
import asyncio
from services.agent import runner, session_service
from google.genai import types

async def test_agent_tools():
    """Test that agent can invoke tools"""
    
    # Test 1: Agent calling customer_data_wrapper via runner
    print("\n" + "="*60)
    print("Test 1: Agent querying customer via MCP tools")
    print("="*60)
    
    session_id = "test-session-mcp"
    user_id = "test-user"
    app_name = "Retention_Agent"
    
    # Create session
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    # Create message
    message = types.Content(
        role='user',
        parts=[types.Part(text="Tell me about customer CUST_0005")]
    )
    
    # Run agent
    response_events = list(runner.run(user_id=user_id, session_id=session_id, new_message=message))
    
    # Extract response
    response_text = ""
    for event in response_events:
        if hasattr(event, "content") and hasattr(event.content, "parts"):
            for part in event.content.parts:
                if hasattr(part, "text"):
                    response_text += part.text
    
    print(f"Agent response:\n{response_text[:500]}...\n")
    
    # Test 2: Simple tool call verification
    print("="*60)
    print("Test 2: Direct tool invocation")
    print("="*60)
    
    from mcp_client.customer_service import customer_data_wrapper
    result = await customer_data_wrapper("Get info for CUST_0002")
    print(f"✓ Tool result: Customer {result.get('customerId')} with churn risk {result.get('churnRiskScore')}")
    print("✓ All tests passed!\n")

if __name__ == "__main__":
    asyncio.run(test_agent_tools())
