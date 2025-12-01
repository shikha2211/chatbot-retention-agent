import logging
from typing import List

from models import CustomerActionStatus
from services.portfolio_service import collection
from services.autonomous.utils.mappers import action_type_mapper

logger = logging.getLogger(__name__)


class ActionChecker:
    """
    Responsible for checking customer action status from MongoDB portfolio database
    """
    
    async def check_customer_action_status(self, customer_ids: List[str]) -> List[CustomerActionStatus]:
        """
        Check customer action status directly from MongoDB portfolio database
        
        Uses existing portfolio data fields:
        - lastActionTaken
        - lastActionDate
        - nextStepRecommendation
        """
        try:
            logger.info(f"Checking action status for {len(customer_ids)} customers from MongoDB")
            
            # Query MongoDB for customer action history
            customers = list(collection.find(
                {"customerId": {"$in": customer_ids}},
                {
                    "customerId": 1,
                    "lastActionTaken": 1,
                    "lastActionDate": 1,
                    "nextStepRecommendation": 1
                }
            ))
            
            statuses = []
            for customer in customers:
                customer_id = customer.get("customerId")
                last_action_taken = customer.get("lastActionTaken")
                last_action_date = customer.get("lastActionDate")
                
                # Determine action status based on available data
                if last_action_taken and last_action_date:
                    action_status = "completed"
                    # Map action types from existing data
                    action_type = action_type_mapper.map_action_type(last_action_taken)
                else:
                    action_status = "none"
                    action_type = None
                    last_action_date = None
                
                statuses.append(CustomerActionStatus(
                    customerId=customer_id,
                    lastActionDate=last_action_date,
                    lastActionType=action_type,
                    actionStatus=action_status
                ))
            
            # Handle customers not found in database
            found_ids = {status.customerId for status in statuses}
            for customer_id in customer_ids:
                if customer_id not in found_ids:
                    statuses.append(CustomerActionStatus(
                        customerId=customer_id,
                        lastActionDate=None,
                        lastActionType=None,
                        actionStatus="none"
                    ))
            
            logger.info(f"Retrieved action status for {len(statuses)} customers from MongoDB")
            return statuses
            
        except Exception as e:
            logger.error(f"Database error checking customer action status: {str(e)}")
            # For action status errors, we can proceed with safe defaults
            logger.warning("Using default 'none' status for all customers due to database error")
            return [
                CustomerActionStatus(
                    customerId=customer_id,
                    lastActionDate=None,
                    lastActionType=None,
                    actionStatus="none"
                ) for customer_id in customer_ids
            ]


# Singleton instance
action_checker = ActionChecker()