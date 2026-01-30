from typing import Optional, List  # Import Optional and List
from pydantic import BaseModel, Field



# 4. Define customer profile request model
class CustomerProfile(BaseModel):
    industrySector: Optional[str] = ""
    companySize: Optional[str] = ""
    productsHeld: Optional[str] = ""
    churnReasonTags: Optional[str] = ""
    digitalEngagementScore: Optional[str] = ""
    satisfactionScore: Optional[str] = ""
    openBankingMonthlyRevenueTrend: Optional[str] = ""
    openBankingCashFlowVolatilityScore: Optional[str] = ""
    competitorAttractivenessScore: Optional[str] = ""




class InputModel(BaseModel):
    colleagueQuery: str

# Add this Pydantic model for structured extraction
class CustomerIDExtractor(BaseModel):
    """Extracts customer ID from user input"""
    customer_id: Optional[str] = None


class CommonResponseStringModel(BaseModel):
    """Simple String response from LLM"""
    responseStr: str = Field(description="The output of the agent as per per the query sent the colleague around customer retention")

# added this for testing the portfolio websocket, cam be removed later.
# [TODO] REMOVE THIS LATER.
class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    rmId: str = Field(..., description="Unique relationship manager ID")
    rmName: str = Field(..., description="Relationship manager full name")
    email: Optional[str] = Field(None, description="Email address")
    accountRegion: Optional[str] = Field(None, description="Account region")


# added this for testing the portfolio websocket, cam be removed later.
# [TODO] REMOVE THIS LATER.
class UserResponse(BaseModel):
    """Response model for user operations"""
    success: bool
    message: str
    rmId: Optional[str] = None


# added this for testing the portfolio websocket, cam be removed later.
# [TODO] REMOVE THIS LATER.
# added this for testing the portfolio websocket, cam be removed later.
class PortfolioCreateRequest(BaseModel):
    """Request model for creating a new portfolio entry"""
    rmId: str = Field(..., description="Relationship manager ID")
    rmName: str = Field(..., description="Relationship manager name")
    customerId: str = Field(..., description="Unique customer ID")
    name: str = Field(..., description="Customer name")
    relationshipStartDate: Optional[str] = Field(None, description="Relationship start date")
    accountRegion: Optional[str] = Field(None, description="Account region")
    segment: Optional[str] = Field(None, description="Customer segment (e.g., SME)")
    customerPriority: Optional[str] = Field(None, description="Customer priority level")
    lastInteractionDate: Optional[str] = Field(None, description="Last interaction date")
    portfolioNotes: Optional[str] = Field(None, description="Additional notes")
    churnRiskCategory: Optional[str] = Field("Low", description="Churn risk category (High/Medium/Low)")
    lastActionTaken: Optional[str] = Field(None, description="Last action taken")
    nextStepRecommendation: Optional[str] = Field(None, description="Next step recommendation")
    lastActionDate: Optional[str] = Field(None, description="Last action date")


# added this for testing the portfolio websocket, cam be removed later.
# [TODO] REMOVE THIS LATER.
class PortfolioResponse(BaseModel):
    """Response model for portfolio operations"""
    success: bool
    message: str
    customerId: Optional[str] = None


# Autonomous Agent Models
class AutoAgentRequest(BaseModel):
    """Request model for autonomous agent operations"""
    rm_id: Optional[str] = Field(None, description="Filter specific RM")
    risk_threshold: float = Field(0.5, description="Minimum risk score to process")


class CustomerActionStatus(BaseModel):
    """Model for customer action status from external API"""
    customerId: str
    lastActionDate: Optional[str] = None
    lastActionType: Optional[str] = None
    actionStatus: str  # "pending", "completed", "failed", "none"


class AutonomousAction(BaseModel):
    """Model for autonomous action execution"""
    customerId: str
    strategyId: str
    strategyName: str
    actionType: str  # "email", "call", "offer", "digital"
    priority: int
    estimatedImpact: float
    status: str = "pending"  # "pending", "executed", "failed"
    executionDetails: Optional[dict] = None


class AutoAgentSummary(BaseModel):
    """Summary statistics for autonomous agent execution"""
    # Dynamic risk category counts
    high_risk: int = 0
    medium_risk: int = 0
    low_risk: int = 0
    
    # Overall statistics
    total_customers_processed: int = 0
    total_strategies_found: int = 0
    total_actions_executed: int = 0
    total_actions_failed: int = 0
    total_customers_filtered: int = 0
    total_no_strategy: int = 0
    total_discovery_failed: int = 0
    
    # Detailed status breakdown
    status_breakdown: dict = {}


class AutoAgentResponse(BaseModel):
    """Response model for autonomous agent operations"""
    processed_customers: int
    actions_taken: List[AutonomousAction]
    summary: AutoAgentSummary
    execution_time: float
    timestamp: str


# Configuration Models
class AutonomousServiceConfig(BaseModel):
    """Configuration model for autonomous service settings"""
    
    # Risk Management
    risk_categories: List[str] = Field(default=["High", "Medium", "Low"], description="Valid risk categories")
    default_risk_threshold: float = Field(default=0.5, description="Default risk threshold")
    
    # Time-based Filters
    action_staleness_days: int = Field(default=30, description="Days after which actions are considered stale")
    
    # Batch Processing Limits
    max_customers_per_batch: int = Field(default=500, description="Maximum customers to process in one batch")
    max_actions_per_execution: int = Field(default=100, description="Maximum actions to execute in one run")
    
    # Strategy Selection
    max_strategies_per_customer: int = Field(default=3, description="Maximum strategies to consider per customer")
    min_strategy_success_rate: float = Field(default=0.3, description="Minimum strategy success rate to consider")
    
    # Execution Controls
    enable_actual_execution: bool = Field(default=False, description="Enable actual strategy execution (vs mock)")
    
    # Environment-specific Settings
    environment: str = Field(default="development", description="Environment: development, staging, production")


class BusinessRulesConfig(BaseModel):
    """Business rules configuration for autonomous operations"""
    
    # Customer Filtering Rules
    exclude_customer_segments: List[str] = Field(default=[], description="Customer segments to exclude from processing")
    minimum_relationship_days: int = Field(default=90, description="Minimum relationship duration in days")
    
    # Action Frequency Rules
    max_actions_per_customer_per_month: int = Field(default=3, description="Maximum actions per customer per month")
    cooldown_period_between_actions_days: int = Field(default=7, description="Minimum days between actions for same customer")
    
    # Risk-based Limits
    high_risk_action_limit: int = Field(default=10, description="Maximum high-risk actions per execution")
    medium_risk_action_limit: int = Field(default=50, description="Maximum medium-risk actions per execution")
    low_risk_action_limit: int = Field(default=100, description="Maximum low-risk actions per execution")

class ClearPortfolioRequest(BaseModel):
    """Request model for clearing portfolio data for a specific RM"""
    rmId: str = Field(..., description="Relationship manager ID to clear portfolio data for")
