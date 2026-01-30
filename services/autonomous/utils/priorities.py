from services.autonomous_config import autonomous_config


class PriorityCalculator:
    """
    Responsible for calculating priorities based on risk levels
    """
    
    def __init__(self):
        self.config = autonomous_config
    
    def get_priority_for_risk_level(self, risk_level: str) -> int:
        """
        Get numeric priority based on risk level position in configured categories
        Lower number = higher priority
        """
        try:
            # Priority is 1-based index of risk level in configured categories
            return self.config.risk_categories.index(risk_level) + 1
        except ValueError:
            # If risk level not found in config, assign lowest priority
            return len(self.config.risk_categories) + 1


# Singleton instance
priority_calculator = PriorityCalculator()