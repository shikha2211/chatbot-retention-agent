import configparser
import json
import os
import time
import random

from pymilvus import MilvusClient
from pymilvus import DataType

milvus_uri = os.getenv('MILVUS_URI')
token = os.getenv('MILVUS_TOKEN')

print(f"\nConnecting to DB: {milvus_uri} with token: {token}")

milvus_client = MilvusClient(uri=milvus_uri, token=token)
print(f"\nConnected to DB: {milvus_uri} successfully")


# Check if the collection exists
collection_name = "customer_retention_strategies"
check_collection = milvus_client.has_collection(collection_name)

if check_collection:
    milvus_client.drop_collection(collection_name)
    print(f"\nDropped the existing collection {collection_name} successfully")

dim = 64

print("Start to create the collection schema")
schema = milvus_client.create_schema()

# Primary key from JSON data and core fields
schema.add_field("retentionStrategyId", DataType.VARCHAR, max_length=128, is_primary=True, description="strategy id (PK)")
schema.add_field("offerDetailsLength", DataType.INT64, description="length of offerDetails text")
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=dim, description="embedding vector")

# Core identifiers and text fields
schema.add_field("strategyName", DataType.VARCHAR, max_length=1024, description="strategy name")
schema.add_field("offerType", DataType.VARCHAR, max_length=128, description="offer type")
schema.add_field("applicableCustomerSegment", DataType.VARCHAR, max_length=128, description="customer segment")

# Arrays stored as JSON strings for portability across Milvus versions
schema.add_field("applicableProducts_json", DataType.VARCHAR, max_length=65535, description="JSON array: applicable products")
schema.add_field("applicableChurnReasonTags_json", DataType.VARCHAR, max_length=65535, description="JSON array: churn reason tags")
schema.add_field("productsHeld_json", DataType.VARCHAR, max_length=65535, description="JSON array: products held")
schema.add_field("churnReasonTags_json", DataType.VARCHAR, max_length=65535, description="JSON array: churn reason tags (duplicate key)")

# Thresholds and numeric attributes
schema.add_field("minimumDigitalEngagementScore", DataType.INT64, description="minimum digital engagement score")
schema.add_field("minimumSatisfactionScore", DataType.INT64, description="minimum satisfaction score")
schema.add_field("openBankingCashFlowVolatilityMax", DataType.INT64, description="max allowed cash flow volatility")
schema.add_field("competitorAttractivenessMinScore", DataType.INT64, description="minimum competitor attractiveness")

# Context and delivery
schema.add_field("openBankingRevenueTrendCondition", DataType.VARCHAR, max_length=64, description="revenue trend condition")
schema.add_field("channelOfDelivery", DataType.VARCHAR, max_length=128, description="delivery channel")
schema.add_field("offerDetails", DataType.VARCHAR, max_length=65535, description="offer details long text")
schema.add_field("estimatedCostToBank", DataType.VARCHAR, max_length=64, description="estimated cost category")
schema.add_field("personalizationLevel", DataType.VARCHAR, max_length=64, description="personalization level")
schema.add_field("timeSensitivity", DataType.VARCHAR, max_length=64, description="time sensitivity")
schema.add_field("remarks", DataType.VARCHAR, max_length=65535, description="remarks long text")
schema.add_field("industrySector", DataType.VARCHAR, max_length=256, description="industry sector")
schema.add_field("companySize", DataType.VARCHAR, max_length=64, description="company size")

# Observed scores and outcomes
schema.add_field("digitalEngagementScore", DataType.INT64, description="observed digital engagement score")
schema.add_field("satisfactionScore", DataType.INT64, description="observed satisfaction score")
schema.add_field("openBankingRevenueTrend", DataType.VARCHAR, max_length=64, description="observed revenue trend")
schema.add_field("openBankingCashFlowVolatilityScore", DataType.INT64, description="observed volatility score")
schema.add_field("competitorAttractivenessScore", DataType.INT64, description="observed competitor attractiveness")
schema.add_field("estimatedSuccessRate", DataType.FLOAT, description="estimated success rate percentage")
schema.add_field("outcome", DataType.VARCHAR, max_length=64, description="outcome")
schema.add_field("retentionScore", DataType.FLOAT, description="overall retention score")

# Optional: full JSON record for ease of retrieval/debugging
schema.add_field("record_json", DataType.VARCHAR, max_length=65535, description="full JSON record")



print("Start to prepare index parameters with default AUTOINDEX")
index_params = milvus_client.prepare_index_params()
index_params.add_index("embedding", metric_type="L2")

