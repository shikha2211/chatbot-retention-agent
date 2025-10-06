import configparser
import json
import os
import random
from typing import List
from pymilvus import MilvusClient


def load_config():
    # Prefer environment variables if present
    uri = os.getenv('MILVUS_URI')
    token = os.getenv('MILVUS_TOKEN')
    if uri and token:
        return uri, token

    # Fall back to api/config.ini relative to this package root
    service_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(service_dir)
    cfg_path = os.path.join(root_dir, 'services', 'config.ini')

    cfp = configparser.RawConfigParser()
    cfp.read(cfg_path)
    uri = cfp.get('example', 'uri')
    token = cfp.get('example', 'token')
    return uri, token


def load_customer_record(path: str) -> dict:
    with open(path, 'r') as f:
        data = json.load(f)
    if isinstance(data, list) and data:
        return data[0]
    return data


def build_customer_embedding(customer: dict, dim: int = 64) -> List[float]:
    # Produce a stable pseudo-embedding seeded by customerId
    seed_basis = str(customer.get('customerId', 'anon'))
    random.seed(hash(seed_basis) % (2**32))
    return [random.random() for _ in range(dim)]



def query_zilliz_milvus_service(customer: dict):
    uri, token = load_config()
    collection_name = "customer_retention_strategies"
    anns_field = "embedding"
    dim = 64

    client = MilvusClient(uri=uri, token=token)

    query_vector = build_customer_embedding(customer, dim=dim)

    search_params = {"metric_type": "L2", "params": {"level": 2}}
    limit = 5

    print(f"Querying Milvus at {uri} for similar retention strategies...\n")
    results = client.search(
        collection_name,
        data=[query_vector],
        limit=limit,
        search_params=search_params,
        anns_field=anns_field,
        output_fields=[
            'retentionStrategyId', 'strategyName', 'offerType', 'applicableCustomerSegment',
            'estimatedSuccessRate', 'retentionScore', 'channelOfDelivery', 'offerDetails',
            'industrySector', 'companySize'
        ],
    )

    hits = results[0] if results else []
    for rank, hit in enumerate(hits, start=1):
        fields = hit.get('entity', {}) or {}
        print(f"#{rank} | id={fields.get('retentionStrategyId')} | distance={hit.get('distance')}")
        print(f"   name: {fields.get('strategyName')} | type: {fields.get('offerType')} | segment: {fields.get('applicableCustomerSegment')}")
        print(f"   success_est: {fields.get('estimatedSuccessRate')} | retention_score: {fields.get('retentionScore')}")
        print(f"   channel: {fields.get('channelOfDelivery')} | sector: {fields.get('industrySector')} | size: {fields.get('companySize')}")
        detail = fields.get('offerDetails')
        if isinstance(detail, str):
            print(f"   details: {detail[:120]}{'...' if len(detail) > 120 else ''}")
        print()
    return results





