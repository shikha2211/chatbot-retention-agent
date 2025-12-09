from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
import time
from datetime import datetime

from models import AutoAgentRequest, AutoAgentResponse, AutoAgentSummary
from services.autonomous.orchestrator import autonomous_orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/auto/agent", 
    response_model=AutoAgentResponse,
    summary="Execute Autonomous Retention Agent",
    description="Triggers autonomous workflow to discover at-risk customers and execute retention strategies",
    responses={
        200: {
            "description": "Autonomous workflow executed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "processed_customers": 25,
                        "actions_taken": [
                            {
                                "customerId": "CUST_12345",
                                "strategyId": "STR_EMAIL_001",
                                "strategyName": "SME Financial Health Check Email",
                                "actionType": "email",
                                "priority": 1,
                                "estimatedImpact": 0.75,
                                "status": "executed",
                                "executionDetails": {
                                    "timestamp": "2024-01-15T10:30:00Z",
                                    "risk_level": "High",
                                    "channel": "email",
                                    "mock_execution": True
                                }
                            }
                        ],
                        "summary": {
                            "high_risk": 8,
                            "medium_risk": 12,
                            "low_risk": 5,
                            "total_customers_processed": 25,
                            "total_strategies_found": 20,
                            "total_actions_executed": 18,
                            "total_actions_failed": 2,
                            "total_customers_filtered": 3,
                            "total_no_strategy": 2,
                            "total_discovery_failed": 0,
                            "status_breakdown": {
                                "executed": 18,
                                "failed": 2,
                                "filtered": 3,
                                "no_strategy": 2
                            }
                        },
                        "execution_time": 12.34,
                        "timestamp": "2024-01-15T10:30:15Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "risk_threshold must be between 0.0 and 1.0"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error during workflow execution", 
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Autonomous agent failed: Database connection error"
                    }
                }
            }
        }
    }
)
async def trigger_autonomous_agent(
    rm_id: Optional[str] = Query(
        None, 
        description="Relationship Manager ID to filter customers (leave empty for all RMs)",
        example="RM_001",
        regex="^RM_[A-Z0-9]{3,}$"
    ),
    risk_threshold: float = Query(
        0.5, 
        description="Minimum risk score to process customers (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
        example=0.7
    )
):
    """
    **Execute Autonomous Retention Agent Workflow**
    
    Discovers at-risk customers and automatically executes personalized retention strategies.
    
    ## Workflow Steps:
    1. **Discovery**: Find customers with High/Medium churn risk
    2. **Filtering**: Exclude recently actioned customers (< 30 days)
    3. **Strategy Finding**: Use RAG to match customers with retention strategies
    4. **Execution**: Send emails, schedule calls, or create offers
    5. **Recording**: Update customer action history in database
    
    ## Parameters:
    - **rm_id**: Filter to specific Relationship Manager's customers
    - **risk_threshold**: Currently unused (reserved for future filtering)
    
    ## Action Types Generated:
    - `executed`: Successfully processed retention actions
    - `failed`: Actions that encountered errors
    - `filtered`: Customers excluded due to batch limits
    - `no_strategy`: Customers with no matching retention strategies
    - `discovery_failed`: Customers with RAG service errors
    
    ## Rate Limits:
    - Maximum 500 customers per batch (configurable)
    - Maximum 100 actions per execution (configurable)
    
    ## Security:
    ⚠️ **Note**: This endpoint can trigger mass customer communications. Ensure proper authentication and authorization in production.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting autonomous agent - RM: {rm_id}, threshold: {risk_threshold}")
        
        # Create request object
        request = AutoAgentRequest(
            rm_id=rm_id,
            risk_threshold=risk_threshold
        )
        
        # Execute the autonomous workflow
        result = await autonomous_orchestrator.execute_autonomous_workflow(request)
        
        execution_time = time.time() - start_time
        
        # Build response
        response = AutoAgentResponse(
            processed_customers=result["processed_customers"],
            actions_taken=result["actions_taken"],
            summary=AutoAgentSummary(**result["summary"]),
            execution_time=round(execution_time, 2),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Autonomous agent completed in {execution_time:.2f}s - Processed: {result['processed_customers']} customers")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in autonomous agent: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Autonomous agent failed: {str(e)}"
        )


@router.get(
    "/auto/agent/status",
    summary="Get Autonomous Agent System Status", 
    description="Check health and operational status of all autonomous agent components",
    responses={
        200: {
            "description": "System status retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy": {
                            "summary": "All systems healthy",
                            "value": {
                                "status": "healthy",
                                "components": {
                                    "mongodb": {
                                        "status": "healthy",
                                        "message": "Connected"
                                    },
                                    "rag_service": {
                                        "status": "healthy", 
                                        "message": "Operational"
                                    }
                                },
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        },
                        "degraded": {
                            "summary": "Some components unhealthy",
                            "value": {
                                "status": "degraded",
                                "components": {
                                    "mongodb": {
                                        "status": "healthy",
                                        "message": "Connected"
                                    },
                                    "rag_service": {
                                        "status": "unhealthy",
                                        "message": "Connection timeout"
                                    }
                                },
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error checking system status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "error": "Database connection failed",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def get_autonomous_agent_status():
    """
    **Get Autonomous Agent System Status**
    
    Performs health checks on all critical components required for autonomous operation.
    
    ## Components Checked:
    - **MongoDB**: Database connectivity and response time
    - **RAG Service**: Vector database and strategy retrieval functionality
    
    ## Status Levels:
    - `healthy`: All components operational
    - `degraded`: Some components have issues but system partially functional
    - `error`: Cannot determine system status due to critical failure
    
    ## Use Cases:
    - Pre-flight checks before running autonomous workflows
    - Monitoring system health in production
    - Troubleshooting execution failures
    """
    try:
        status = await autonomous_orchestrator.get_system_status()
        
        return {
            "status": "healthy" if status["all_healthy"] else "degraded",
            "components": status["components"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking autonomous agent status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

