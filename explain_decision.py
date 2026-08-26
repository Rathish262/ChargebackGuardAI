import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"


# ==========================================
# LOAD MODEL
# ==========================================

print("===== CHARGEBACKGUARD AI =====")
print("DECISION EXPLANATION ENGINE")
print()

saved_model = joblib.load(MODEL_FILE)

if isinstance(saved_model, dict):

    model = saved_model["model"]
    feature_columns = saved_model["feature_columns"]

else:

    model = saved_model
    feature_columns = None

print("Model loaded successfully.")
print()


# ==========================================
# INITIALIZE ENGINES
# ==========================================

evidence_engine = EvidenceEngine()
decision_engine = DecisionEngine()


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

    if feature_columns is not None:

        features = features.reindex(
            columns=feature_columns,
            fill_value=0
        )

    return features


# ==========================================
# ANALYZE CASE
# ==========================================

def analyze_case(case):

    # --------------------------------------
    # ML PREDICTION
    # --------------------------------------

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    # --------------------------------------
    # ML CONFIDENCE
    # --------------------------------------

    probabilities = model.predict_proba(X)[0]

    classes = model.classes_

    probability_map = dict(
        zip(classes, probabilities)
    )

    ml_confidence = probability_map.get(
        ml_prediction,
        0
    )

    # --------------------------------------
    # EVIDENCE ANALYSIS
    # --------------------------------------

    evidence = evidence_engine.analyze(case)

    # --------------------------------------
    # FINAL DECISION
    # --------------------------------------

    decision = decision_engine.decide(
        case,
        ml_prediction
    )

    return {

        "ml_prediction": ml_prediction,

        "ml_confidence": ml_confidence,

        "evidence_score":
            evidence["evidence_score"],

        "evidence_level":
            evidence["evidence_level"],

        "contradiction":
            evidence["contradiction_detected"],

        "evidence_reasons":
            evidence["reasons"],

        "warnings":
            evidence["warnings"],

        "final_decision":
            decision["decision"],

        "decision_reason":
            decision["reason"]
    }


# ==========================================
# LOAD TEST DATA
# ==========================================

print("Loading held-out test dataset...")

test_df = pd.read_csv(TEST_FILE)

print(
    "Held-out test cases:",
    len(test_df)
)

print()


# ==========================================
# SELECT IMPORTANT CASES
# ==========================================

cases_to_explain = []


# Find a CONTEST case

contest_cases = test_df[
    test_df["ground_truth"] == "CONTEST"
]

if len(contest_cases) > 0:

    cases_to_explain.append(
        contest_cases.iloc[0]
    )


# Find a DO_NOT_CONTEST case

not_contest_cases = test_df[
    test_df["ground_truth"] == "DO_NOT_CONTEST"
]

if len(not_contest_cases) > 0:

    cases_to_explain.append(
        not_contest_cases.iloc[0]
    )


# Find a HUMAN_REVIEW case

review_cases = test_df[
    test_df["ground_truth"] == "HUMAN_REVIEW"
]

if len(review_cases) > 0:

    cases_to_explain.append(
        review_cases.iloc[0]
    )


# ==========================================
# DISPLAY EXPLANATIONS
# ==========================================

for row in cases_to_explain:

    case = row.to_dict()

    result = analyze_case(case)

    print("=" * 60)

    print(
        "DISPUTE ID:",
        case["dispute_id"]
    )

    print(
        "GROUND TRUTH:",
        case["ground_truth"]
    )

    print()

    print(
        "Amount: ₹",
        case["amount"]
    )

    print(
        "Reason:",
        case["reason"]
    )

    print(
        "Delivery Status:",
        case["delivery_status"]
    )

    print(
        "Delivery Proof:",
        case["delivery_proof"]
    )

    print(
        "Refund Status:",
        case["refund_status"]
    )

    print()

    print("----- AI ANALYSIS -----")

    print(
        "ML Prediction:",
        result["ml_prediction"]
    )

    print(
        "ML Confidence:",
        round(
            result["ml_confidence"] * 100,
            2
        ),
        "%"
    )

    print(
        "Evidence Score:",
        result["evidence_score"],
        "/ 100"
    )

    print(
        "Evidence Level:",
        result["evidence_level"]
    )

    print(
        "Contradiction:",
        result["contradiction"]
    )

    print()

    print("Evidence Reasons:")

    if result["evidence_reasons"]:

        for reason in result["evidence_reasons"]:

            print(
                " -",
                reason
            )

    else:

        print(" None")

    print()

    print("Warnings:")

    if result["warnings"]:

        for warning in result["warnings"]:

            print(
                " ⚠",
                warning
            )

    else:

        print(" None")

    print()

    print("FINAL DECISION:")

    print(
        result["final_decision"]
    )

    print()

    print("DECISION REASON:")

    print(
        result["decision_reason"]
    )

    print()


print("=" * 60)

print("===== EXPLANATION COMPLETED =====")