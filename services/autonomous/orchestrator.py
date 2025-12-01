import logging
from typing import Dict

from models import AutoAgentRequest

# Discovery modules
from services.autonomous.discovery.customer_finder import customer_finder
from services.autonomous.discovery.action_checker import action_checker
from services.autonomous.discovery.customer_filter import customer_filter

# Strategy modules
from services.autonomous.strategy.categorizer import strategy_categorizer

# Execution modules
from services.autonomous.execution.executor import strategy_executor
from services.autonomous.execution.mock_executor import mock_executor

# Persistence modules
from services.autonomous.persistence.db_updater import db_updater
from services.autonomous.persistence.action_recorder import action_recorder

# Utils
from services.autonomous.utils.summarizer import summary_generator
from services.autonomous.utils.health_checker import health_checker

logger = logging.getLogger(__name__)


# Status value conventions:
# CustomerActionStatus.actionStatus: "pending", "completed", "failed", "none"
# AutonomousAction.status: "executed", "planned", "failed", "filtered", "no_strategy", "discovery_failed"


class AutonomousOrchestrator:
    """
    Main orchestrator for autonomous retention agent workflow.
    Coordinates all autonomous service components to execute retention actions.
    """
    
    async def execute_autonomous_workflow(self, request: AutoAgentRequest) -> Dict:
        """
        Execute the complete autonomous workflow
        
        Steps:
        1. Discover at-risk customers
        2. Check action status 
        3. Filter unactioned customers
        4. Apply batch limits
        5. Find strategies and categorize
        6. Execute strategies (mock for now)
        7. Update database
        8. Record actions and build summary
        """
        logger.info(f"Starting autonomous workflow - RM: {request.rm_id}, dry_run: {request.dry_run}")
        
        # Step 1: Get all at-risk customers
        at_risk_customers = await customer_finder.discover_at_risk_customers(request.rm_id)
        logger.info(f"Found {len(at_risk_customers)} at-risk customers")
        
        # Step 2: Check action status
        action_statuses = await action_checker.check_customer_action_status([c["customerId"] for c in at_risk_customers])
        
        # Step 3: Filter unactioned customers
        unactioned_customers = customer_filter.filter_unactioned_customers(at_risk_customers, action_statuses)
        logger.info(f"Found {len(unactioned_customers)} customers needing action")
        
        # Step 4: Apply batch size limits and track filtered customers
        customers_to_process, filtered_actions = customer_filter.apply_batch_limits(unactioned_customers)
        if filtered_actions:
            logger.warning(f"Filtered {len(filtered_actions)} customers due to batch size limits")
        
        # Step 5: Find strategies and categorize by risk
        categorized_strategies = await strategy_categorizer.find_and_categorize_strategies(customers_to_process)
        
        # Extract system actions (no strategies, discovery failures)
        system_actions = categorized_strategies.pop("_system_actions", [])
        
        # Step 6: Execute strategies
        executed_actions = []
        if not request.dry_run:
            executed_actions = await strategy_executor.execute_strategies(categorized_strategies)
            
            # Step 7: Update database (only for successful/failed execution actions, not system actions)
            db_actions = [a for a in executed_actions if a.actionType != "system"]
            await db_updater.update_action_records(db_actions)
        else:
            # For dry run, create mock actions
            executed_actions = mock_executor.create_mock_actions(categorized_strategies)
        
        # Step 8: Combine all actions and record them
        all_actions = executed_actions + filtered_actions + system_actions
        action_recorder.record_actions(all_actions)
        
        # Build summary
        summary = summary_generator.build_summary(categorized_strategies, all_actions)
        
        return {
            "processed_customers": len(all_actions),  # Total customers processed (all action types)
            "actions_taken": all_actions,
            "summary": summary
        }
    
    async def get_system_status(self) -> Dict:
        """
        Check health of all components used by autonomous agent
        """
        return await health_checker.get_system_status()


# Singleton instance
autonomous_orchestrator = AutonomousOrchestrator()