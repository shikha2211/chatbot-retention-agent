from pymongo import MongoClient
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI =  os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["retention_db"]
collection = db["portfolio_data"]


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