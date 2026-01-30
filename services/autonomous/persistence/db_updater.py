import logging
from datetime import datetime
from typing import List

from models import AutonomousAction
from services.portfolio_service import collection

logger = logging.getLogger(__name__)


class DatabaseUpdater:
    """
    Responsible for updating MongoDB with executed actions
    """
    
    async def update_action_records(self, actions: List[AutonomousAction]):
        """
        Update MongoDB with executed actions
        """
        try:
            for action in actions:
                # Update portfolio collection with last action
                collection.update_one(
                    {"customerId": action.customerId},
                    {
                        "$set": {
                            "lastActionTaken": action.strategyName,
                            "lastActionDate": datetime.now().isoformat(),
                            "nextStepRecommendation": "Monitor customer response"
                        }
                    }
                )
            
            logger.info(f"Updated {len(actions)} customer action records in MongoDB")
            
        except Exception as e:
            logger.error(f"Database error updating action records: {str(e)}")
            # Database update failures are serious - log but don't crash the workflow
            logger.warning("Action execution completed but database updates failed")


# Singleton instance
db_updater = DatabaseUpdater()