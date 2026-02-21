from typing import List, Dict

from models import AutonomousAction
from services.autonomous_config import autonomous_config


class SummaryGenerator:
    """
    Responsible for building execution summary statistics
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    def build_summary(self, categorized_strategies: Dict, all_actions: List[AutonomousAction]) -> Dict:
        """
        Build execution summary statistics
        """
        summary = {}
        
        # Dynamic risk category counts (only for customers with strategies found)
        for category in self.config.risk_categories:
            key = f"{category.lower()}_risk"
            summary[key] = len(categorized_strategies.get(category, []))
        
        # Action status counts
        status_counts = {}
        for action in all_actions:
            status = action.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Overall statistics
        summary.update({
            "total_customers_processed": len(all_actions),  # All customers that went through the system
            "total_strategies_found": sum(len(strategies) for strategies in categorized_strategies.values()),
            "total_actions_executed": status_counts.get("executed", 0),
            "total_actions_failed": status_counts.get("failed", 0),
            "total_customers_filtered": status_counts.get("filtered", 0),
            "total_no_strategy": status_counts.get("no_strategy", 0),
            "total_discovery_failed": status_counts.get("discovery_failed", 0)
        })
        
        # Add detailed status breakdown
        summary["status_breakdown"] = status_counts
        
        return summary


# Singleton instance
summary_generator = SummaryGenerator()