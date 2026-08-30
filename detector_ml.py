import pandas as pd
from sklearn.ensemble import IsolationForest

def build_features(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    df["time_since_last_txn"] = df.groupby("user_id")["timestamp"].diff().dt.total_seconds()
    df["time_since_last_txn"] = df["time_since_last_txn"].fillna(9999)

    df["user_avg_amount"] = df.groupby("user_id")["amount"].transform("median")
    df["amount_ratio"] = df["amount"] / df["user_avg_amount"].replace(0, 1)

    return df

def run_ml_detection(df):
    df = build_features(df)

    feature_cols = ["amount", "time_since_last_txn", "amount_ratio"]
    X = df[feature_cols]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )
    model.fit(X)

    df["anomaly_score_raw"] = model.decision_function(X)
    df["ml_flag"] = model.predict(X) == -1

    min_score = df["anomaly_score_raw"].min()
    max_score = df["anomaly_score_raw"].max()
    df["risk_score"] = ((max_score - df["anomaly_score_raw"]) / (max_score - min_score) * 100).round(1)

    return df

if __name__ == "__main__":
    df = pd.read_csv("transactions.csv")
    result = run_ml_detection(df)

    flagged = result[result["ml_flag"] == True].sort_values("risk_score", ascending=False)

    print(f"Total transactions: {len(result)}")
    print(f"Flagged by ML: {len(flagged)}")
    print()
    print("Top flagged transactions (by risk score):")
    print(flagged[["user_id", "amount", "timestamp", "risk_score"]].head(10).to_string(index=False))