from evidence_engine import EvidenceEngine


class DecisionEngine:

    def __init__(self):

        self.evidence_engine = EvidenceEngine()

    # ==========================================
    # DECIDE
    # ==========================================

    def decide(self, case, ml_prediction):

        evidence = self.evidence_engine.analyze(case)

        score = evidence["evidence_score"]

        evidence_level = evidence["evidence_level"]

        contradiction = evidence["contradiction_detected"]

        warnings = evidence["warnings"]

        delivery_status = str(
            case.get("delivery_status", "")
        ).strip().lower()

        delivery_proof = str(
            case.get("delivery_proof", "")
        ).strip().lower()

        refund_status = str(
            case.get("refund_status", "")
        ).strip().lower()

        reason = str(
            case.get("reason", "")
        ).strip().lower()

        # ==========================================
        # 1. CONTRADICTION SAFETY RULE
        # ==========================================

        if contradiction:

            return self._result(
                decision="HUMAN_REVIEW",
                reason="Conflicting evidence detected",
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 2. REFUND SAFETY
        # ==========================================

        if refund_status == "issued":

            return self._result(
                decision="DO_NOT_CONTEST",
                reason="Refund has already been issued",
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 3. DELIVERY FAILURE
        # ==========================================

        if (
            delivery_status == "failed"
            and reason == "product_not_received"
        ):

            return self._result(
                decision="DO_NOT_CONTEST",
                reason=(
                    "Delivery failed and supports "
                    "the non-receipt claim"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 4. UNAUTHORIZED TRANSACTION
        # ==========================================

        if reason == "unauthorized_transaction":

            return self._result(
                decision="HUMAN_REVIEW",
                reason=(
                    "Unauthorized transaction "
                    "requires verification"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 5. DUPLICATE CHARGE
        # ==========================================

        if reason == "duplicate_charge":

            return self._result(
                decision="HUMAN_REVIEW",
                reason=(
                    "Duplicate charge requires "
                    "transaction verification"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 6. STRONG DELIVERY EVIDENCE
        # ==========================================

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and score >= 90
        ):

            return self._result(
                decision="CONTEST",
                reason=(
                    "Strong delivery evidence "
                    "supports contesting"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 7. ML DO NOT CONTEST
        # ==========================================

        if ml_prediction == "DO_NOT_CONTEST":

            return self._result(
                decision="DO_NOT_CONTEST",
                reason=(
                    "Risk model recommends "
                    "not contesting"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 8. WEAK EVIDENCE
        # ==========================================

        if score < 40:

            return self._result(
                decision="HUMAN_REVIEW",
                reason="Evidence strength is too weak",
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 9. ML HUMAN REVIEW
        # ==========================================

        if ml_prediction == "HUMAN_REVIEW":

            return self._result(
                decision="HUMAN_REVIEW",
                reason=(
                    "Risk model recommends "
                    "human verification"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 10. ML CONTEST
        # ==========================================

        if ml_prediction == "CONTEST":

            return self._result(
                decision="CONTEST",
                reason=(
                    "Risk model recommends "
                    "contesting the dispute"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 11. SAFE DEFAULT
        # ==========================================

        return self._result(
            decision="HUMAN_REVIEW",
            reason="Case requires human verification",
            score=score,
            level=evidence_level,
            warnings=warnings
        )

    # ==========================================
    # RESULT HELPER
    # ==========================================

    @staticmethod
    def _result(
        decision,
        reason,
        score,
        level,
        warnings
    ):

        return {

            "decision": decision,

            "reason": reason,

            "evidence_score": score,

            "evidence_level": level,

            "warnings": warnings
        }


# ==========================================
# LOCAL TEST
# ==========================================

if __name__ == "__main__":

    engine = DecisionEngine()

    test_cases = [

        {
            "name":
                "STRONG DELIVERY",

            "case": {

                "dispute_id":
                    "STRONG_TEST",

                "amount":
                    5000,

                "reason":
                    "product_not_received",

                "delivery_status":
                    "delivered",

                "delivery_proof":
                    "True",

                "refund_status":
                    "not_issued",

                "customer_message":
                    "I did not receive my order.",

                "merchant_message":
                    "Delivery was completed and proof is available."
            },

            "ml_prediction":
                "CONTEST"
        },

        {
            "name":
                "STRONG DELIVERY + ML HUMAN REVIEW",

            "case": {

                "dispute_id":
                    "STRONG_ML_REVIEW_TEST",

                "amount":
                    5000,

                "reason":
                    "product_not_received",

                "delivery_status":
                    "delivered",

                "delivery_proof":
                    "True",

                "refund_status":
                    "not_issued",

                "customer_message":
                    "I did not receive my order.",

                "merchant_message":
                    "Delivery was completed and proof is available."
            },

            "ml_prediction":
                "HUMAN_REVIEW"
        },

        {
            "name":
                "CONTRADICTORY",

            "case": {

                "dispute_id":
                    "CONTRADICTION_TEST",

                "amount":
                    5000,

                "reason":
                    "product_not_received",

                "delivery_status":
                    "delivered",

                "delivery_proof":
                    "True",

                "refund_status":
                    "not_issued",

                "customer_message":
                    "I did not receive my order.",

                "merchant_message":
                    "Customer previously confirmed that the order was received."
            },

            "ml_prediction":
                "CONTEST"
        },

        {
            "name":
                "DELIVERY FAILURE",

            "case": {

                "dispute_id":
                    "FAILURE_TEST",

                "amount":
                    5000,

                "reason":
                    "product_not_received",

                "delivery_status":
                    "failed",

                "delivery_proof":
                    "False",

                "refund_status":
                    "not_issued",

                "customer_message":
                    "I did not receive my order.",

                "merchant_message":
                    "Delivery attempt failed."
            },

            "ml_prediction":
                "DO_NOT_CONTEST"
        }
    ]

    print(
        "===== CHARGEBACKGUARD AI ====="
    )

    print(
        "Decision Engine Test"
    )

    print()

    for item in test_cases:

        result = engine.decide(
            item["case"],
            item["ml_prediction"]
        )

        print(
            "----------------------------------------"
        )

        print(
            "Test:",
            item["name"]
        )

        print(
            "ML Prediction:",
            item["ml_prediction"]
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
            "Final Decision:",
            result["decision"]
        )

        print(
            "Reason:",
            result["reason"]
        )

        print()

    print(
        "===== TEST COMPLETED ====="
    )