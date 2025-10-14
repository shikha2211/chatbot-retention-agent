from pymongo import MongoClient
from typing import Dict, List
import os
from dotenv import load_dotenv
from fastapi import WebSocket
import json
import asyncio
from threading import Thread
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

print(f'====> MONGO_URI is : {MONGO_URI}')

if MONGO_URI is None or "localhost" in MONGO_URI:
    MONGO_URI="mongodb+srv://admin:retention-db-connect@retention-agent-db.xz7rajn.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client["retention_db"]
collection = db["portfolio_data"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioWebSocketManager:
    def __init__(self):
        # Dictionary to store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # manages mongo db change stream life cycle
        self.change_stream_active = False   
        self.change_stream_thread = None
        
    async def connect(self, websocket: WebSocket, user_id: str):
        # accept the websocket connection
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user: {user_id}")
        
        # Start change stream if not already active
        if not self.change_stream_active:
            self.start_change_stream()
            
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user: {user_id}")
        
        # Stop change stream if no active connections
        if not self.active_connections and self.change_stream_active:
            self.stop_change_stream()
            
    async def send_portfolio_update(self, user_id: str, portfolio_data: dict):
        if user_id in self.active_connections:
            message = json.dumps({
                "type": "portfolio_update",
                "data": {"customer_ids": portfolio_data}
            })
            
            # Send to all connections for this user
            disconnected_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message to WebSocket: {e}")
                    disconnected_connections.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected_connections:
                self.disconnect(conn, user_id)
                
    def start_change_stream(self):
        # start background thread to monitor db changes
        if not self.change_stream_active:
            self.change_stream_active = True
            self.change_stream_thread = Thread(target=self._watch_changes, daemon=True)
            self.change_stream_thread.start()
            logger.info("Started MongoDB change stream")
            
    def stop_change_stream(self):
        self.change_stream_active = False
        if self.change_stream_thread:
            self.change_stream_thread.join(timeout=1)
        logger.info("Stopped MongoDB change stream")
        
    def _watch_changes(self):
        try:
            # Watch for changes in the portfolio_data collection
            with collection.watch() as stream:
                for change in stream:
                    if not self.change_stream_active:
                        break
                        
                    # Process the change
                    operation_type = change['operationType']
                    logger.info(f"Change stream detected: {operation_type}")
                    
                    if operation_type in ['insert', 'update', 'replace', 'delete']:
                        # Get the rmId from the changed document
                        rm_id = None
                        
                        if 'fullDocument' in change and change['fullDocument']:
                            rm_id = change['fullDocument'].get('rmId')
                        elif 'documentKey' in change:
                            # For delete operations, try to get rmId from the document
                            doc_id = change['documentKey']['_id']
                            try:
                                doc = collection.find_one({"_id": doc_id})
                                if doc:
                                    rm_id = doc.get('rmId')
                            except Exception as e:
                                logger.error(f"Error fetching document for rmId: {e}")
                        
                        logger.info(f"Change for rmId: {rm_id}, Active connections: {list(self.active_connections.keys())}")
                        
                        if rm_id and rm_id in self.active_connections:
                            # Fetch updated portfolio data and send to connected clients
                            updated_portfolio = get_portfolio_for_user(rm_id)
                            if updated_portfolio:
                                logger.info(f"Sending portfolio update to {rm_id}")
                                # Use asyncio to run the async function in the thread
                                asyncio.run(self.send_portfolio_update(rm_id, updated_portfolio))
                            else:
                                logger.warning(f"No portfolio data found for {rm_id}")
                        else:
                            logger.info(f"No active connections for rmId: {rm_id}")
                                
        except Exception as e:
            logger.error(f"Error in change stream: {e}")
            self.change_stream_active = False

def get_portfolio_for_user(user_id: str) -> Dict[str, list]:
    """ Fetch all customers for a given rmId/userId and categorize by churn risk. """

    documents = collection.find({"rmId": user_id})

    if not documents:
        return {}
    
    categorized = {"High": [], "Medium": [], "Low": []}

    for doc in documents:
        risk = doc.get("churnRiskCategory", "Unknown")
        item = {
            "customerId": doc.get("customerId"),
            "name": doc.get("name"),
            "lastActionTaken": doc.get("lastActionTaken"),
            "lastActionDate": doc.get("lastActionDate"),
            "nextRecommendedStep": doc.get("nextStepRecommendation")
        }
        categorized.setdefault(risk, []).append(item)

    return categorized


# added this for testing the portfolio websocket to add new portfolio entries
# [TODO] can be removed later.
def create_portfolio_entry(portfolio_data: dict) -> dict:
    """Create a new portfolio entry in MongoDB."""
    try:
        # Check if customer ID already exists for this RM
        existing = collection.find_one({
            "customerId": portfolio_data.get("customerId"),
            "rmId": portfolio_data.get("rmId")
        })
        
        if existing:
            return {
                "success": False,
                "message": f"Portfolio entry already exists for customer {portfolio_data.get('customerId')}",
                "customerId": portfolio_data.get("customerId")
            }
        
        # Insert the new portfolio entry
        result = collection.insert_one(portfolio_data)
        
        if result.inserted_id:
            logger.info(f"Created portfolio entry for customer: {portfolio_data.get('customerId')}")
            return {
                "success": True,
                "message": "Portfolio entry created successfully",
                "customerId": portfolio_data.get("customerId")
            }
        else:
            return {
                "success": False,
                "message": "Failed to create portfolio entry"
            }
            
    except Exception as e:
        logger.error(f"Error creating portfolio entry: {e}")
        return {
            "success": False,
            "message": f"Error creating portfolio entry: {str(e)}"
        }
