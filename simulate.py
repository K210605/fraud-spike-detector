import time
import random
import pandas as pd
from detector_combined import run_combined_detection
from database import init_db, save_to_db

MERCHANTS = ["Amazon", "Swiggy", "Zomato", "Flipkart", "Uber", "BookMyShow",
             "Netflix", "BigBasket", "Myntra", "Ola"]
USERS = [f"user_{i:03d}" for i in range(1, 51)]

CSV_FILE = "transactions.csv"


def generate_normal_batch(n, base_time):
    rows = []
    for i in range(n):
        txn_time = base_time + pd.Timedelta(seconds=i * random.randint(3, 8))
        rows.append({
            "user_id": random.choice(USERS),
            "amount": round(random.gauss(800, 400), 2),
            "merchant": random.choice(MERCHANTS),
            "timestamp": txn_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return rows


def generate_fraud_spike(base_time):
    fraud_user = random.choice(USERS)
    rows = []
    for i in range(random.randint(6, 12)):
        txn_time = base_time + pd.Timedelta(seconds=i * 4)
        rows.append({
            "user_id": fraud_user,
            "amount": round(random.uniform(10, 60), 2),
            "merchant": random.choice(MERCHANTS),
            "timestamp": txn_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return rows


def run_simulation(rounds=20, interval_seconds=15):
    print("🚀 Starting live transaction simulation...")
    print(f"   New batch every {interval_seconds}s, {rounds} rounds total\n")

    for round_num in range(1, rounds + 1):
        df = pd.read_csv(CSV_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["is_new_batch"] = False

        now = df["timestamp"].max() + pd.Timedelta(seconds=random.randint(30, 120))

        new_rows = generate_normal_batch(random.randint(8, 15), now)

        is_fraud_round = random.random() < 0.25
        if is_fraud_round:
            new_rows += generate_fraud_spike(now)
            print(f"[Round {round_num}] ⚠️  Injecting a fraud spike ({len(new_rows)} new txns)")
        else:
            print(f"[Round {round_num}] Adding {len(new_rows)} normal txns")

        new_df = pd.DataFrame(new_rows)
        new_df["is_new_batch"] = True

        df = pd.concat([df, new_df], ignore_index=True)

        result = run_combined_detection(df)
        result["is_new_batch"] = df["is_new_batch"]

        df_to_save = df.drop(columns=["is_new_batch"])
        df_to_save.to_csv(CSV_FILE, index=False)

        save_to_db(result)

        this_batch = result[result["is_new_batch"] == True]
        flagged_now = int(this_batch["final_flag"].sum())
        print(f"   🚩 {flagged_now} of {len(this_batch)} in this batch flagged as suspicious")

        time.sleep(interval_seconds)

    print("\n✅ Simulation complete.")


if __name__ == "__main__":
    init_db()
    run_simulation(rounds=20, interval_seconds=15)