import sqlite3
import pandas as pd

DB_NAME = "fraud_detector.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            amount REAL,
            merchant TEXT,
            timestamp TEXT,
            risk_score REAL,
            final_flag INTEGER,
            reason TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_to_db(df):
    conn = sqlite3.connect(DB_NAME)

    df_to_save = df[["user_id", "amount", "merchant", "timestamp", "risk_score", "final_flag", "reason"]].copy()
    df_to_save["final_flag"] = df_to_save["final_flag"].astype(int)
    df_to_save["timestamp"] = df_to_save["timestamp"].astype(str)

    df_to_save.to_sql("transactions", conn, if_exists="replace", index=False)

    conn.close()
    print(f"✅ {len(df_to_save)} rows saved to {DB_NAME}")


if __name__ == "__main__":
    from detector_combined import run_combined_detection

    init_db()

    df = pd.read_csv("transactions.csv")
    result = run_combined_detection(df)

    save_to_db(result)

    conn = sqlite3.connect(DB_NAME)
    check = pd.read_sql("SELECT * FROM transactions WHERE final_flag = 1 ORDER BY risk_score DESC LIMIT 5", conn)
    conn.close()

    print()