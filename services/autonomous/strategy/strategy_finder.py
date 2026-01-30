import logging
from typing import Dict, Optional

from tools import StrategyRetrievalTool
from models import CustomerProfile

logger = logging.getLogger(__name__)


class StrategyFinder:
    """
    Responsible for finding retention strategies using RAG service
    """
    
    async def find_strategy_for_customer(self, customer_profile: Dict) -> Optional[Dict]:
        """
        Find the best strategy for a customer using StrategyRetrievalTool
        
        Returns:
            Best strategy dict if found, None if no strategies found
        """
        try:
            # Convert customer dict to CustomerProfile model for the tool
            profile = CustomerProfile(
                industrySector=customer_profile.get("industrySector", ""),
                companySize=customer_profile.get("companySize", ""),
                productsHeld=customer_profile.get("productsHeld", ""),
                churnReasonTags=customer_profile.get("churnReasonTags", ""),
                digitalEngagementScore=customer_profile.get("digitalEngagementScore", ""),
                satisfactionScore=customer_profile.get("satisfactionScore", ""),
                openBankingMonthlyRevenueTrend=customer_profile.get("openBankingMonthlyRevenueTrend", ""),
                openBankingCashFlowVolatilityScore=customer_profile.get("openBankingCashFlowVolatilityScore", ""),
                competitorAttractivenessScore=customer_profile.get("competitorAttractivenessScore", "")
            )
            
            # Use StrategyRetrievalTool to find strategies
            strategy_results = await StrategyRetrievalTool(profile)
            
            if strategy_results and not strategy_results.get("error"):
                if strategy_results.get("results") or strategy_results.get("strategies"):
                    # Handle both possible response formats
                    strategies = strategy_results.get("results") or strategy_results.get("strategies")
                    if strategies and len(strategies) > 0:
                        # Take the best strategy (first one with highest similarity)
                        best_strategy = strategies[0]
                        return best_strategy
            
            return None
                
        except Exception as e:
            logger.error(f"StrategyRetrievalTool error for customer {customer_profile.get('customerId', 'unknown')}: {str(e)}")
            raise  # Re-raise to let caller handle the error appropriately


# Singleton instance
strategy_finder = StrategyFinder()