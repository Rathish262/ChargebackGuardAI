import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"


print("===== CHARGEBACKGUARD AI =====")
print("Loading AI system...")


# ==========================================
# LOAD MODEL
# ==========================================

saved_model = joblib.load(MODEL_FILE)

print("Model loaded successfully.")


# Our train_model.py saved the model
# inside a dictionary.
# Find the actual model automatically.

if isinstance(saved_model, dict):

    print("Saved model type: dictionary")
    print("Available keys:", list(saved_model.keys()))

    if "model" in saved_model:
        model = saved_model["model"]

    elif "classifier" in saved_model:
        model = saved_model["classifier"]

    else:
        raise ValueError(
            "Could not find trained model inside saved dictionary."
        )

else:

    print("Saved model type: direct model")
    model = saved_model


# ==========================================
# INITIALIZE ENGINES
# ==========================================

evidence_engine = EvidenceEngine()
decision_engine = DecisionEngine()


# ==========================================
# PREPARE FEATURES
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

    # Convert delivery proof to numeric

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

    # Convert categorical columns

    features = pd.get_dummies(
        features,
        columns=[
            "delivery_status",
            "refund_status",
            "reason"
        ]
    )

    # IMPORTANT:
    # Use the exact feature columns used during training

    feature_columns = saved_model["feature_columns"]

    features = features.reindex(
        columns=feature_columns,
        fill_value=0
    )

    return features
# ==========================================
# ANALYZE ONE DISPUTE
# ==========================================

def analyze_dispute(case):

    # --------------------------------------
    # ML prediction
    # --------------------------------------

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    # --------------------------------------
    # Evidence analysis
    # --------------------------------------

    evidence_result = evidence_engine.analyze(case)

    # --------------------------------------
    # Final safety decision
    # --------------------------------------

    final_result = decision_engine.decide(
        case,
        ml_prediction
    )

    return {

        "dispute_id":
            case["dispute_id"],

        "amount":
            case["amount"],

        "ml_prediction":
            ml_prediction,

        "evidence_score":
            evidence_result["evidence_score"],

        "evidence_level":
            evidence_result["evidence_level"],

        "contradiction_detected":
            evidence_result["contradiction_detected"],

        "final_decision":
            final_result["decision"],

        "decision_reason":
            final_result["reason"],

        "reasons":
            evidence_result["reasons"],

        "warnings":
            final_result["warnings"]
    }


# ==========================================
# TEST COMPLETE PIPELINE
# ==========================================

if __name__ == "__main__":

    print("AI system loaded successfully.")
    print()

    test_df = pd.read_csv(TEST_FILE)

    print(
        "Testing complete pipeline on:",
        len(test_df),
        "cases"
    )

    print()

    # Test first case

    case = test_df.iloc[0].to_dict()

    result = analyze_dispute(case)

    print("===== DISPUTE ANALYSIS =====")
    print()

    print(
        "Dispute ID:",
        result["dispute_id"]
    )

    print(
        "Amount: ₹",
        result["amount"]
    )

    print()

    print(
        "ML Prediction:",
        result["ml_prediction"]
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
        result["contradiction_detected"]
    )

    print()

    print(
        "FINAL DECISION:",
        result["final_decision"]
    )

    print(
        "Decision Reason:",
        result["decision_reason"]
    )

    print()

    print("Evidence Reasons:")

    for reason in result["reasons"]:

        print(" -", reason)

    print()

    print("Warnings:")

    if result["warnings"]:

        for warning in result["warnings"]:

            print(" ⚠", warning)

    else:

        print(" None")

    print()

    print("===== ANALYSIS COMPLETED =====")