from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import datetime
from detector_rules import AMOUNT_MULTIPLIER_THRESHOLD, VELOCITY_WINDOW_SECONDS, VELOCITY_THRESHOLD

DB_NAME = "fraud_detector.db"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TransactionCheckRequest(BaseModel):
    user_id: str
    amount: float
    merchant: str


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


@app.post("/check-transaction")
def check_transaction(request: TransactionCheckRequest):
    conn = get_connection()
    user_history = pd.read_sql(
        "SELECT amount, timestamp FROM transactions WHERE user_id = ?",
        conn,
        params=(request.user_id,)
    )
    all_amounts = pd.read_sql("SELECT amount FROM transactions", conn)
    conn.close()

    is_new_user = len(user_history) == 0

    if not is_new_user:
        median_amount = user_history["amount"].median()
    else:
        median_amount = all_amounts["amount"].median()

    if median_amount <= 0:
        median_amount = 1

    ratio = request.amount / median_amount
    amount_flag = ratio >= AMOUNT_MULTIPLIER_THRESHOLD

    velocity_flag = False
    if not is_new_user:
        now = datetime.now()
        user_history["timestamp"] = pd.to_datetime(user_history["timestamp"], errors="coerce")
        recent_count = user_history[
            user_history["timestamp"] >= (now - pd.Timedelta(seconds=VELOCITY_WINDOW_SECONDS))
        ].shape[0]
        velocity_flag = recent_count >= VELOCITY_THRESHOLD

    risk_score = min(100.0, round(ratio * 15, 1))
    final_flag = amount_flag or velocity_flag

    reasons = []
    if amount_flag:
        reasons.append(f"amount is {ratio:.1f}x this user's typical spend")
    if velocity_flag:
        reasons.append("rapid repeated transactions")
    if is_new_user:
        reasons.append("new user — limited history, using overall average as baseline")

    reason = ", ".join(reasons) if reasons else "No anomaly detected — transaction looks normal"

    return {
        "user_id": request.user_id,
        "amount": request.amount,
        "merchant": request.merchant,
        "flagged": bool(final_flag),
        "risk_score": float(risk_score),
        "reason": reason
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)