import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ProfileConverter:
    """
    Responsible for converting MongoDB customer documents to format expected by RAG service
    """
    
    def convert_to_customer_profile(self, customer_data: Dict) -> Dict:
        """
        Convert MongoDB customer document to format expected by RAG service
        
        TODO: ENHANCE DATA MAPPING - Currently using basic mapping from portfolio data
        In production, enhance this with:
        - Real customer data from CustomerDataTool API
        - Complete customer profile attributes (income, products, etc.)
        - Business context and relationship history
        """
        # =============================================================================
        # BASIC MAPPING - ENHANCE WITH REAL CUSTOMER DATA
        # =============================================================================
        logger.debug("🔶 Using basic customer profile mapping - Enhance with real customer data")
        
        # Create a basic customer profile for RAG
        # You may need to extend this based on available customer data
        return {
            "customerId": customer_data.get("customerId"),
            "industrySector": "SME",  # Default from portfolio data - could get from CustomerDataTool
            "churnRiskCategory": customer_data.get("churnRiskCategory"),
            "segment": customer_data.get("segment", "SME"),
            "customerPriority": customer_data.get("customerPriority", "Medium")
        }
        # =============================================================================
        # END BASIC MAPPING
        # =============================================================================


# Singleton instance
profile_converter = ProfileConverter()