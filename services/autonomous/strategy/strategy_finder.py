import logging
from typing import Dict, Optional

from services.query_zilliz_milvus_service import query_zilliz_milvus_service

logger = logging.getLogger(__name__)


class StrategyFinder:
    """
    Responsible for finding retention strategies using RAG service
    """
    
    def find_strategy_for_customer(self, customer_profile: Dict) -> Optional[Dict]:
        """
        Find the best strategy for a customer using RAG service
        
        Returns:
            Best strategy dict if found, None if no strategies found
        """
        try:
            # Use existing RAG service to find strategies
            strategy_results = query_zilliz_milvus_service(customer_profile)
            
            if strategy_results.get("results"):
                # Take the best strategy (first one with highest similarity)
                best_strategy = strategy_results["results"][0]
                return best_strategy
            else:
                return None
                
        except Exception as e:
            logger.error(f"RAG service error for customer {customer_profile.get('customerId', 'unknown')}: {str(e)}")
            raise  # Re-raise to let caller handle the error appropriately


# Singleton instance
strategy_finder = StrategyFinder()