import logging
from typing import Dict

from services.portfolio_service import collection
from services.query_zilliz_milvus_service import query_zilliz_milvus_service

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Responsible for checking health of all components used by autonomous agent
    """
    
    async def get_system_status(self) -> Dict:
        """
        Check health of all components used by autonomous agent
        """
        components = {}
        
        try:
            # Check MongoDB connection
            collection.find_one()
            components["mongodb"] = {"status": "healthy", "message": "Connected"}
        except Exception as e:
            components["mongodb"] = {"status": "unhealthy", "message": str(e)}
        
        try:
            # Check RAG service
            test_customer = {"customerId": "TEST", "industrySector": "SME"}
            query_zilliz_milvus_service(test_customer)
            components["rag_service"] = {"status": "healthy", "message": "Operational"}
        except Exception as e:
            components["rag_service"] = {"status": "unhealthy", "message": str(e)}
        
        # Overall health
        all_healthy = all(comp["status"] == "healthy" for comp in components.values())
        
        return {
            "all_healthy": all_healthy,
            "components": components
        }


# Singleton instance
health_checker = HealthChecker()