print(f"\nStart to create example collection: {collection_name}")
# create collection with the above schema and index parameters, and then load automatically
milvus_client.create_collection(collection_name, schema=schema, index_params=index_params)
collection_property = milvus_client.describe_collection(collection_name)
print("Collection details: %s" % collection_property)

# insert data with customized ids
nb = 1000
insert_rounds = 2
start = 0           # first primary key id
total_rt = 0        # total response time for inert

print(f"\nLoading records from sme_retention_strategies_flattened_no_id.json for collection: {collection_name}")
with open('sme_retention_strategies_flattened_no_id.json', 'r') as f:
    records = json.load(f)

print(f"\nStart to insert {len(records)} entities into collection (deduplicated by retentionStrategyId): {collection_name}")
rows = []
seen_ids = set()
for rec in records:
    rsid = rec.get("retentionStrategyId")
    if not isinstance(rsid, str) or rsid in seen_ids:
        continue
    seen_ids.add(rsid)

    vector = [random.random() for _ in range(dim)]
    offer_len = len(rec.get("offerDetails", "")) if isinstance(rec.get("offerDetails", ""), str) else 0

    row = {
        "retentionStrategyId": rsid,
        "offerDetailsLength": offer_len,
        "embedding": vector,
        "record_json": json.dumps(rec),
    }
    # Optional non-PK text fields
    if isinstance(rec.get("strategyName"), str):
        row["strategyName"] = rec["strategyName"]
    if isinstance(rec.get("offerType"), str):
        row["offerType"] = rec["offerType"]
    if isinstance(rec.get("applicableCustomerSegment"), str):
        row["applicableCustomerSegment"] = rec["applicableCustomerSegment"]
    # Arrays to JSON strings
    if isinstance(rec.get("applicableProducts"), list):
        row["applicableProducts_json"] = json.dumps(rec["applicableProducts"])
    if isinstance(rec.get("applicableChurnReasonTags"), list):
        row["applicableChurnReasonTags_json"] = json.dumps(rec["applicableChurnReasonTags"])
    if isinstance(rec.get("productsHeld"), list):
        row["productsHeld_json"] = json.dumps(rec["productsHeld"])
    if isinstance(rec.get("churnReasonTags"), list):
        row["churnReasonTags_json"] = json.dumps(rec["churnReasonTags"])

    # Numeric optionals
    for k in [
        "minimumDigitalEngagementScore",
        "minimumSatisfactionScore",
        "openBankingCashFlowVolatilityMax",
        "competitorAttractivenessMinScore",
        "digitalEngagementScore",
        "satisfactionScore",
        "openBankingCashFlowVolatilityScore",
        "competitorAttractivenessScore",
    ]:
        if isinstance(rec.get(k), int):
            row[k] = rec[k]
    # Floats
    if isinstance(rec.get("retentionScore"), (int, float)):
        row["retentionScore"] = float(rec["retentionScore"])
    est = rec.get("estimatedSuccessRate (%)")
    if isinstance(est, (int, float)):
        row["estimatedSuccessRate"] = float(est)
    # Short strings
    for k in [
        "openBankingRevenueTrendCondition",
        "channelOfDelivery",
        "estimatedCostToBank",
        "personalizationLevel",
        "timeSensitivity",
        "remarks",
        "industrySector",
        "companySize",
        "openBankingRevenueTrend",
        "outcome",
        "offerDetails",
    ]:
        if isinstance(rec.get(k), str):
            row[k] = rec[k]

    rows.append(row)

t0 = time.time()
milvus_client.insert(collection_name, rows)
ins_rt = time.time() - t0
total_rt += ins_rt
print(f"\nInsert completed in {round(total_rt,4)} seconds")

print("Start to flush")
start_flush = time.time()
milvus_client.flush(collection_name)
end_flush = time.time()
print(f"\nFlush completed in {round(end_flush - start_flush, 4)} seconds")

# search
nq = 3
search_params = {"metric_type": "L2",  "params": {"level": 2}}
limit = 2

for i in range(5):
   search_vectors = [[random.random() for _ in range(dim)] for _ in range(nq)]
   t0 = time.time()
   results = milvus_client.search(collection_name,
                                  data=search_vectors,
                                  limit=limit,
                                  search_params=search_params,
                                  anns_field="embedding")
   t1 = time.time()
   assert len(results) == nq
   assert len(results[0]) == limit
   print(f"\nSearch {i} results: {results}")
   print(f"\nSearch {i} latency: {round(t1-t0, 4)} seconds")

