from nlp_engine import NLPEngine


class EvidenceEngine:

    def __init__(self):

        self.max_score = 100
        self.nlp = NLPEngine()

    # ==========================================
    # TEXT HELPERS
    # ==========================================

    @staticmethod
    def _contains_any(text, phrases):

        return any(
            phrase in text
            for phrase in phrases
        )

    # ==========================================
    # ANALYZE CASE
    # ==========================================

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
        # NLP ANALYSIS
        # ==========================================

        nlp_result = self.nlp.analyze(
            customer_message,
            merchant_message
        )

        customer_nlp = nlp_result["customer"]
        merchant_nlp = nlp_result["merchant"]

        nlp_contradiction = bool(
            nlp_result.get(
                "contradiction_detected",
                False
            )
        )

        nlp_contradiction_reasons = nlp_result.get(
            "contradiction_reasons",
            []
        )

        # ==========================================
        # CUSTOMER RECEIPT STATUS
        # ==========================================

        customer_receipt_status = customer_nlp.get(
            "receipt_status",
            "UNKNOWN"
        )

        customer_non_receipt_detected = customer_nlp.get(
            "non_receipt_detected",
            False
        )

        customer_receipt_detected = customer_nlp.get(
            "receipt_detected",
            False
        )

        previous_confirmation_detected = customer_nlp.get(
            "previous_confirmation_detected",
            False
        )

        # ==========================================
        # FALLBACK CUSTOMER DETECTION
        # ==========================================

        if self._contains_any(
            customer_message,
            [
                "did not receive",
                "didn't receive",
                "never received",
                "not received",
                "did not get",
                "didn't get",
                "never got",
                "never arrived",
                "did not arrive",
                "didn't arrive",
                "never reached me"
            ]
        ):

            customer_non_receipt_detected = True

        if self._contains_any(
            customer_message,
            [
                "i received",
                "i got",
                "i have received",
                "package was received",
                "order was received"
            ]
        ):

            customer_receipt_detected = True

        if self._contains_any(
            customer_message,
            [
                "previously confirmed",
                "previously said",
                "previously stated",
                "earlier confirmed",
                "earlier said",
                "earlier stated",
                "confirmed receipt",
                "confirmed that the order was received",
                "confirmed that the product was received",
                "confirmed that the package was received",
                "earlier i confirmed"
            ]
        ):

            previous_confirmation_detected = True

        # ==========================================
        # CUSTOMER STATUS
        # ==========================================

        if (
            customer_non_receipt_detected
            and (
                customer_receipt_detected
                or previous_confirmation_detected
            )
        ):

            customer_receipt_status = "CONFLICTING"

        elif customer_receipt_status == "UNKNOWN":

            if customer_receipt_detected:

                customer_receipt_status = "RECEIVED"

            elif customer_non_receipt_detected:

                customer_receipt_status = "NOT_RECEIVED"

            elif previous_confirmation_detected:

                customer_receipt_status = "PREVIOUSLY_CONFIRMED"

        # ==========================================
        # MERCHANT DETECTION
        # ==========================================

        merchant_delivery_confirmed = bool(
            merchant_nlp.get(
                "delivery_confirmed",
                False
            )
        )

        merchant_customer_received = bool(
            merchant_nlp.get(
                "customer_received",
                False
            )
        )

        # Merchant customer receipt fallback
        merchant_received_fallback = self._contains_any(
            merchant_message,
            [
                "customer received",
                "customer has received",
                "customer already received",
                "customer was received",
                "customer was already received",
                "customer previously received",
                "customer confirmed receipt",
                "customer confirmed",
                "confirmed receipt",
                "order was received by customer",
                "package was received by customer",
                "customer received the package",
                "customer received the product",
                "customer received the order"
            ]
        )

        if merchant_received_fallback:

            merchant_customer_received = True

        # Merchant delivery fallback
        merchant_delivery_fallback = self._contains_any(
            merchant_message,
            [
                "delivery was completed",
                "delivery completed",
                "order was delivered",
                "package was delivered",
                "product was delivered",
                "successfully delivered",
                "delivery was successful",
                "delivered successfully",
                "reached the destination",
                "order reached the destination",
                "package reached the destination"
            ]
        )

        if merchant_delivery_fallback:

            merchant_delivery_confirmed = True

        # ==========================================
        # CONTRADICTION DETECTION
        # ==========================================

        if nlp_contradiction:

            contradiction_detected = True

            for item in nlp_contradiction_reasons:

                if item not in warnings:

                    warnings.append(item)

        # Customer denies receipt
        # + merchant says customer received

        if (
            customer_non_receipt_detected
            and merchant_customer_received
        ):

            contradiction_detected = True

            warning = (
                "Customer claims non-receipt while merchant evidence "
                "indicates customer received the order"
            )

            if warning not in warnings:

                warnings.append(warning)

        # Customer denies receipt
        # + previous confirmation

        if (
            customer_non_receipt_detected
            and previous_confirmation_detected
        ):

            contradiction_detected = True

            warning = (
                "Customer message contains both non-receipt "
                "and previous receipt confirmation"
            )

            if warning not in warnings:

                warnings.append(warning)

        # Customer message contains both claims

        if (
            customer_non_receipt_detected
            and customer_receipt_detected
        ):

            contradiction_detected = True

            warning = (
                "Customer message contains conflicting receipt claims"
            )

            if warning not in warnings:

                warnings.append(warning)

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
        # NLP EVIDENCE
        # ==========================================

        nlp_score = 0

        if customer_receipt_status == "RECEIVED":

            nlp_score += 10

            reasons.append(
                "NLP detected customer confirmation of receipt"
            )

        elif customer_receipt_status == "NOT_RECEIVED":

            nlp_score += 3

            reasons.append(
                "NLP detected customer non-receipt claim"
            )

        elif customer_receipt_status == "CONFLICTING":

            warnings.append(
                "NLP detected conflicting receipt claims in customer message"
            )

        elif customer_receipt_status == "PREVIOUSLY_CONFIRMED":

            warnings.append(
                "NLP detected previous customer confirmation of receipt"
            )

        if merchant_customer_received:

            nlp_score += 7

            reasons.append(
                "NLP detected merchant statement that customer received the order"
            )

        elif merchant_delivery_confirmed:

            reasons.append(
                "NLP detected merchant delivery confirmation"
            )

        score += nlp_score

        # ==========================================
        # COMMUNICATION SCORE
        # ==========================================

        communication_score = 0

        if customer_receipt_status == "RECEIVED":

            communication_score += 8

        elif customer_receipt_status == "NOT_RECEIVED":

            communication_score += 3

        if merchant_customer_received:

            communication_score += 7

        score += communication_score

        # ==========================================
        # STRONG DELIVERY CONSISTENCY
        # ==========================================
        #
        # Delivery + proof is strong evidence.
        # Customer non-receipt alone should not destroy
        # the strength of objective delivery evidence.
        #
        # A merchant/customer contradiction is handled
        # separately and causes HUMAN_REVIEW in DecisionEngine.
        # ==========================================

        consistency_score = 0

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and customer_receipt_status == "NOT_RECEIVED"
            and not merchant_customer_received
        ):

            consistency_score = 20

        elif customer_receipt_status == "RECEIVED":

            consistency_score = 20

        elif (
            delivery_status == "failed"
            and customer_receipt_status == "NOT_RECEIVED"
        ):

            consistency_score = 20

        elif (
            delivery_status == "delivered"
            and delivery_proof == "true"
            and customer_non_receipt_detected
            and not contradiction_detected
        ):

            consistency_score = 20

        score += consistency_score

        # ==========================================
        # STRONG DELIVERY BONUS
        # ==========================================
        #
        # Objective delivery + proof should reach
        # STRONG evidence even when customer disputes receipt.
        # ==========================================

        if (
            delivery_status == "delivered"
            and delivery_proof == "true"
        ):

            score += 20

            reasons.append(
                "Strong objective delivery evidence is available"
            )

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
        # RETURN
        # ==========================================

        return {

            "evidence_score": score,

            "evidence_level": evidence_level,

            "contradiction_detected":
                contradiction_detected,

            "reasons": reasons,

            "warnings": warnings,

            "nlp_analysis": {

                "customer_receipt_status":
                    customer_receipt_status,

                "customer_non_receipt_detected":
                    customer_non_receipt_detected,

                "customer_receipt_detected":
                    customer_receipt_detected,

                "previous_confirmation_detected":
                    previous_confirmation_detected,

                "merchant_delivery_confirmed":
                    merchant_delivery_confirmed,

                "merchant_customer_received":
                    merchant_customer_received,

                "nlp_contradiction":
                    nlp_contradiction,

                "contradiction_reasons":
                    nlp_contradiction_reasons
            },

            "evidence_breakdown": {

                "delivery_evidence":
                    delivery_score,

                "delivery_proof":
                    delivery_proof_score,

                "refund_evidence":
                    refund_score,

                "communication_evidence":
                    communication_score,

                "nlp_evidence":
                    nlp_score,

                "consistency":
                    consistency_score
            }
        }


if __name__ == "__main__":

    engine = EvidenceEngine()

    case = {

        "dispute_id": "TEST",

        "amount": 5000,

        "reason": "product_not_received",

        "delivery_status": "delivered",

        "delivery_proof": "True",

        "refund_status": "not_issued",

        "customer_message":
            "I did not receive my order.",

        "merchant_message":
            "Delivery was completed and proof is available."
    }

    result = engine.analyze(case)

    print("===== CHARGEBACKGUARD AI =====")
    print("Evidence Engine Test")
    print()

    print("Evidence Score:",
          result["evidence_score"])

    print("Evidence Level:",
          result["evidence_level"])

    print("Contradiction:",
          result["contradiction_detected"])

    print()

    print("NLP Analysis:")

    for key, value in result["nlp_analysis"].items():

        print(
            " -",
            key + ":",
            value
        )

    print()

    print("Warnings:")

    for warning in result["warnings"]:

        print(" -", warning)

    print()
    print("===== TEST COMPLETED =====")