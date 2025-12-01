import logging
from typing import List

from models import AutonomousAction

logger = logging.getLogger(__name__)


class ActionRecorder:
    """
    Responsible for recording and tracking action history
    
    TODO: In production, this could be extended to:
    - Store full action history in a separate collection
    - Track action effectiveness and outcomes
    - Provide audit trails for compliance
    - Support action rollback/retry mechanisms
    """
    
    def record_actions(self, actions: List[AutonomousAction]):
        """
        Record actions for audit and tracking purposes
        
        Currently this is just logging, but could be extended to:
        - Store in action history table
        - Send to audit systems
        - Trigger monitoring alerts
        """
        logger.info(f"Recording {len(actions)} actions for audit trail")
        
        for action in actions:
            logger.info(f"Action recorded: {action.customerId} - {action.strategyName} - {action.status}")
    
    def get_action_summary(self, actions: List[AutonomousAction]) -> dict:
        """
        Generate summary statistics for recorded actions
        """
        status_counts = {}
        for action in actions:
            status = action.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_actions": len(actions),
            "status_breakdown": status_counts
        }


# Singleton instance
action_recorder = ActionRecorder()