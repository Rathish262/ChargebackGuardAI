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

        customer_message = str(
            case.get("customer_message", "")
        ).strip().lower()

        merchant_message = str(
            case.get("merchant_message", "")
        ).strip().lower()

        ml_prediction = str(
            ml_prediction
        ).strip().upper()
                 # ==========================================
        # INPUT VALIDATION
        # ==========================================

        if not reason:

            return self._result(
                decision="HUMAN_REVIEW",
                reason="Dispute reason is missing",
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 1. EXPLICIT COMMUNICATION CONFLICT
        # ==========================================
        #
        # Detect cases where the customer currently
        # denies receiving the order, but the evidence
        # says the customer previously confirmed receipt.
        #
        # These cases must go to HUMAN_REVIEW.
        # ==========================================

        customer_denies_receipt = any(
            phrase in customer_message
            for phrase in [
                "did not receive",
                "didn't receive",
                "never received",
                "not received",
                "did not get",
                "didn't get",
                "never got"
            ]
        )

        customer_previous_confirmation = any(
            phrase in customer_message
            for phrase in [
                "previously confirmed",
                "previously said",
                "previously stated",
                "earlier confirmed",
                "earlier said",
                "earlier stated",
                "confirmed that the order was received",
                "confirmed that the product was received",
                "confirmed receipt"
            ]
        )

        merchant_confirms_receipt = any(
            phrase in merchant_message
            for phrase in [
                "customer confirmed receipt",
                "customer confirmed",
                "confirmed receipt",
                "customer received the product",
                "customer received the order",
                "customer has received the product",
                "customer has received the order",
                "customer previously confirmed receipt",
                "customer previously confirmed that the order was received"
            ]
        )

        explicit_conflict = (
            customer_denies_receipt
            and (
                customer_previous_confirmation
                or merchant_confirms_receipt
            )
        )

        # ==========================================
        # 2. CRITICAL SAFETY RULE
        # ==========================================

        if contradiction or explicit_conflict:

            return self._result(
                decision="HUMAN_REVIEW",
                reason="Conflicting evidence detected",
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 3. REFUND ALREADY ISSUED
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
        # 4. DELIVERY FAILURE
        # ==========================================

        if (
            reason == "product_not_received"
            and delivery_status == "failed"
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
        # 5. UNAUTHORIZED TRANSACTION
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
        # 6. DUPLICATE CHARGE
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
        # 7. PRODUCT NOT AS DESCRIBED
        # ==========================================
        #
        # Delivery confirmation alone does not prove
        # that the product matched its description.
        #
        # Therefore this reason should NOT automatically
        # become CONTEST based only on delivery evidence.
        # ==========================================

        if reason == "product_not_as_described":

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

            return self._result(
                decision="HUMAN_REVIEW",
                reason=(
                    "Product description dispute "
                    "requires evidence verification"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 8. STRONG OBJECTIVE DELIVERY EVIDENCE
        # ==========================================
        #
        # Applies ONLY to product_not_received.
        #
        # Conditions:
        #
        #   delivered
        #   delivery proof exists
        #   evidence score >= 90
        #
        # If these conditions are satisfied and there
        # is no contradiction, the case can be contested.
        #
        # IMPORTANT:
        # This rule intentionally overrides ML
        # HUMAN_REVIEW because the objective evidence
        # is strong.
        # ==========================================

        if (
            reason == "product_not_received"
            and delivery_status == "delivered"
            and delivery_proof == "true"
            and score >= 90
        ):

            return self._result(
                decision="CONTEST",
                reason=(
                    "Strong objective delivery evidence "
                    "supports contesting"
                ),
                score=score,
                level=evidence_level,
                warnings=warnings
            )

        # ==========================================
        # 9. ML DO NOT CONTEST
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
        # 10. WEAK EVIDENCE
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
        # 11. ML HUMAN REVIEW
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
        # 12. ML CONTEST
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
        # 13. SAFE DEFAULT
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

    print("===== CHARGEBACKGUARD AI =====")
    print("Decision Engine V5 Test")
    print()

    engine = DecisionEngine()

    test_cases = [

        # --------------------------------------
        # TEST 1
        # --------------------------------------

        {
            "name": "STRONG DELIVERY + ML CONTEST",

            "case": {
                "dispute_id": "STRONG_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message": (
                    "I did not receive my order."
                ),
                "merchant_message": (
                    "Delivery was completed and "
                    "proof is available."
                )
            },

            "ml_prediction": "CONTEST"
        },

        # --------------------------------------
        # TEST 2
        # --------------------------------------

        {
            "name": "STRONG DELIVERY + ML HUMAN REVIEW",

            "case": {
                "dispute_id": "STRONG_ML_REVIEW_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message": (
                    "I did not receive my order."
                ),
                "merchant_message": (
                    "Delivery was completed and "
                    "proof is available."
                )
            },

            "ml_prediction": "HUMAN_REVIEW"
        },

        # --------------------------------------
        # TEST 3
        # --------------------------------------

        {
            "name": "PRODUCT NOT AS DESCRIBED",

            "case": {
                "dispute_id": "DESCRIPTION_TEST",
                "amount": 5000,
                "reason": "product_not_as_described",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message": (
                    "The product I received "
                    "was not as described."
                ),
                "merchant_message": (
                    "No additional evidence "
                    "is available."
                )
            },

            "ml_prediction": "HUMAN_REVIEW"
        },

        # --------------------------------------
        # TEST 4
        # --------------------------------------

        {
            "name": "CONTRADICTORY",

            "case": {
                "dispute_id": "CONTRADICTION_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message": (
                    "I did not receive my order."
                ),
                "merchant_message": (
                    "Customer previously confirmed "
                    "that the order was received."
                )
            },

            "ml_prediction": "CONTEST"
        },

        # --------------------------------------
        # TEST 5
        # --------------------------------------

        {
            "name": "DELIVERY FAILURE",

            "case": {
                "dispute_id": "FAILURE_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "failed",
                "delivery_proof": "False",
                "refund_status": "not_issued",
                "customer_message": (
                    "I did not receive my order."
                ),
                "merchant_message": (
                    "Delivery attempt failed."
                )
            },

            "ml_prediction": "DO_NOT_CONTEST"
        }
    ]

    # ==========================================
    # RUN TESTS
    # ==========================================

    for item in test_cases:

        result = engine.decide(
            item["case"],
            item["ml_prediction"]
        )

        print("----------------------------------------")

        print(
            "Test:",
            item["name"]
        )

        print(
            "Dispute ID:",
            item["case"]["dispute_id"]
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

        print("Warnings:")

        if result["warnings"]:

            for warning in result["warnings"]:
                print(" -", warning)

        else:
            print(" - None")

        print()

    print("===== TEST COMPLETED =====")