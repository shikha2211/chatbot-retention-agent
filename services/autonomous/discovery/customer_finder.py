import logging
from typing import List, Dict, Optional

from services.portfolio_service import collection
from services.autonomous_config import autonomous_config

logger = logging.getLogger(__name__)


class CustomerFinder:
    """
    Responsible for discovering at-risk customers from MongoDB portfolio data
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    async def discover_at_risk_customers(self, rm_id: Optional[str]) -> List[Dict]:
        """
        Get all customers on risk from MongoDB portfolio data
        """
        try:
            # Query MongoDB for at-risk customers using configured risk categories
            # Filter out 'Low' risk from configured categories for at-risk customer discovery
            at_risk_categories = [cat for cat in self.config.risk_categories if cat != "Low"]
            query = {
                "churnRiskCategory": {"$in": at_risk_categories}
            }
            
            # Filter by RM if specified
            if rm_id:
                query["rmId"] = rm_id
                
            customers = list(collection.find(query))
            logger.info(f"Retrieved {len(customers)} at-risk customers from MongoDB")
            
            return customers
            
        except Exception as e:
            logger.error(f"Database error discovering at-risk customers: {str(e)}")
            # For database errors, we cannot proceed safely
            raise RuntimeError(f"Failed to discover at-risk customers: {str(e)}") from e


# Singleton instance
customer_finder = CustomerFinder()