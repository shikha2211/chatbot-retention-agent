from fastapi import APIRouter, HTTPException
from services.portfolio_service import get_portfolio_for_user

router = APIRouter()

@router.get("/portfolio/{user_id}")
def fetch_portfolio(user_id: str):
    portfolio = get_portfolio_for_user(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found for this user.")
    return {"customer_ids": portfolio}