import pandas as pd

VELOCITY_WINDOW_SECONDS = 60
VELOCITY_THRESHOLD = 5
AMOUNT_MULTIPLIER_THRESHOLD = 5


def detect_velocity_spikes(df):
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
    df["velocity_flag"] = False
    df["velocity_count"] = 0

    for user, group in df.groupby("user_id"):
        timestamps = group["timestamp"].values
        indices = group.index.values

        for i, idx in enumerate(indices):
            current_time = timestamps[i]
            window_start = current_time - pd.Timedelta(seconds=VELOCITY_WINDOW_SECONDS)

            count_in_window = ((timestamps >= window_start) & (timestamps <= current_time)).sum()
            df.loc[idx, "velocity_count"] = count_in_window

            if count_in_window >= VELOCITY_THRESHOLD:
                df.loc[idx, "velocity_flag"] = True

    return df


def detect_amount_anomalies(df):
    df = df.copy()
    df["amount_flag"] = False
    df["user_avg_amount"] = 0.0

    for user, group in df.groupby("user_id"):
        avg_amount = group["amount"].median()
        df.loc[group.index, "user_avg_amount"] = avg_amount

        if avg_amount > 0:
            is_high = group["amount"] > (avg_amount * AMOUNT_MULTIPLIER_THRESHOLD)
            df.loc[group.index[is_high], "amount_flag"] = True

    return df


def run_rule_based_detection(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = detect_velocity_spikes(df)
    df = detect_amount_anomalies(df)
    df["rule_flag"] = df["velocity_flag"] | df["amount_flag"]
    return df


if __name__ == "__main__":
    df = pd.read_csv("transactions.csv")
    result = run_rule_based_detection(df)

    flagged = result[result["rule_flag"] == True]
    print(f"Total transactions: {len(result)}")
    print(f"Flagged by rules: {len(flagged)}")
    print()
    print("Sample flagged transactions:")
    print(flagged[["user_id", "amount", "timestamp", "velocity_flag", "amount_flag"]].head(10).to_string(index=False))