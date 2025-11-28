from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Response
from services.portfolio_service import get_portfolio_for_user, PortfolioWebSocketManager
from models import ClearPortfolioRequest
import json

router = APIRouter()

# Create a global WebSocket manager instance
websocket_manager = PortfolioWebSocketManager()

@router.get("/portfolio/{user_id}")
def fetch_portfolio(user_id: str):
    portfolio = get_portfolio_for_user(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found for this user.")
    return {"customer_ids": portfolio}

@router.websocket("/portfolio/ws/{user_id}")
async def portfolio_websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        # Send initial portfolio data
        initial_portfolio = get_portfolio_for_user(user_id)
        if initial_portfolio:
            await websocket.send_text(json.dumps({
                "type": "initial_data",
                "data": {"customer_ids": initial_portfolio}
            }))
        
        # Keep connection alive and handle any client messages
        while True:
            try:
                # Wait for any message from client (like ping/pong)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in WebSocket communication: {e}")
                break
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket, user_id)

# added this for testing the portfolio websocket, cam be removed later.
@router.post("/portfolio", status_code=201)
def create_portfolio(portfolio_request: dict):
    """Create a new portfolio entry for a customer"""
    from services.portfolio_service import create_portfolio_entry
    
    result = create_portfolio_entry(portfolio_request)
    
    if not result.get("success"):
        if "already exists" in result.get("message", ""):
            raise HTTPException(status_code=409, detail=result.get("message"))
        else:
            raise HTTPException(status_code=500, detail=result.get("message"))
    
    return result

@router.post("/clearData")
def clear_portfolio(request: ClearPortfolioRequest):
    """Clear portfolio data for a specific RM/user from MongoDB.
    
    Request body should contain: {"rmId": "shipra123"}
    Usage: POST /api/clearData with body {"rmId": "shipra123"}
    """
    from services.portfolio_service import clear_portfolio_data
    result = clear_portfolio_data(request.rmId)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))
    return Response(status_code=204)