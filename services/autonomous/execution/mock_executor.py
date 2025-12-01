from typing import List, Dict

from models import AutonomousAction
from services.autonomous_config import autonomous_config
from services.autonomous.execution.action_factory import action_factory


class MockExecutor:
    """
    Responsible for creating mock actions for dry runs
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    def create_mock_actions(self, categorized_strategies: Dict[str, List[Dict]]) -> List[AutonomousAction]:
        """
        Create mock actions for dry run
        """
        mock_actions = []
        
        for risk_level in self.config.risk_categories:
            for item in categorized_strategies.get(risk_level, []):
                customer = item["customer"]
                strategy = item["strategy"]
                
                action = action_factory.create_planned_action(customer, strategy, risk_level)
                mock_actions.append(action)
        
        return mock_actions


# Singleton instance
mock_executor = MockExecutor()