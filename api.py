from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd

DB_NAME = "fraud_detector.db"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return sqlite3.connect(DB_NAME)


@app.get("/")
def home():
    return {"message": "Fraud Spike Detector API is running"}


@app.get("/transactions")
def get_all_transactions():
    conn = get_connection()
    df = pd.read_sql("SELECT rowid, * FROM transactions ORDER BY rowid DESC", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/transactions/flagged")
def get_flagged_transactions():
    conn = get_connection()
    df = pd.read_sql("SELECT rowid, * FROM transactions WHERE final_flag = 1 ORDER BY risk_score DESC", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/stats")
def get_stats():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()

    total = len(df)
    flagged = int(df["final_flag"].sum())
    avg_risk_flagged = round(df[df["final_flag"] == 1]["risk_score"].mean(), 1) if flagged > 0 else 0

    return {
        "total_transactions": total,
        "flagged_count": flagged,
        "flagged_percent": round((flagged / total) * 100, 2) if total > 0 else 0,
        "avg_risk_score_flagged": avg_risk_flagged
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)