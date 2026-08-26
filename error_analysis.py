import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"


print("===== CHARGEBACKGUARD AI =====")
print("ERROR ANALYSIS")
print()


# ==========================================
# LOAD MODEL
# ==========================================

saved_model = joblib.load(MODEL_FILE)

model = saved_model["model"]
feature_columns = saved_model["feature_columns"]

print("Model loaded successfully.")


# ==========================================
# FEATURE PREPARATION
# ==========================================

def prepare_features(case):

    df = pd.DataFrame([case])

    features = df[
        [
            "amount",
            "delivery_status",
            "delivery_proof",
            "refund_status",
            "reason"
        ]
    ].copy()

    features["delivery_proof"] = (
        features["delivery_proof"]
        .astype(str)
        .map({
            "True": 1,
            "False": 0,
            "true": 1,
            "false": 0
        })
    )

    features = pd.get_dummies(
        features,
        columns=[
            "delivery_status",
            "refund_status",
            "reason"
        ]
    )

    features = features.reindex(
        columns=feature_columns,
        fill_value=0
    )

    return features


# ==========================================
# LOAD TEST DATA
# ==========================================

test_df = pd.read_csv(TEST_FILE)

print(
    "Held-out test cases:",
    len(test_df)
)

print()


# ==========================================
# INITIALIZE ENGINES
# ==========================================

evidence_engine = EvidenceEngine()
decision_engine = DecisionEngine()


# ==========================================
# ANALYZE CASE
# ==========================================

def analyze_case(case):

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    evidence = evidence_engine.analyze(case)

    final_result = decision_engine.decide(
        case,
        ml_prediction
    )

    return (
        ml_prediction,
        final_result
    )


# ==========================================
# FIND ERRORS
# ==========================================

errors = []


for _, row in test_df.iterrows():

    case = row.to_dict()

    actual = case["ground_truth"]

    ml_prediction, result = analyze_case(case)

    final_prediction = result["decision"]

    if actual != final_prediction:

        errors.append({

            "dispute_id": case["dispute_id"],

            "amount": case["amount"],

            "scenario": case["scenario"],

            "reason": case["reason"],

            "delivery_status": case["delivery_status"],

            "delivery_proof": case["delivery_proof"],

            "refund_status": case["refund_status"],

            "ground_truth": actual,

            "ml_prediction": ml_prediction,

            "final_decision": final_prediction,

            "evidence_score":
                result["evidence_score"],

            "evidence_level":
                result["evidence_level"],

            "decision_reason":
                result["reason"]
        })


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("===== ERROR SUMMARY =====")

print()

print(
    "Total errors:",
    len(errors)
)

print()


# ==========================================
# ERROR BREAKDOWN
# ==========================================

if errors:

    error_df = pd.DataFrame(errors)

    print("===== ERROR BREAKDOWN =====")

    print()

    print(
        error_df[
            [
                "ground_truth",
                "final_decision"
            ]
        ].value_counts()
    )

    print()


    # ======================================
    # SHOW FIRST 20 ERRORS
    # ======================================

    print("===== FIRST 20 ERRORS =====")

    print()

    for _, error in error_df.head(20).iterrows():

        print("----------------------------------------")

        print(
            "Dispute ID:",
            error["dispute_id"]
        )

        print(
            "Scenario:",
            error["scenario"]
        )

        print(
            "Reason:",
            error["reason"]
        )

        print(
            "Ground Truth:",
            error["ground_truth"]
        )

        print(
            "ML Prediction:",
            error["ml_prediction"]
        )

        print(
            "Final Decision:",
            error["final_decision"]
        )

        print(
            "Evidence Score:",
            error["evidence_score"]
        )

        print(
            "Evidence Level:",
            error["evidence_level"]
        )

        print(
            "Decision Reason:",
            error["decision_reason"]
        )

        print("----------------------------------------")


    # ======================================
    # SAVE ERRORS
    # ======================================

    error_df.to_csv(
        "data/test/error_cases.csv",
        index=False
    )

    print()

    print(
        "Error cases saved to:",
        "data/test/error_cases.csv"
    )

else:

    print("No errors found.")


print()

print("===== ERROR ANALYSIS COMPLETED =====")