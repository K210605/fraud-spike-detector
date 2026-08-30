import pandas as pd
from detector_combined import run_combined_detection

KNOWN_FRAUD_USER_1 = "user_007"
KNOWN_FRAUD_USER_2 = "user_022"


def label_ground_truth(df):
    df = df.copy()
    df["is_actual_fraud"] = False

    df.loc[
        (df["user_id"] == KNOWN_FRAUD_USER_1) & (df["amount"] >= 10) & (df["amount"] <= 50),
        "is_actual_fraud"
    ] = True

    df.loc[
        (df["user_id"] == KNOWN_FRAUD_USER_2) & (df["amount"] == 45000.00),
        "is_actual_fraud"
    ] = True

    return df


def calculate_metrics(df):
    true_positives = len(df[(df["is_actual_fraud"] == True) & (df["final_flag"] == True)])
    false_positives = len(df[(df["is_actual_fraud"] == False) & (df["final_flag"] == True)])
    false_negatives = len(df[(df["is_actual_fraud"] == True) & (df["final_flag"] == False)])
    true_negatives = len(df[(df["is_actual_fraud"] == False) & (df["final_flag"] == False)])

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (true_positives + true_negatives) / len(df)

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_negatives": true_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1_score, 3),
        "accuracy": round(accuracy, 3)
    }


if __name__ == "__main__":
    df = pd.read_csv("transactions.csv")
    df = label_ground_truth(df)

    result = run_combined_detection(df)

    metrics = calculate_metrics(result)

    print("=== Model Evaluation ===")
    print(f"True Positives (correctly caught fraud):  {metrics['true_positives']}")
    print(f"False Positives (false alarms):            {metrics['false_positives']}")
    print(f"False Negatives (missed fraud):             {metrics['false_negatives']}")
    print(f"True Negatives (correctly ignored normal):  {metrics['true_negatives']}")
    print()
    print(f"Precision: {metrics['precision']}")
    print(f"Recall:    {metrics['recall']}")
    print(f"F1 Score:  {metrics['f1_score']}")
    print(f"Accuracy:  {metrics['accuracy']}")