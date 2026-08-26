
from evidence_engine import EvidenceEngine


class DecisionEngine:

    def __init__(self):
        self.evidence_engine = EvidenceEngine()

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

        # -----------------------------------
        # 1. EXPLICIT COMMUNICATION CONFLICT
        # -----------------------------------

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

        # -----------------------------------
        # 2. CRITICAL SAFETY RULE
        # -----------------------------------

        if contradiction or explicit_conflict:

            return {
                "decision": "HUMAN_REVIEW",
                "reason": "Conflicting evidence detected",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 3. REFUND SAFETY
        # -----------------------------------

        if refund_status == "issued":

            return {
                "decision": "DO_NOT_CONTEST",
                "reason": "Refund has already been issued",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 4. DELIVERY FAILURE
        # -----------------------------------

        if (
            delivery_status == "failed"
            and reason == "product_not_received"
        ):

            return {
                "decision": "DO_NOT_CONTEST",
                "reason": "Delivery failed and supports the non-receipt claim",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 5. UNAUTHORIZED TRANSACTION
        # -----------------------------------

        if reason == "unauthorized_transaction":

            return {
                "decision": "HUMAN_REVIEW",
                "reason": "Unauthorized transaction requires verification",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 6. DUPLICATE CHARGE
        # -----------------------------------

        if reason == "duplicate_charge":

            return {
                "decision": "HUMAN_REVIEW",
                "reason": "Duplicate charge requires transaction verification",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 7. STRONG DELIVERY EVIDENCE
        # -----------------------------------

        # Strong independent delivery evidence can
        # override an uncertain ML prediction.
        #
        # Critical conflicts, refunds, failed delivery,
        # and sensitive dispute reasons have already
        # been handled above.

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and score >= 90
        ):

            return {
                "decision": "CONTEST",
                "reason": "Strong delivery evidence supports contesting",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 8. ML DO NOT CONTEST
        # -----------------------------------

        if ml_prediction == "DO_NOT_CONTEST":

            return {
                "decision": "DO_NOT_CONTEST",
                "reason": "Risk model recommends not contesting",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 9. WEAK EVIDENCE
        # -----------------------------------

        if score < 40:

            return {
                "decision": "HUMAN_REVIEW",
                "reason": "Evidence strength is too weak",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 10. ML HUMAN REVIEW
        # -----------------------------------

        if ml_prediction == "HUMAN_REVIEW":

            return {
                "decision": "HUMAN_REVIEW",
                "reason": "Risk model recommends human verification",
                "evidence_score": score,
                "evidence_level": evidence_level,
                "warnings": warnings
            }

        # -----------------------------------
        # 11. SAFE DEFAULT
        # -----------------------------------

        return {
            "decision": "HUMAN_REVIEW",
            "reason": "Case requires human verification",
            "evidence_score": score,
            "evidence_level": evidence_level,
            "warnings": warnings
        }


# ===========================================
# TEST DECISION ENGINE
# ===========================================

if __name__ == "__main__":

    print("===== CHARGEBACKGUARD AI =====")
    print("Decision Engine V3 Test")
    print()

    test_cases = [

        {
            "name": "STRONG DELIVERY",

            "case": {
                "dispute_id": "STRONG_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message":
                    "I did not receive my order.",
                "merchant_message":
                    "Delivery was completed and proof is available."
            },

            "ml_prediction": "CONTEST"
        },

        {
            "name": "STRONG DELIVERY + ML HUMAN REVIEW",

            "case": {
                "dispute_id": "STRONG_ML_REVIEW_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message":
                    "I did not receive my order.",
                "merchant_message":
                    "Delivery was completed and proof is available."
            },

            "ml_prediction": "HUMAN_REVIEW"
        },

        {
            "name": "CONTRADICTORY",

            "case": {
                "dispute_id": "CONTRADICTION_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "delivered",
                "delivery_proof": "True",
                "refund_status": "not_issued",
                "customer_message":
                    "I did not receive my order.",
                "merchant_message":
                    "Customer previously confirmed that the order was received."
            },

            "ml_prediction": "CONTEST"
        },

        {
            "name": "DELIVERY FAILURE",

            "case": {
                "dispute_id": "FAILURE_TEST",
                "amount": 5000,
                "reason": "product_not_received",
                "delivery_status": "failed",
                "delivery_proof": "False",
                "refund_status": "not_issued",
                "customer_message":
                    "I did not receive my order.",
                "merchant_message":
                    "Delivery attempt failed."
            },

            "ml_prediction": "DO_NOT_CONTEST"
        }
    ]

    engine = DecisionEngine()

    for item in test_cases:

        case = item["case"]
        ml_prediction = item["ml_prediction"]

        result = engine.decide(
            case,
            ml_prediction
        )

        print("----------------------------------------")
        print("Test:", item["name"])
        print("Dispute ID:", case["dispute_id"])
        print("ML Prediction:", ml_prediction)

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

