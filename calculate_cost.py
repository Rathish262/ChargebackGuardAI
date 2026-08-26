import pandas as pd
import joblib


TEST_FILE = "data/test/held_out_test.csv"
MODEL_FILE = "models/chargeback_model.pkl"


# Evaluation assumptions
CONTEST_FALSE_POSITIVE_COST = 100
DO_NOT_CONTEST_FALSE_NEGATIVE_COST = 500


print("===== CHARGEBACKGUARD AI =====")
print("FALSE-POSITIVE COST EVALUATION")
print()


# Load test data
test_df = pd.read_csv(TEST_FILE)

print("Held-out test cases:", len(test_df))


# Load model
package = joblib.load(MODEL_FILE)

model = package["model"]
feature_columns = package["feature_columns"]


# Prepare features
features = test_df[
    [
        "amount",
        "delivery_status",
        "delivery_proof",
        "refund_status",
        "reason"
    ]
].copy()


# Convert delivery proof
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


# Match training columns
X_test = features.reindex(
    columns=feature_columns,
    fill_value=0
)


y_test = test_df["ground_truth"]


# Predictions
predictions = model.predict(X_test)


# ------------------------------------------------
# FALSE POSITIVE
# ------------------------------------------------
#
# AI says CONTEST
# BUT ground truth is NOT CONTEST
#
# These are cases where AI recommends fighting
# a dispute when it should not.
# ------------------------------------------------

false_positives = (
    (predictions == "CONTEST") &
    (y_test != "CONTEST")
)

fp_count = false_positives.sum()


# ------------------------------------------------
# FALSE NEGATIVE
# ------------------------------------------------
#
# AI does NOT say CONTEST
# BUT ground truth says CONTEST
#
# These represent potentially missed
# contestable disputes.
# ------------------------------------------------

false_negatives = (
    (predictions != "CONTEST") &
    (y_test == "CONTEST")
)

fn_count = false_negatives.sum()


# Calculate costs

false_positive_cost = (
    fp_count * CONTEST_FALSE_POSITIVE_COST
)

false_negative_cost = (
    fn_count * DO_NOT_CONTEST_FALSE_NEGATIVE_COST
)

total_cost = (
    false_positive_cost +
    false_negative_cost
)


print()
print("===== RESULTS =====")

print("False positives:", fp_count)

print("False-positive cost:")
print(
    "₹",
    false_positive_cost
)

print()

print("False negatives:", fn_count)

print("False-negative cost:")
print(
    "₹",
    false_negative_cost
)

print()

print("Total modeled decision cost:")
print(
    "₹",
    total_cost
)


print()
print("===== INTERPRETATION =====")

print(
    "False positive = AI recommended CONTEST "
    "when the ground truth was not CONTEST."
)

print(
    "False negative = AI did not recommend CONTEST "
    "when the ground truth was CONTEST."
)

print()
print("Evaluation assumptions:")
print(
    "CONTEST false-positive cost = ₹",
    CONTEST_FALSE_POSITIVE_COST
)

print(
    "Missed-CONTEST cost = ₹",
    DO_NOT_CONTEST_FALSE_NEGATIVE_COST
)

print()
print("NOTE:")
print(
    "These costs are evaluation assumptions, "
    "not actual Razorpay fees."
)