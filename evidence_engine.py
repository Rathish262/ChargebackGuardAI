class EvidenceEngine:

    def __init__(self):
        self.max_score = 100

    def analyze(self, case):

        score = 0
        reasons = []
        warnings = []

        contradiction_detected = False

        # ==========================================
        # NORMALIZE INPUT
        # ==========================================

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

        # ==========================================
        # DELIVERY EVIDENCE
        # ==========================================

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

        # ==========================================
        # DELIVERY PROOF
        # ==========================================

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

        # ==========================================
        # REFUND STATUS
        # ==========================================

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

        # ==========================================
        # DISPUTE REASON
        # ==========================================

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

        # ==========================================
        # CUSTOMER MESSAGE ANALYSIS
        # ==========================================

        customer_not_received = any(
            phrase in customer_message
            for phrase in [

                "never received",
                "did not receive",
                "didn't receive",
                "not received",
                "have not received",
                "haven't received",

                "never got",
                "did not get",
                "didn't get",

                "i do not have my order",
                "i don't have my order",

                "order never arrived",
                "order did not arrive",
                "order didn't arrive",

                "package never arrived",
                "package did not arrive",
                "package didn't arrive",

                "product never arrived",
                "product did not arrive",
                "product didn't arrive"
            ]
        )

        # ==========================================
        # CUSTOMER PREVIOUSLY CONFIRMED RECEIPT
        # ==========================================

        customer_previous_receipt = any(
            phrase in customer_message
            for phrase in [

                "previously confirmed receipt",
                "previously confirmed that i received",

                "previously confirmed that the order was received",
                "previously confirmed that the product was received",
                "previously confirmed that the package was received",

                "previously said that i received",
                "previously stated that i received",

                "earlier confirmed receipt",
                "earlier confirmed that i received",

                "earlier said that i received",
                "earlier stated that i received",

                "confirmed receipt",
                "confirmed that the order was received",
                "confirmed that the product was received",
                "confirmed that the package was received"
            ]
        )

        # ==========================================
        # CUSTOMER DIRECTLY CONFIRMS RECEIPT
        # ==========================================

        customer_received = any(
            phrase in customer_message
            for phrase in [

                "i received the product",
                "i received my order",
                "i received the order",
                "i received my package",
                "i received the package",

                "i got the product",
                "i got my order",
                "i got the order",
                "i got my package",
                "i got the package",

                "i have received the product",
                "i have received my order",
                "i have received the order",
                "i have received my package",
                "i have received the package",

                "my order arrived",
                "my package arrived",
                "the package arrived",
                "the order arrived",
                "the product arrived",

                "i got it",
                "i received it"
            ]
        )

        # ==========================================
        # MERCHANT MESSAGE ANALYSIS
        # ==========================================

        merchant_confirmed = any(
            phrase in merchant_message
            for phrase in [

                # Explicit confirmation

                "customer confirmed receipt",
                "customer confirmed that they received",
                "customer confirmed that he received",
                "customer confirmed that she received",

                # Customer received item

                "customer received the product",
                "customer received the order",
                "customer received the package",

                "customer has received the product",
                "customer has received the order",
                "customer has received the package",

                "customer got the product",
                "customer got the order",
                "customer got the package",

                # Dataset edge-case wording

                "customer was already received the package",
                "customer already received the package",

                # Previous confirmation

                "customer previously confirmed receipt",
                "customer previously confirmed that they received",

                "customer previously confirmed that the order was received",
                "customer previously confirmed that the product was received",
                "customer previously confirmed that the package was received",

                "customer earlier confirmed receipt",
                "customer earlier confirmed that they received",

                "customer earlier confirmed that the order was received",
                "customer earlier confirmed that the product was received",

                "customer previously said they received",
                "customer previously said that they received",

                "customer previously stated they received",
                "customer previously stated that they received"
            ]
        )

        # ==========================================
        # COMMUNICATION SCORE
        # ==========================================

        communication_score = 0

        if customer_received:

            communication_score += 8

        elif customer_not_received:

            communication_score += 3

        if merchant_confirmed:

            communication_score += 7

        # ==========================================
        # CONTRADICTION DETECTION
        # ==========================================

        # CASE 1:
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

        # CASE 2:
        # Customer denies receipt but merchant says
        # customer received/confirmed receipt.

        if (
            merchant_confirmed
            and customer_not_received
        ):

            contradiction_detected = True

            warnings.append(
                "Merchant states customer previously confirmed receipt while customer denies receipt"
            )

        # CASE 3:
        # Customer message itself contains both
        # received and not-received claims.

        if (
            customer_received
            and customer_not_received
        ):

            contradiction_detected = True

            warnings.append(
                "Customer message contains conflicting receipt claims"
            )

        # ==========================================
        # DELIVERY VS CUSTOMER CLAIM
        # ==========================================

        # Delivered + customer denial is suspicious,
        # but NOT automatically a contradiction.

        if (
            delivery_status == "delivered"
            and customer_not_received
        ):

            warnings.append(
                "Customer disputes receipt despite delivery record showing delivered"
            )

        # ==========================================
        # CONSISTENCY SCORE
        # ==========================================

        consistency_score = 0

        # Strong delivery evidence + customer denial.
        # This is suspicious but not an explicit
        # communication contradiction.

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and customer_not_received
            and not contradiction_detected
        ):

            consistency_score = 20

        # Explicit merchant/customer conflict.

        elif (
            merchant_confirmed
            and customer_not_received
        ):

            consistency_score = 0

        # Customer confirms receipt.

        elif (
            customer_received
            and not customer_not_received
        ):

            consistency_score = 20

        # Delivery failed + customer says not received.

        elif (
            delivery_status == "failed"
            and customer_not_received
        ):

            consistency_score = 20

        score += communication_score
        score += consistency_score

        # ==========================================
        # SCORE BOUNDARY
        # ==========================================

        score = max(
            0,
            min(score, self.max_score)
        )

        # ==========================================
        # EVIDENCE LEVEL
        # ==========================================

        if score >= 70:

            evidence_level = "STRONG"

        elif score >= 40:

            evidence_level = "MODERATE"

        else:

            evidence_level = "WEAK"

        # ==========================================
        # RETURN RESULT
        # ==========================================

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


# ==========================================
# LOCAL TEST
# ==========================================

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
    print("Evidence Engine V7 Test")
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