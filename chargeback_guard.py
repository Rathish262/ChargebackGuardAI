import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


MODEL_FILE = "models/chargeback_model.pkl"


class ChargebackGuard:

    def __init__(self):

        # Load trained model
        saved_model = joblib.load(MODEL_FILE)

        if isinstance(saved_model, dict):

            self.model = saved_model["model"]
            self.feature_columns = saved_model["feature_columns"]

        else:

            self.model = saved_model
            self.feature_columns = None

        # Initialize engines
        self.evidence_engine = EvidenceEngine()
        self.decision_engine = DecisionEngine()


    # ==========================================
    # FEATURE PREPARATION
    # ==========================================

    def prepare_features(self, case):

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
            .str.strip()
            .str.lower()
            .map({
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

        # Match training features
        if self.feature_columns is not None:

            features = features.reindex(
                columns=self.feature_columns,
                fill_value=0
            )

        return features


    # ==========================================
    # ANALYZE ONE DISPUTE
    # ==========================================

    def analyze(self, case):

        # --------------------------------------
        # 1. ML PREDICTION
        # --------------------------------------

        X = self.prepare_features(case)

        ml_prediction = self.model.predict(X)[0]

        # --------------------------------------
        # 2. ML CONFIDENCE
        # --------------------------------------

        ml_confidence = None

        if hasattr(self.model, "predict_proba"):

            probabilities = self.model.predict_proba(X)[0]

            ml_confidence = float(
                max(probabilities) * 100
            )

        # --------------------------------------
        # 3. EVIDENCE ANALYSIS
        # --------------------------------------

        evidence = self.evidence_engine.analyze(
            case
        )

        # --------------------------------------
        # 4. FINAL DECISION
        # --------------------------------------

        final_result = self.decision_engine.decide(
            case,
            ml_prediction
        )

        # --------------------------------------
        # 5. COMBINED RESULT
        # --------------------------------------

        return {

            "dispute_id":
                case.get("dispute_id", ""),

            "amount":
                case.get("amount", 0),

            "ml_prediction":
                ml_prediction,

            "ml_confidence":
                ml_confidence,

            "evidence_score":
                evidence["evidence_score"],

            "evidence_level":
                evidence["evidence_level"],

            "contradiction_detected":
                evidence["contradiction_detected"],

            "final_decision":
                final_result["decision"],

            "decision_reason":
                final_result["reason"],

            "reasons":
                evidence["reasons"],

            "warnings":
                final_result["warnings"],

            "evidence_breakdown":
                evidence.get(
                    "evidence_breakdown",
                    {}
                )
        }


# ==========================================
# SIMPLE TEST
# ==========================================

if __name__ == "__main__":

    print(
        "===== CHARGEBACKGUARD AI ====="
    )

    print(
        "Central Pipeline Test"
    )

    print()

    test_case = {

        "dispute_id":
            "PIPELINE_TEST",

        "amount":
            5000,

        "reason":
            "product_not_received",

        "delivery_status":
            "delivered",

        "delivery_proof":
            True,

        "refund_status":
            "not_issued",

        "customer_message":
            "I did not receive my order.",

        "merchant_message":
            "Delivery was completed and proof is available."
    }

    guard = ChargebackGuard()

    result = guard.analyze(
        test_case
    )

    print(
        "Dispute ID:",
        result["dispute_id"]
    )

    print(
        "ML Prediction:",
        result["ml_prediction"]
    )

    if result["ml_confidence"] is not None:

        print(
            "ML Confidence:",
            f"{result['ml_confidence']:.1f}%"
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
        "Reason:",
        result["decision_reason"]
    )

    print()

    print("Warnings:")

    if result["warnings"]:

        for warning in result["warnings"]:

            print(
                " -",
                warning
            )

    else:

        print(" - None")

    print()

    print(
        "===== TEST COMPLETED ====="
    )