import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

NUM_USERS = 50
NUM_NORMAL_TXNS = 2000
START_TIME = datetime(2026,8,27,9,0,0)

merchants = ["Amazon", "Swiggy" , "Zomato" ,"Flipkart","Uber","BookMyShow","Netflix","BigBasket","Myntra","Ola"]
def random_user_ids(n):
    return [f"user_{i:03d}" for i in range(1,n+1)]

users = random_user_ids(NUM_USERS)

rows = []
for _ in range(NUM_NORMAL_TXNS):
    user = random.choice(users)
    # normal amount: most transacations small-medium ,occasionally bigger
    amount = round(np.random.gamma(shape=2.0,scale = 400),2)
    merchant = random.choice(merchants)
    #spread transactions across -24 hours randomly 
    offset_seconds = random.randint(0, 24*60*60)
    timestamp = START_TIME + timedelta(seconds=offset_seconds)
    rows.append({
        "user_id":user,
        "amount":amount,
        "merchant":merchant,
        "timestamp":timestamp
    })
fraud_user_1 = "user_007"
spike1_start = START_TIME + timedelta(hours=5)
for i in range(25):
    amount = round(random.uniform(10,50),2)
    timestamp = spike1_start + timedelta(seconds=i*4)
    rows.append({
        "user_id":fraud_user_1,
        "amount":amount,
        "merchant":random.choice(merchants),
        "timestamp":timestamp
    })

fraud_user_2 = "user_022"
spike2_time = START_TIME + timedelta(hours=14)
rows.append({
    "user_id":fraud_user_2,
    "amount":45000.00,
    "merchant":"Amazon",
    "timestamp":spike2_time
})

df = pd.DataFrame(rows)
df = df.sort_values("timestamp").reset_index(drop=True)
df.to_csv("transactions.csv", index=False)

print(f"✅ {len(df)} transactions generate ho gaye.")
print(f"   - Normal: {NUM_NORMAL_TXNS}")
print(f"   - Fraud Spike 1 (user_007, rapid small txns): 25")
print(f"   - Fraud Spike 2 (user_022, one huge txn): 1")
print("Saved to transactions.csv")
