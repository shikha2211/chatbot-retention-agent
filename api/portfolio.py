from fastapi import APIRouter, HTTPException
from services.portfolio_service import get_portfolio_for_user

router = APIRouter()

@router.get("/portfolio/{user_id}")
def fetch_portfolio(user_id: str):
    # Fetch the portfolio documents for the given user_id
    portfolio = get_portfolio_for_user(user_id)

    # If no documents are found, raise a 404 HTTPException
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found for this user.")
    
    # Directly return the portfolio documents
    return {"customer_ids": portfolio}