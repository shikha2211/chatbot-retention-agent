import logging
from datetime import datetime
from typing import List, Dict

from models import AutonomousAction
from services.autonomous_config import autonomous_config
from services.autonomous.strategy.profile_converter import profile_converter
from services.autonomous.strategy.strategy_finder import strategy_finder
from services.autonomous.utils.priorities import priority_calculator

logger = logging.getLogger(__name__)


class StrategyCategorizer:
    """
    Responsible for finding strategies for customers and categorizing by risk level
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    async def find_and_categorize_strategies(self, customers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Find strategies for customers using existing RAG service and categorize by risk
        """
        # Initialize categorized dict using configured risk categories
        categorized = {category: [] for category in self.config.risk_categories}
        
        # Track customers with no strategies for comprehensive reporting
        system_actions = []
        
        for customer_data in customers:
            customer_id = customer_data.get('customerId', 'unknown')
            
            try:
                # Convert MongoDB document to CustomerProfile format for RAG
                customer_profile = profile_converter.convert_to_customer_profile(customer_data)
                
                # Use RAG service to find strategies
                strategy = strategy_finder.find_strategy_for_customer(customer_profile)
                
                if strategy:
                    risk_category = customer_data.get("churnRiskCategory", "Medium")
                    categorized[risk_category].append({
                        "customer": customer_data,
                        "strategy": strategy
                    })
                else:
                    # No strategies found for this customer
                    no_strategy_action = AutonomousAction(
                        customerId=customer_id,
                        strategyId="NO_STRATEGY",
                        strategyName="No retention strategy found",
                        actionType="system",
                        priority=priority_calculator.get_priority_for_risk_level(
                            customer_data.get("churnRiskCategory", "Medium")
                        ),
                        estimatedImpact=0.0,
                        status="no_strategy",
                        executionDetails={
                            "timestamp": datetime.now().isoformat(),
                            "reason": "no_matching_strategies",
                            "risk_category": customer_data.get("churnRiskCategory", "Medium"),
                            "customer_profile": customer_profile
                        }
                    )
                    system_actions.append(no_strategy_action)
                    
            except Exception as e:
                logger.error(f"RAG service error for customer {customer_id}: {str(e)}")
                # Create action for RAG service failure
                rag_error_action = AutonomousAction(
                    customerId=customer_id,
                    strategyId="RAG_ERROR",
                    strategyName="Strategy discovery failed",
                    actionType="system",
                    priority=priority_calculator.get_priority_for_risk_level(
                        customer_data.get("churnRiskCategory", "Medium")
                    ),
                    estimatedImpact=0.0,
                    status="discovery_failed",
                    executionDetails={
                        "timestamp": datetime.now().isoformat(),
                        "reason": "rag_service_error",
                        "error": str(e),
                        "risk_category": customer_data.get("churnRiskCategory", "Medium")
                    }
                )
                system_actions.append(rag_error_action)
                continue
        
        # Store system actions in categorized dict for later retrieval
        categorized["_system_actions"] = system_actions
        
        return categorized


# Singleton instance
strategy_categorizer = StrategyCategorizer()