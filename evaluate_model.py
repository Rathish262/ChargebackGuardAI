import pandas as pd
import joblib

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


TEST_FILE = "data/test/held_out_test.csv"
MODEL_FILE = "models/chargeback_model.pkl"


print("===== CHARGEBACKGUARD AI =====")
print("Loading held-out test dataset...")

test_df = pd.read_csv(TEST_FILE)

print("Held-out test cases:", len(test_df))


# Load saved model package
package = joblib.load(MODEL_FILE)

model = package["model"]
feature_columns = package["feature_columns"]


# Prepare test features
features = test_df[
    [
        "amount",
        "delivery_status",
        "delivery_proof",
        "refund_status",
        "reason"
    ]
].copy()


# Convert boolean delivery proof
features["delivery_proof"] = (
    features["delivery_proof"]
    .astype(str)
    .map({
        "True": 1,
        "False": 0
    })
)


# Convert categorical features
features = pd.get_dummies(
    features,
    columns=[
        "delivery_status",
        "refund_status",
        "reason"
    ]
)


# Make test columns identical to training columns
X_test = features.reindex(
    columns=feature_columns,
    fill_value=0
)


y_test = test_df["ground_truth"]


# Predict
predictions = model.predict(X_test)


print()
print("===== HELD-OUT TEST RESULTS =====")

print()
print("Accuracy:")
print(round(accuracy_score(y_test, predictions), 4))


print()
print("===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_test,
        predictions,
        labels=[
            "CONTEST",
            "DO_NOT_CONTEST",
            "HUMAN_REVIEW"
        ],
        zero_division=0
    )
)


print("===== CONFUSION MATRIX =====")

labels = [
    "CONTEST",
    "DO_NOT_CONTEST",
    "HUMAN_REVIEW"
]

matrix = confusion_matrix(
    y_test,
    predictions,
    labels=labels
)

print("Labels:", labels)
print(matrix)


print()
print("===== TEST COMPLETED =====")