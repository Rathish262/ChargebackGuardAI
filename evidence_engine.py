class EvidenceEngine:

    def __init__(self):
        self.max_score = 100

    def analyze(self, case):

        score = 0
        reasons = []
        warnings = []

        contradiction_detected = False

        # -----------------------------------
        # NORMALIZE INPUT
        # -----------------------------------

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
        # DELIVERY EVIDENCE
        # -----------------------------------

        delivery_score = 0

        if delivery_status == "delivered":

            delivery_score = 30

            reasons.append(
                "Delivery status confirms successful delivery"
            )

        elif delivery_status == "failed":

            reasons.append(
                "Delivery attempt failed"
            )

        elif delivery_status == "unknown":

            reasons.append(
                "Delivery status is unknown"
            )

        score += delivery_score

        # -----------------------------------
        # DELIVERY PROOF
        # -----------------------------------

        delivery_proof_score = 0

        if delivery_proof == "true":

            delivery_proof_score = 25

            reasons.append(
                "Delivery proof is available"
            )

        elif delivery_proof == "false":

            reasons.append(
                "Delivery proof is missing"
            )

        score += delivery_proof_score

        # -----------------------------------
        # REFUND STATUS
        # -----------------------------------

        refund_score = 0

        if refund_status == "not_issued":

            refund_score = 15

            reasons.append(
                "Refund has not been issued"
            )

        elif refund_status == "issued":

            warnings.append(
                "Refund has already been issued"
            )

        score += refund_score

        # -----------------------------------
        # DISPUTE REASON
        # -----------------------------------

        if reason == "product_not_received":

            reasons.append(
                "Dispute concerns non-receipt of product"
            )

        elif reason == "product_not_as_described":

            reasons.append(
                "Dispute concerns product description"
            )

        elif reason == "unauthorized_transaction":

            warnings.append(
                "Unauthorized transaction requires additional verification"
            )

        elif reason == "duplicate_charge":

            warnings.append(
                "Duplicate charge requires transaction verification"
            )

        # -----------------------------------
        # CUSTOMER MESSAGE
        # -----------------------------------

        customer_not_received = any(
            phrase in customer_message
            for phrase in [
                "never received",
                "did not receive",
                "didn't receive",
                "not received",
                "never got",
                "did not get",
                "didn't get",
                "have not received",
                "haven't received",
                "i do not have my order",
                "i don't have my order"
            ]
        )

        customer_previous_receipt = any(
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
                "confirmed receipt",
                "said that the order was received",
                "said that the product was received",
                "stated that the order was received",
                "stated that the product was received"
            ]
        )

        customer_received = any(
            phrase in customer_message
            for phrase in [
                "i received the product",
                "i received my order",
                "i got the product",
                "i got my order",
                "i have received the product",
                "i have received my order"
            ]
        )

        # -----------------------------------
        # MERCHANT MESSAGE
        # -----------------------------------

        merchant_confirmed = any(
            phrase in merchant_message
            for phrase in [
                "customer confirmed receipt",
                "customer confirmed",
                "confirmed receipt",
                "customer received the product",
                "customer received the order",
                "customer has received the product",
                "customer has received the order",

                # Important:
                # Merchant can report that the
                # customer previously confirmed receipt.

                "customer previously confirmed",
                "customer previously said",
                "customer previously stated",
                "customer earlier confirmed",
                "customer earlier said",
                "customer earlier stated",

                "previously confirmed that the order was received",
                "previously confirmed that the product was received",
                "previously confirmed receipt",

                "earlier confirmed that the order was received",
                "earlier confirmed that the product was received",
                "earlier confirmed receipt"
            ]
        )

        # -----------------------------------
        # COMMUNICATION SCORE
        # -----------------------------------

        communication_score = 0

        if customer_received:

            communication_score += 8

        elif customer_not_received:

            communication_score += 3

        if merchant_confirmed:

            communication_score += 7

        # -----------------------------------
        # CONTRADICTION DETECTION
        # -----------------------------------

        # Customer denies receipt but previously
        # confirmed receipt.

        if (
            customer_not_received
            and customer_previous_receipt
        ):

            contradiction_detected = True

            warnings.append(
                "Customer message contains conflicting receipt statements"
            )

        # Merchant says customer previously
        # confirmed receipt while customer now
        # denies receiving the order.

        if (
            merchant_confirmed
            and customer_not_received
        ):

            contradiction_detected = True

            warnings.append(
                "Merchant states customer previously confirmed receipt while customer denies receipt"
            )

        # -----------------------------------
        # DELIVERY VS CUSTOMER CLAIM
        # -----------------------------------

        # Delivered + customer denial is treated
        # as conflicting evidence, but not by itself
        # as a contradiction.

        if (
            delivery_status == "delivered"
            and customer_not_received
        ):

            warnings.append(
                "Customer disputes receipt despite delivery record showing delivered"
            )

        # -----------------------------------
        # CONSISTENCY SCORE
        # -----------------------------------

        consistency_score = 0

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and customer_not_received
            and not contradiction_detected
        ):

            consistency_score = 20

        elif (
            merchant_confirmed
            and customer_not_received
        ):

            consistency_score = 0

        elif (
            customer_received
            and not customer_not_received
        ):

            consistency_score = 20

        elif (
            delivery_status == "failed"
            and customer_not_received
        ):

            consistency_score = 20

        score += communication_score
        score += consistency_score

        # -----------------------------------
        # SCORE BOUNDARY
        # -----------------------------------

        score = max(
            0,
            min(score, self.max_score)
        )

        # -----------------------------------
        # EVIDENCE LEVEL
        # -----------------------------------

        if score >= 70:

            evidence_level = "STRONG"

        elif score >= 40:

            evidence_level = "MODERATE"

        else:

            evidence_level = "WEAK"

        # -----------------------------------
        # RETURN RESULT
        # -----------------------------------

        return {

            "evidence_score": score,

            "evidence_level": evidence_level,

            "contradiction_detected":
                contradiction_detected,

            "reasons": reasons,

            "warnings": warnings,

            "evidence_breakdown": {

                "delivery_evidence":
                    delivery_score,

                "delivery_proof":
                    delivery_proof_score,

                "refund_evidence":
                    refund_score,

                "communication_evidence":
                    communication_score,

                "consistency":
                    consistency_score
            }
        }


# -------------------------------------------
# TEST
# -------------------------------------------

if __name__ == "__main__":

    engine = EvidenceEngine()

    test_cases = [

        {
            "dispute_id": "STRONG_TEST",

            "amount": 5000,

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

        {
            "dispute_id": "CONTRADICTION_TEST",

            "amount": 5000,

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

        {
            "dispute_id": "FAILURE_TEST",

            "amount": 5000,

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
                "The delivery attempt failed."
        }
    ]

    print("===== CHARGEBACKGUARD AI =====")
    print("Evidence Engine V5 Test")
    print()

    for case in test_cases:

        result = engine.analyze(case)

        print("----------------------------------------")

        print(
            "Dispute ID:",
            case["dispute_id"]
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
            "Contradiction Detected:",
            result["contradiction_detected"]
        )

        print()

        print("Evidence Breakdown:")

        for key, value in result[
            "evidence_breakdown"
        ].items():

            print(
                " -",
                key + ":",
                value
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

    print("===== TEST COMPLETED =====")