from datetime import datetime
from typing import Dict, Optional

from models import AutonomousAction
from services.autonomous.utils.mappers import action_type_mapper
from services.autonomous.utils.priorities import priority_calculator


class ActionFactory:
    """
    Factory for creating AutonomousAction objects
    """
    
    def create_executed_action(self, customer: Dict, strategy: Dict, risk_level: str) -> AutonomousAction:
        """Create an executed action record"""
        action_type = action_type_mapper.determine_action_type(strategy)
        
        return AutonomousAction(
            customerId=customer.get("customerId"),
            strategyId=strategy.get("retentionStrategyId", "UNKNOWN"),
            strategyName=strategy.get("strategyName", "Unknown Strategy"),
            actionType=action_type,
            priority=priority_calculator.get_priority_for_risk_level(risk_level),
            estimatedImpact=strategy.get("estimatedSuccessRate", 0.5),
            status="executed",  # In production, this might be "pending" initially
            executionDetails={
                "timestamp": datetime.now().isoformat(),
                "risk_level": risk_level,
                "channel": strategy.get("channelOfDelivery", "email"),
                "mock_execution": True  # Remove this in production
            }
        )
    
    def create_failed_action(self, customer: Dict, strategy: Dict, risk_level: str, error: Exception) -> AutonomousAction:
        """Create a failed action record"""
        customer_id = customer.get('customerId', 'unknown')
        
        return AutonomousAction(
            customerId=customer_id,
            strategyId=strategy.get("retentionStrategyId", "FAILED"),
            strategyName=strategy.get("strategyName", "Failed Strategy"),
            actionType=action_type_mapper.determine_action_type(strategy),
            priority=priority_calculator.get_priority_for_risk_level(risk_level),
            estimatedImpact=0.0,
            status="failed",
            executionDetails={
                "timestamp": datetime.now().isoformat(),
                "error": str(error),
                "risk_level": risk_level
            }
        )
    


# Singleton instance
action_factory = ActionFactory()