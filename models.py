from typing import Optional  # Import Optional
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
# [TODO] REMOVE THIS LATER.class PortfolioResponse(BaseModel):
    """Response model for portfolio operations"""
    success: bool
    message: str
    customerId: Optional[str] = None


class ClearPortfolioRequest(BaseModel):
    """Request model for clearing portfolio data for a specific RM"""
    rmId: str = Field(..., description="Relationship manager ID to clear portfolio data for")
