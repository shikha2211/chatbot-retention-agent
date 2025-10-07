from fastapi import APIRouter, HTTPException, Body
from services.query_zilliz_milvus_service import query_zilliz_milvus_service
from models import CustomerProfile



router = APIRouter()

@router.post("/fetch-retention-strategies")
async def fetch_retention_strategies(customer: dict = CustomerProfile):
    
    print(f"\n==> Inside /api/fetch-retention-strategies, customer : {customer}"); 

    results = query_zilliz_milvus_service(customer)
    

    return results