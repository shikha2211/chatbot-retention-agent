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
