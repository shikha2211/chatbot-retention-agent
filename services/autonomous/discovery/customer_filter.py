from datetime import datetime
from typing import List, Dict

from models import CustomerActionStatus, AutonomousAction
from services.autonomous_config import autonomous_config


class CustomerFilter:
    """
    Responsible for filtering customers that need action and applying batch limits
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    def filter_unactioned_customers(self, customers: List[Dict], action_statuses: List[CustomerActionStatus]) -> List[Dict]:
        """
        Filter customers that need action (no recent action or action > staleness period)
        """
        # Create lookup for action statuses
        status_lookup = {status.customerId: status for status in action_statuses}
        
        unactioned = []
        for customer in customers:
            customer_id = customer.get("customerId")
            status = status_lookup.get(customer_id)
            
            needs_action = False
            if not status or status.actionStatus == "none":
                needs_action = True
            elif status.lastActionDate:
                # Check if last action was stale based on configured staleness period
                last_action = datetime.fromisoformat(status.lastActionDate.replace('Z', '+00:00'))
                days_since_action = (datetime.now() - last_action.replace(tzinfo=None)).days
                if days_since_action > self.config.action_staleness_days:
                    needs_action = True
            
            if needs_action:
                unactioned.append(customer)
        
        return unactioned
    
    def apply_batch_limits(self, customers: List[Dict]) -> tuple[List[Dict], List[AutonomousAction]]:
        """
        Apply batch size limits and create filtered actions for customers over the limit
        
        Returns:
            tuple: (customers_to_process, filtered_actions)
        """
        filtered_actions = []
        
        if len(customers) > self.config.max_customers_per_batch:
            # Create actions for filtered customers
            filtered_customers = customers[self.config.max_customers_per_batch:]
            for i, customer in enumerate(filtered_customers):
                filtered_action = AutonomousAction(
                    customerId=customer.get("customerId", "unknown"),
                    strategyId="BATCH_LIMIT",
                    strategyName="Filtered due to batch size limit",
                    actionType="system",
                    priority=999,  # Lowest priority
                    estimatedImpact=0.0,
                    status="filtered",
                    executionDetails={
                        "timestamp": datetime.now().isoformat(),
                        "reason": "batch_size_limit",
                        "batch_limit": self.config.max_customers_per_batch,
                        "customer_position": self.config.max_customers_per_batch + i + 1
                    }
                )
                filtered_actions.append(filtered_action)
            
            customers_to_process = customers[:self.config.max_customers_per_batch]
        else:
            customers_to_process = customers
            
        return customers_to_process, filtered_actions


# Singleton instance
customer_filter = CustomerFilter()