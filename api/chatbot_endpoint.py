from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ADK components
try:
    from services.agent import runner, session_service
    from google.genai import types

    ADK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ADK agent not available: {e}")
    runner = None
    session_service = None
    types = None
    ADK_AVAILABLE = False

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat queries"""

    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat queries"""

    response: str
    session_id: str
    customer_id: Optional[str] = None
    status: str = "success"


class SessionInfo(BaseModel):
    """Session information model"""

    session_id: str
    user_id: str
    messages_count: int
    created_at: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the ADK retention agent.

    This endpoint exposes the Google ADK agent as a REST API for chatbot integration.
    """
    try:
        
        print(f"\n\n=>Received new request for POST/api/chat message is : {request.message} , sessionID : {request.session_id}, userId : {request.user_id}")
        
        
        if not ADK_AVAILABLE or not runner or not session_service or not types:
            # Fallback response when ADK is not available
            return ChatResponse(
                response=f"I received your message: '{request.message}'. However, the ADK agent is not fully initialized. Please check the server logs for more details.",
                session_id=request.session_id or "default-session",
                customer_id=request.customer_id,
                status="warning",
            )

        # Use provided session_id or create a default one
        session_id = request.session_id or "default-session"
        user_id = request.user_id or "default-user"
        app_name = "Retention_Agent"

        # Get or create session using ADK's session service
        print(f"\n\n=>Get exissting session_service.get_session session_id: {session_id}, user_id: {user_id}, app_name: {app_name}");
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        print(f"\n Check existing session : {'existing session present' if session else 'no existing session'}")
        
        if not session:
            print(f"\n No existing session creating new")
            session = await session_service.create_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

        # Prepare the message for the agent
        message_content = request.message
        if request.customer_id:
            message_content += f" Customer ID: {request.customer_id}"

        # Create the message content using Google GenAI types
        new_message = types.Content(
            role='user',
            parts=[types.Part(text=message_content)]
        )

        print(f"\nExecuting Agent now with user_id: {user_id} , sessionId : {session_id} and message: {new_message} ")
        
        # Run the ADK agent
        # =================
        response_events = list(
            runner.run(user_id=user_id, session_id=session_id, new_message=new_message)
        )

        # Extract the response from the events
        response_text = ""
        for event in response_events:
            # print(f'\n ===> response event from agent {event}')
            if hasattr(event, "content") and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and isinstance(part.text, str) :
                        response_text += part.text

        if not response_text:
            response_text = "I received your message but couldn't generate a response."

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            customer_id=request.customer_id,
        )

    except Exception as e:
        logging.error(f"Error in chat query: {str(e)}")
        return ChatResponse(
            response=f"Error processing your request: {str(e)}",
            session_id=request.session_id or "error-session",
            customer_id=request.customer_id,
            status="error",
        )

@router.get("/chat/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a specific session"""

    print(f"\n==>Getting session using session_id: {session_id}")
    try:
        if not ADK_AVAILABLE or not session_service:
            raise HTTPException(status_code=503, detail="Session service not initialized")
            
        session = await session_service.get_session(
            app_name="Retention_Agent",
            user_id="default-user",
            session_id=session_id
        )
        if not session:
            print(f"\n==>GET SESS Session Not found for session_id: {session_id}")

            raise HTTPException(status_code=404, detail="GET Session not found")
        
        return SessionInfo(
            session_id=session_id,
            user_id=getattr(session, 'user_id', 'unknown'),
            messages_count=len(getattr(session, 'messages', [])),
            created_at=getattr(session, 'created_at', None)
        )
    except Exception as e:
        logging.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")




@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    
    print(f"\n==>Delete session using session_id: {session_id}")

    try:
        if not ADK_AVAILABLE or not session_service:
            raise HTTPException(
                status_code=503, detail="Session service not initialized"
            )

        session = await session_service.get_session(
            app_name="Retention_Agent", user_id="default-user", session_id=session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="DELETE Session not found")

        await session_service.delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/chat/health")
async def health_check():
    """Health check endpoint for the chat service"""
    try:
        if not ADK_AVAILABLE:
            return {
                "status": "unhealthy",
                "agent": "not_available",
                "session_service": "not_available",
                "runner": "not_available",
                "message": "ADK agent module not found",
            }

        if not runner or not session_service or not types:
            return {
                "status": "unhealthy",
                "agent": "not_initialized",
                "session_service": "not_initialized",
                "runner": "not_initialized",
                "message": "ADK components not properly initialized",
            }

        # Test if the agent runner is working
        test_session = await session_service.create_session(
            app_name="Retention_Agent",
            user_id="health-check",
            session_id="health-check-session",
        )

        return {
            "status": "healthy",
            "agent": "retention_agent",
            "session_service": "active",
            "runner": "ready",
            "message": "All ADK components are working",
        }
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "agent": "error",
            "session_service": "error",
            "runner": "error",
            "message": f"Health check failed: {str(e)}",
        }
