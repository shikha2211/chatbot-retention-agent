import logging
from typing import List, Dict, Optional

from services.autonomous_config import autonomous_config
from tools import AllCustomersDataTool

logger = logging.getLogger(__name__)


class CustomerFinder:
    """
    Responsible for discovering at-risk customers from MongoDB portfolio data
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    async def discover_at_risk_customers(self, rm_id: Optional[str]) -> List[Dict]:
        """
        Get all customers on risk using Customer API, filtered by risk level and optional RM
        """
        try:
            # Get all customers from Customer API
            all_customers_data = await AllCustomersDataTool()
            
            # Handle both list and dict responses from API
            if isinstance(all_customers_data, list):
                all_customers = all_customers_data
            elif isinstance(all_customers_data, dict) and "customers" in all_customers_data:
                all_customers = all_customers_data["customers"]
            elif isinstance(all_customers_data, dict):
                # If it's a single customer object, wrap in list
                all_customers = [all_customers_data]
            else:
                logger.warning("Unexpected response format from Customer API")
                return []
            
            # Filter for at-risk customers using configured risk categories
            # Filter out 'Low' risk from configured categories for at-risk customer discovery
            at_risk_categories = [cat for cat in self.config.risk_categories if cat != "Low"]
            
            at_risk_customers = []
            for customer in all_customers:
                # Check if customer has risk category field (multiple possible field names)
                risk_category = (customer.get("churnRiskCategory") or 
                               customer.get("riskCategory") or 
                               customer.get("risk_category") or 
                               customer.get("churn_risk"))
                
                if risk_category in at_risk_categories:
                    # Filter by RM if specified
                    if rm_id:
                        customer_rm = (customer.get("rmId") or 
                                     customer.get("rm_id") or 
                                     customer.get("relationshipManagerId"))
                        if customer_rm == rm_id:
                            at_risk_customers.append(customer)
                    else:
                        at_risk_customers.append(customer)
            
            logger.info(f"Retrieved {len(at_risk_customers)} at-risk customers from Customer API")
            return at_risk_customers
            
        except Exception as e:
            logger.error(f"Customer API error discovering at-risk customers: {str(e)}")
            # For API errors, we cannot proceed safely
            raise RuntimeError(f"Failed to discover at-risk customers: {str(e)}") from e


# Singleton instance
customer_finder = CustomerFinder()