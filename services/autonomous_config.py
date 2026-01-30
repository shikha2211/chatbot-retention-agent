import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class AutonomousConfig:
    """Simple configuration for autonomous service"""
    
    def __init__(self):
        # Risk Management - these are business domain concepts, not config
        self.risk_categories: List[str] = ["High", "Medium", "Low"]
        
        # Time-based Filters
        self.action_staleness_days: int = int(os.getenv('AUTO_ACTION_STALENESS_DAYS', '30'))
        
        # Batch Processing Limits
        self.max_customers_per_batch: int = int(os.getenv('AUTO_MAX_CUSTOMERS_BATCH', '500'))
        self.max_actions_per_execution: int = int(os.getenv('AUTO_MAX_ACTIONS_EXECUTION', '100'))
        
        # Environment-specific Settings
        self.environment: str = os.getenv('ENVIRONMENT', 'development')
        
        # Adjust limits based on environment
        if self.environment == 'production':
            # Stricter limits for production
            self.max_customers_per_batch = min(self.max_customers_per_batch, 100)
        elif self.environment == 'development':
            # Smaller batches for development
            self.max_customers_per_batch = min(self.max_customers_per_batch, 10)


# Singleton instance
autonomous_config = AutonomousConfig()