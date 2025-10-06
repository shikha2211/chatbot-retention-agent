from fastapi import APIRouter, HTTPException, Body
from services.query_zilliz_milvus_service import query_zilliz_milvus_service



router = APIRouter()

@router.post("/fetch-retention-strategies")
def fetch_retention_strategies(customer: dict = Body(...)):
    results = query_zilliz_milvus_service(customer)
    if not results:
        raise HTTPException(status_code=404, detail="No strategies found for this customer details.")

    hits = results[0] if results else []
    serialized = []
    for hit in hits:
        entity = hit.get('entity', {}) or {}
        serialized.append({
            "retentionStrategyId": entity.get("retentionStrategyId"),
            "strategyName": entity.get("strategyName"),
            "offerType": entity.get("offerType"),
            "applicableCustomerSegment": entity.get("applicableCustomerSegment"),
            "estimatedSuccessRate": entity.get("estimatedSuccessRate"),
            "retentionScore": entity.get("retentionScore"),
            "channelOfDelivery": entity.get("channelOfDelivery"),
            "industrySector": entity.get("industrySector"),
            "companySize": entity.get("companySize"),
            "distance": hit.get("distance"),
        })

    return {"results": serialized}