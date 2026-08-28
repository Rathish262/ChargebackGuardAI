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

    probabilities = model.predict_proba(X)[0]

    ml_confidence = max(probabilities)

    evidence = evidence_engine.analyze(case)

    final_result = decision_engine.decide(
        case,
        ml_prediction
    )

    return (
        ml_prediction,
        ml_confidence,
        evidence,
        final_result
    )


# ==========================================
# ERROR COLLECTION
# ==========================================

ml_errors = []
final_errors = []


# ==========================================
# ANALYZE ALL TEST CASES
# ==========================================

for _, row in test_df.iterrows():

    case = row.to_dict()

    actual = case["ground_truth"]

    (
        ml_prediction,
        ml_confidence,
        evidence,
        result
    ) = analyze_case(case)

    final_prediction = result["decision"]


    # --------------------------------------
    # ML ERROR
    # --------------------------------------

    if actual != ml_prediction:

        ml_errors.append({

            "dispute_id":
                case["dispute_id"],

            "scenario":
                case["scenario"],

            "amount":
                case["amount"],

            "reason":
                case["reason"],

            "delivery_status":
                case["delivery_status"],

            "delivery_proof":
                case["delivery_proof"],

            "refund_status":
                case["refund_status"],

            "ground_truth":
                actual,

            "ml_prediction":
                ml_prediction,

            "ml_confidence":
                round(
                    ml_confidence * 100,
                    2
                ),

            "final_decision":
                final_prediction,

            "evidence_score":
                evidence["evidence_score"],

            "evidence_level":
                evidence["evidence_level"],

            "contradiction_detected":
                evidence[
                    "contradiction_detected"
                ],

            "decision_reason":
                result["reason"]
        })


    # --------------------------------------
    # FINAL SYSTEM ERROR
    # --------------------------------------

    if actual != final_prediction:

        final_errors.append({

            "dispute_id":
                case["dispute_id"],

            "scenario":
                case["scenario"],

            "amount":
                case["amount"],

            "reason":
                case["reason"],

            "delivery_status":
                case["delivery_status"],

            "delivery_proof":
                case["delivery_proof"],

            "refund_status":
                case["refund_status"],

            "ground_truth":
                actual,

            "ml_prediction":
                ml_prediction,

            "final_decision":
                final_prediction,

            "evidence_score":
                evidence["evidence_score"],

            "evidence_level":
                evidence["evidence_level"],

            "contradiction_detected":
                evidence[
                    "contradiction_detected"
                ],

            "decision_reason":
                result["reason"]
        })


# ==========================================
# ML ERROR SUMMARY
# ==========================================

print("===== ML ERROR SUMMARY =====")

print()

print(
    "Total ML errors:",
    len(ml_errors)
)

print(
    "ML correct predictions:",
    len(test_df) - len(ml_errors)
)

ml_accuracy = (
    (len(test_df) - len(ml_errors))
    / len(test_df)
) * 100

print(
    f"ML accuracy from error analysis: "
    f"{ml_accuracy:.2f}%"
)

print()


# ==========================================
# ML ERROR BREAKDOWN
# ==========================================

if ml_errors:

    ml_error_df = pd.DataFrame(
        ml_errors
    )

    print(
        "===== ML ERROR BREAKDOWN ====="
    )

    print()

    print(
        ml_error_df[
            [
                "ground_truth",
                "ml_prediction"
            ]
        ].value_counts()
    )

    print()


    # ======================================
    # FIRST 20 ML ERRORS
    # ======================================

    print(
        "===== FIRST 20 ML ERRORS ====="
    )

    print()

    for _, error in (
        ml_error_df
        .head(20)
        .iterrows()
    ):

        print(
            "----------------------------------------"
        )

        print(
            "Dispute ID:",
            error["dispute_id"]
        )

        print(
            "Scenario:",
            error["scenario"]
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
            "ML Confidence:",
            f'{error["ml_confidence"]}%'
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
            "Contradiction:",
            error["contradiction_detected"]
        )

        print(
            "Decision Reason:",
            error["decision_reason"]
        )

        print(
            "----------------------------------------"
        )

    ml_error_df.to_csv(
        "data/test/ml_error_cases.csv",
        index=False
    )

    print()

    print(
        "ML error cases saved to:",
        "data/test/ml_error_cases.csv"
    )

else:

    print(
        "No ML errors found."
    )


print()


# ==========================================
# FINAL SYSTEM ERROR SUMMARY
# ==========================================

print(
    "===== FINAL SYSTEM ERROR SUMMARY ====="
)

print()

print(
    "Total final decision errors:",
    len(final_errors)
)

print(
    "Final correct decisions:",
    len(test_df) - len(final_errors)
)

final_accuracy = (
    (len(test_df) - len(final_errors))
    / len(test_df)
) * 100

print(
    f"Final system accuracy: "
    f"{final_accuracy:.2f}%"
)

print()


# ==========================================
# FINAL ERROR BREAKDOWN
# ==========================================

if final_errors:

    final_error_df = pd.DataFrame(
        final_errors
    )

    print(
        "===== FINAL ERROR BREAKDOWN ====="
    )

    print()

    print(
        final_error_df[
            [
                "ground_truth",
                "final_decision"
            ]
        ].value_counts()
    )

    print()


    final_error_df.to_csv(
        "data/test/final_error_cases.csv",
        index=False
    )

    print(
        "Final error cases saved to:",
        "data/test/final_error_cases.csv"
    )

else:

    print(
        "No final decision errors found."
    )


print()

print(
    "===== ERROR ANALYSIS COMPLETED ====="
)