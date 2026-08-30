import pandas as pd
from detector_rules import run_rule_based_detection
from detector_ml import run_ml_detection

def run_combined_detection(df):
    df_rules = run_rule_based_detection(df.copy())
    df_ml = run_ml_detection(df.copy())

    combined = df_rules.copy()
    combined["ml_flag"] = df_ml["ml_flag"]
    combined["risk_score"] = df_ml["risk_score"]

    combined["final_flag"] = combined["rule_flag"] | combined["ml_flag"]

    def get_reason(row):
        reasons = []
        if row["velocity_flag"]:
            reasons.append("rapid transactions")
        if row["amount_flag"]:
            reasons.append("unusually high amount")
        if row["ml_flag"] and not row["rule_flag"]:
            reasons.append("ML anomaly pattern")
        return ", ".join(reasons) if reasons else "normal"

    combined["reason"] = combined.apply(get_reason, axis=1)

    return combined


if __name__ == "__main__":
    df = pd.read_csv("transactions.csv")
    result = run_combined_detection(df)

    flagged = result[result["final_flag"] == True].sort_values("risk_score", ascending=False)

    print(f"Total transactions: {len(result)}")
    print(f"Flagged (combined): {len(flagged)}")
    print()
    print("Top flagged transactions:")
    print(flagged[["user_id", "amount", "timestamp", "risk_score", "reason"]].head(15).to_string(index=False))

    result.to_csv("flagged_results.csv", index=False)
    print()
    print("Full results saved to flagged_results.csv")