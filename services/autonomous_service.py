# New modular autonomous service - backward compatibility wrapper
from services.autonomous.orchestrator import autonomous_orchestrator


class AutonomousService:
    """
    Backward compatibility wrapper for the refactored autonomous service.
    Delegates to the new modular orchestrator.
    """
    
    async def execute_autonomous_workflow(self, request):
        """Execute autonomous workflow using new orchestrator"""
        return await autonomous_orchestrator.execute_autonomous_workflow(request)
    
    async def get_system_status(self):
        """Get system status using new health checker"""
        return await autonomous_orchestrator.get_system_status()


# Singleton instance for backward compatibility
autonomous_service = AutonomousService()