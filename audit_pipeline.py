
from datetime import datetime


class AuditPipeline:

    def __init__(self, evidence_engine, decision_engine):
        self.evidence_engine = evidence_engine
        self.decision_engine = decision_engine

    def analyze(self, case, ml_prediction, ml_confidence=None):

        # ==========================================
        # 1. EVIDENCE ANALYSIS
        # ==========================================

        evidence = self.evidence_engine.analyze(case)

        # ==========================================
        # 2. FINAL DECISION
        # ==========================================

        decision = self.decision_engine.decide(
            case,
            ml_prediction
        )

        # ==========================================
        # 3. AUDIT RECORD
        # ==========================================

        audit_record = {

            "timestamp":
                datetime.now().isoformat(),

            "dispute_id":
                case.get("dispute_id", ""),

            "amount":
                case.get("amount", 0),

            "reason":
                case.get("reason", ""),

            # ------------------------------
            # ML
            # ------------------------------

            "ml_prediction":
                ml_prediction,

            "ml_confidence":
                ml_confidence,

            # ------------------------------
            # Evidence
            # ------------------------------

            "evidence_score":
                evidence["evidence_score"],

            "evidence_level":
                evidence["evidence_level"],

            "contradiction_detected":
                evidence["contradiction_detected"],

            "evidence_breakdown":
                evidence["evidence_breakdown"],

            "evidence_reasons":
                evidence["reasons"],

            "warnings":
                evidence["warnings"],

            # ------------------------------
            # Final Decision
            # ------------------------------

            "final_decision":
                decision["decision"],

            "decision_reason":
                decision["reason"]
        }

        return audit_record


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from evidence_engine import EvidenceEngine
    from decision_engine import DecisionEngine

    evidence_engine = EvidenceEngine()
    decision_engine = DecisionEngine()

    pipeline = AuditPipeline(
        evidence_engine,
        decision_engine
    )

    test_case = {

        "dispute_id":
            "AUDIT_TEST",

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

    result = pipeline.analyze(
        test_case,
        ml_prediction="CONTEST",
        ml_confidence=0.98
    )

    print("===== CHARGEBACKGUARD AI =====")
    print("AUDIT PIPELINE TEST")
    print()

    print("Dispute ID:",
          result["dispute_id"])

    print("ML Prediction:",
          result["ml_prediction"])

    print("ML Confidence:",
          result["ml_confidence"])

    print("Evidence Score:",
          result["evidence_score"])

    print("Evidence Level:",
          result["evidence_level"])

    print("Contradiction:",
          result["contradiction_detected"])

    print("Final Decision:",
          result["final_decision"])

    print("Decision Reason:",
          result["decision_reason"])

    print()

    print("===== AUDIT TEST COMPLETED =====")

