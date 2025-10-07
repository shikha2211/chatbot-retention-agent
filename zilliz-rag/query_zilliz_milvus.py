import configparser
import json
import os
import random
from typing import List

from pymilvus import MilvusClient


def load_config():
    cfp = configparser.RawConfigParser()
    cfp.read('config.ini')
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


def main():
    uri, token = load_config()
    collection_name = "customer_retention_strategies"
    anns_field = "embedding"
    dim = 64

    client = MilvusClient(uri=uri, token=token)

    customer_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'agents-adk', 'retention-agent', 'customer_response.json',
    )
    customer = load_customer_record(customer_path)

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


if __name__ == "__main__":
    main()


