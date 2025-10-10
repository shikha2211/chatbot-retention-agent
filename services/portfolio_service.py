from pymongo import MongoClient
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["retention_db"]
collection = db["portfolio_data_actions"]

def get_portfolio_for_user(user_id: str) -> Dict[str, List[Dict]]:
    """ Fetch all customers for a given rmId/userId and categorize by churn risk. """
    
    # Fetch documents where relationshipManager.managerId matches user_id
    documents = collection.find({"relationshipManager.managerId": user_id})
    
    if not documents:
        return {}
    
    # Initialize categories
    categorized = {"High": [], "Medium": [], "Low": []}

    # Categorize documents by risk level
    for doc in documents:
        # CHANGE: Convert ObjectId to string
        doc["_id"] = str(doc["_id"])
        risk_level = doc.get("riskProfile", {}).get("riskLevel", "Unknown")
        categorized.setdefault(risk_level, []).append(doc)

    return categorized