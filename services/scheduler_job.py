import schedule
import time
import requests
from datetime import datetime
from services.query_zilliz_milvus_service import query_zilliz_milvus_service


def callZillizQuery():
    print(f"\n\n Current time is : [{datetime.now()}] , Scheduler Calling Zilliz for Regular query")
    try:
        customer = {
            "customerId": "CUST_0006",
            "industrySector": "Retail",
            "productsHeld": "Deposits, Lending, Credit Card",
            "averageCurrentAccountBalance": "36358.82",
            "depositBalance": "70329.99",
            "digitalEngagementScore": "5",
            "satisfactionScore": "1",
            "relationshipManagerEngagementScore": "3",
            "competitorAttractivenessScore": "9",
            "churnRiskScore": "0.64",
            "churnRiskCategory": "Medium",
            "primaryChurnReasons": "Faster loan approvals at fintech lender, Better API integrations for current account accounting, Declining revenue and better working capital support offered elsewhere",
            "churnReasonTags": "Speed/Convenience, Cash Flow Stress, Product Features"
        }

        response = query_zilliz_milvus_service(customer)
        print("✅ Success:", response)
    except requests.RequestException as e:
        print("❌ Error While query_zilliz_milvus_service:", e)

def startScheduler():
    
    executionTime = "14:32"

    print(f"[{datetime.now()}] is current time")

    # Schedule to run every day at 09:00 AM
    schedule.every().day.at(executionTime).do(callZillizQuery)

    print(f"\n\n 🚀 Scheduler started. will run the job at : {executionTime}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
