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

if MONGO_URI is None or "localhost" in MONGO_URI:
    MONGO_URI="mongodb+srv://admin:retention-db-connect@retention-agent-db.xz7rajn.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client["retention_db"]
collection = db["portfolio_data_actions"]

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
            # Watch for changes in the portfolio_data_actions collection
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
                        
                        if operation_type == 'delete':
                            # For delete operations, get rmId from fullDocumentBeforeChange
                            if 'fullDocumentBeforeChange' in change and change['fullDocumentBeforeChange']:
                                rm_id = change['fullDocumentBeforeChange'].get('rmId')
                            else:
                                logger.warning("Could not get rmId from deleted document, checking all active connections")
                                for active_rm_id in list(self.active_connections.keys()):
                                    updated_portfolio = get_portfolio_for_user(active_rm_id)
                                    if updated_portfolio:
                                        asyncio.run(self.send_portfolio_update(active_rm_id, updated_portfolio))
                                    else:
                                        # Send empty portfolio if all data was cleared
                                        empty_portfolio = {"High": [], "Medium": [], "Low": []}
                                        asyncio.run(self.send_portfolio_update(active_rm_id, empty_portfolio))
                                continue
                        elif 'fullDocument' in change and change['fullDocument']:
                            rm_id = change['fullDocument'].get('rmId')
                        
                        logger.info(f"Change for rmId: {rm_id}, Active connections: {list(self.active_connections.keys())}")
                        
                        if rm_id and rm_id in self.active_connections:
                            # Fetch updated portfolio data and send to connected clients
                            updated_portfolio = get_portfolio_for_user(rm_id)
                            if updated_portfolio:
                                logger.info(f"Sending portfolio update to {rm_id}")
                                # Use asyncio to run the async function in the thread
                                asyncio.run(self.send_portfolio_update(rm_id, updated_portfolio))
                            else:
                                # Send empty portfolio when data is cleared
                                logger.info(f"Sending empty portfolio update to {rm_id}")
                                empty_portfolio = {"High": [], "Medium": [], "Low": []}
                                asyncio.run(self.send_portfolio_update(rm_id, empty_portfolio))
                        elif rm_id:
                            logger.info(f"No active connections for rmId: {rm_id}")
                                
        except Exception as e:
            logger.error(f"Error in change stream: {e}")
            self.change_stream_active = False

def get_portfolio_for_user(user_id: str) -> Dict[str, list]:
    """ Fetch all customers for a given rmId/userId and categorize by churn risk. """

    documents = list(collection.find({"relationshipManager.managerId": user_id}))
    print("Documents-----------:")
    for doc in documents:
        print(doc)

    if not documents:
        return {}
    
    categorized = {"High": [], "Medium": [], "Low": []}

    for doc in documents:
        risk_profile = doc.get("riskProfile", {})
        risk = risk_profile.get("riskLevel", "Unknown")
        
        # Find the action that matches lastActionId
        last_action = {}
        last_action_id = doc.get("lastActionId")
        if last_action_id and "actions" in doc:
            last_action = next(
                (action for action in doc["actions"] if action.get("actionId") == last_action_id),
                {}
            )
        
        item = {
            "customerId": doc.get("customerId"),
            "name": doc.get("customerName"),
            "lastAction": {
                "actionId": last_action_id,
                "actionType": last_action.get("actionType"),
                "details": last_action.get("actionDetails", {}),
                "status": last_action.get("status"),
                "outcome": last_action.get("outcome"),
                "takenOn": last_action.get("takenOn"),
                "takenBy": last_action.get("takenBy")
            },
            "lastActionDate": doc.get("lastActionTakenOn"),
            # "nextRecommendedStep": doc.get("nextStepRecommendation")
        }
        categorized.setdefault(risk, []).append(item)

    return categorized


# added this for testing the portfolio websocket to add new portfolio entries
# [TODO] can be removed later.
def create_portfolio_entry(portfolio_data: dict) -> dict:
    """Create a new portfolio entry in MongoDB."""
    try:
        # print("\n=== New Portfolio Entry ===")
        # print("Portfolio Data:", portfolio_data)
        
        # Print all documents in the collection
        all_docs = list(collection.find({}))
        print(f"\n=== Collection Contents ({len(all_docs)} documents) ===")
        for i, doc in enumerate(all_docs, 1):
            print(f"\nDocument {i}:")
            for key, value in doc.items():
                print(f"  {key}: {value}")
        print("\n" + "="*50 + "\n")
        
        # Check if customer ID already exists for this RM
        existing = collection.find_one({
            "customerId": portfolio_data.get("customerId"),
            "rmId": portfolio_data.get("relationshipManager.managerId")
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


def clear_portfolio_data(rmId: str) -> dict:
    """Clear all portfolio data from MongoDB"""
    try:
        result = collection.delete_many({"rmId": rmId})
        logger.info(f"Cleared portfolio collection. Deleted {result.deleted_count} documents")
        return {
            "success": True,
            "message": f"Portfolio data cleared successfully. Deleted {result.deleted_count} documents"
        }
    except Exception as e:
        logger.error(f"Error clearing portfolio data: {e}")
        return {
            "success": False,
            "message": f"Error clearing portfolio data: {str(e)}"
        }