import requests
import json
import random
import time

API_URL = "https://VOTRE-API-ID.execute-api.us-east-1.amazonaws.com/prod/transaction"

users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
merchants = ["MERCH_AMAZON", "MERCH_WALMART", "MERCH_APPLE", "MERCH_TARGET"]
categories = ["RETAIL", "GROCERY", "ELECTRONICS", "FOOD"]

def send_transaction(tx):
    try:
        r = requests.post(API_URL, json=tx, timeout=10)
        print(f"{'✅' if r.status_code==200 else '❌'} {tx['user_id']} ${tx['amount']:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🚀 Génération de 50 transactions...")

# 30 normales
for i in range(30):
    send_transaction({
        "user_id": random.choice(["user_001", "user_004", "user_005"]),
        "amount": round(random.uniform(20, 300), 2),
        "merchant_id": random.choice(merchants),
        "merchant_category": random.choice(categories),
        "device_id": "device_abc123",
        "location": "New York, US"
    })
    time.sleep(0.5)

# 10 suspectes
for i in range(10):
    send_transaction({
        "user_id": random.choice(users),
        "amount": round(random.uniform(3000, 8000), 2),
        "merchant_id": "MERCH_SUSPICIOUS",
        "merchant_category": "UNKNOWN",
        "device_id": "device_unknown",
        "location": "Unknown"
    })
    time.sleep(0.5)

# 10 nouveau client
for i in range(10):
    send_transaction({
        "user_id": "user_003",
        "amount": round(random.uniform(500, 2000), 2),
        "merchant_id": random.choice(merchants),
        "merchant_category": random.choice(categories),
        "device_id": "device_new999",
        "location": "Chicago, US"
    })
    time.sleep(0.5)

print("\n✅ TERMINÉ! Vérifiez:")
print("1. Emails SNS")
print("2. CloudWatch Logs")
print("3. S3 raw/ (attendre 2 min)")


Exécuter:

pip install requests
python generate_transactions.py

