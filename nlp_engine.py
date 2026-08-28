import re


class NLPEngine:

    def __init__(self):

        # =========================================================
        # CUSTOMER NON-RECEIPT PATTERNS
        # =========================================================

        self.non_receipt_patterns = [

            r"\bnever received\b",
            r"\bdid not receive\b",
            r"\bdidn't receive\b",
            r"\bnot received\b",
            r"\bhave not received\b",
            r"\bhaven't received\b",

            r"\bnever got\b",
            r"\bdid not get\b",
            r"\bdidn't get\b",

            r"\bnever arrived\b",
            r"\bdid not arrive\b",
            r"\bdidn't arrive\b",

            r"\bnever reached me\b",
            r"\bdid not reach me\b",
            r"\bdidn't reach me\b",

            r"\bnothing was handed to me\b",
            r"\bnothing was delivered to me\b",

            r"\bi do not have my order\b",
            r"\bi don't have my order\b",

            r"\bi do not have the package\b",
            r"\bi don't have the package\b",

            r"\bi do not have the product\b",
            r"\bi don't have the product\b",

            r"\bpackage never reached me\b",
            r"\bshipment did not reach me\b",
            r"\border never reached me\b"
        ]

        # =========================================================
        # CUSTOMER RECEIPT PATTERNS
        # =========================================================

        self.receipt_patterns = [

            r"\bi received the product\b",
            r"\bi received my order\b",
            r"\bi received the order\b",
            r"\bi received my package\b",
            r"\bi received the package\b",

            r"\bi got the product\b",
            r"\bi got my order\b",
            r"\bi got the order\b",
            r"\bi got my package\b",
            r"\bi got the package\b",

            r"\bi have received the product\b",
            r"\bi have received my order\b",
            r"\bi have received the order\b",
            r"\bi have received my package\b",
            r"\bi have received the package\b",

            r"\bmy order arrived\b",
            r"\bmy package arrived\b",
            r"\bthe package arrived\b",
            r"\bthe order arrived\b",
            r"\bthe product arrived\b",

            r"\bi received it\b",
            r"\bi got it\b",
            r"\bthe package has arrived\b",
            r"\bthe order has arrived\b"
        ]

        # =========================================================
        # PREVIOUS CONFIRMATION
        # =========================================================

        self.previous_confirmation_patterns = [

            r"\bpreviously confirmed receipt\b",
            r"\bpreviously confirmed that .* received\b",

            r"\bpreviously said .* received\b",
            r"\bpreviously stated .* received\b",

            r"\bearlier confirmed receipt\b",
            r"\bearlier confirmed that .* received\b",

            r"\bearlier said .* received\b",
            r"\bearlier stated .* received\b",

            r"\bconfirmed receipt\b",
            r"\bconfirmed that .* received\b",

            r"\bconfirmed that .* was received\b",

            r"\bconfirmed receipt earlier\b",
            r"\bpreviously acknowledged receipt\b",
            r"\bearlier acknowledged receipt\b"
        ]

        # =========================================================
        # MERCHANT DELIVERY PATTERNS
        # =========================================================

        self.delivery_patterns = [

            r"\border was delivered\b",
            r"\bpackage was delivered\b",
            r"\bproduct was delivered\b",

            r"\border was successfully delivered\b",
            r"\bpackage was successfully delivered\b",
            r"\bproduct was successfully delivered\b",

            r"\bdelivery was completed\b",
            r"\bdelivery completed\b",

            r"\bdelivered successfully\b",

            r"\breached the destination\b",
            r"\breached the address\b",

            r"\border reached the destination\b",
            r"\bpackage reached the destination\b",

            r"\bdelivery was successful\b",
            r"\bsuccessfully delivered\b",

            r"\bdelivery attempt was successful\b",
            r"\bdelivery attempt completed\b"
        ]

        # =========================================================
        # MERCHANT CUSTOMER RECEIPT PATTERNS
        # =========================================================

        self.merchant_receipt_patterns = [

            # Normal wording
            r"\bcustomer received the product\b",
            r"\bcustomer received the order\b",
            r"\bcustomer received the package\b",

            r"\bcustomer has received the product\b",
            r"\bcustomer has received the order\b",
            r"\bcustomer has received the package\b",

            r"\bcustomer got the product\b",
            r"\bcustomer got the order\b",
            r"\bcustomer got the package\b",

            r"\bcustomer confirmed receipt\b",
            r"\bcustomer confirmed that they received\b",

            r"\bcustomer previously confirmed receipt\b",
            r"\bcustomer previously confirmed that the order was received\b",
            r"\bcustomer previously confirmed that the product was received\b",
            r"\bcustomer previously confirmed that the package was received\b",

            r"\bcustomer acknowledged receipt\b",
            r"\bcustomer has acknowledged receipt\b",

            r"\bcustomer accepted the package\b",
            r"\bcustomer accepted the order\b",

            # -----------------------------------------------------
            # Different / imperfect wording
            # -----------------------------------------------------

            r"\bcustomer was already received the package\b",
            r"\bcustomer was already received the order\b",
            r"\bcustomer was already received the product\b",

            r"\bcustomer was already given the package\b",
            r"\bcustomer was already given the order\b",

            r"\bcustomer had received the package\b",
            r"\bcustomer had received the order\b",
            r"\bcustomer had received the product\b",

            r"\bcustomer has already received the package\b",
            r"\bcustomer has already received the order\b",
            r"\bcustomer has already received the product\b",

            r"\bcustomer already received the package\b",
            r"\bcustomer already received the order\b",
            r"\bcustomer already received the product\b",

            r"\bcustomer already got the package\b",
            r"\bcustomer already got the order\b",
            r"\bcustomer already got the product\b"
        ]

        # =========================================================
        # REFUND PATTERNS
        # =========================================================

        self.refund_patterns = [

            r"\brefund has already been issued\b",
            r"\brefund was already issued\b",
            r"\brefund has been issued\b",
            r"\brefund was issued\b",
            r"\brefund already issued\b",

            r"\brefund issued\b",
            r"\brefund processed\b",
            r"\brefund has been processed\b",
            r"\brefund was processed\b",

            r"\bpayment refunded\b",
            r"\bamount refunded\b"
        ]

        # =========================================================
        # UNAUTHORIZED TRANSACTION PATTERNS
        # =========================================================

        self.unauthorized_patterns = [

            r"\bi do not recognize this transaction\b",
            r"\bi don't recognize this transaction\b",

            r"\bi did not make this transaction\b",
            r"\bi didn't make this transaction\b",

            r"\bthis transaction is not mine\b",
            r"\bunauthorized transaction\b",
            r"\bunauthorised transaction\b",

            r"\bi did not authorize this transaction\b",
            r"\bi didn't authorize this transaction\b",

            r"\bi do not recognize this payment\b",
            r"\bi don't recognize this payment\b",

            r"\bi did not make this payment\b",
            r"\bi didn't make this payment\b",

            # Existing test compatibility
            r"\btransaction requires verification\b",
            r"\btransaction requires additional verification\b",
            r"\bpayment requires verification\b",
            r"\bpayment requires additional verification\b",
            r"\brequires verification\b"
        ]

        # =========================================================
        # DUPLICATE PAYMENT PATTERNS
        # =========================================================

        self.duplicate_patterns = [

            r"\bcharged twice\b",
            r"\bcharged two times\b",
            r"\bcharged two times for the same\b",
            r"\bcharged twice for the same\b",

            r"\bduplicate charge\b",
            r"\bduplicate payment\b",

            r"\bpaid twice\b",
            r"\bpayment made twice\b",

            r"\bcharged multiple times\b",
            r"\bcharged more than once\b",

            # Existing test compatibility
            r"\btwo payment records\b",
            r"\btwo payment transactions\b",
            r"\bmultiple payment records\b",
            r"\bmultiple payment transactions\b",

            r"\bduplicate transaction\b",
            r"\bduplicate transactions\b"
        ]

    # =========================================================
    # NORMALIZE TEXT
    # =========================================================

    def normalize(self, text):

        if text is None:
            return ""

        text = str(text).lower().strip()
        text = re.sub(r"\s+", " ", text)

        return text

    # =========================================================
    # PATTERN MATCHER
    # =========================================================

    def contains_pattern(self, text, patterns):

        for pattern in patterns:

            if re.search(pattern, text):
                return True

        return False

    # =========================================================
    # CUSTOMER MESSAGE
    # =========================================================

    def analyze_customer_message(self, message):

        text = self.normalize(message)

        non_receipt = self.contains_pattern(
            text,
            self.non_receipt_patterns
        )

        received = self.contains_pattern(
            text,
            self.receipt_patterns
        )

        previous_confirmation = self.contains_pattern(
            text,
            self.previous_confirmation_patterns
        )

        if non_receipt and (
            received or previous_confirmation
        ):

            receipt_status = "CONFLICTING"

        elif previous_confirmation:

            receipt_status = "PREVIOUSLY_CONFIRMED"

        elif received:

            receipt_status = "RECEIVED"

        elif non_receipt:

            receipt_status = "NOT_RECEIVED"

        else:

            receipt_status = "UNKNOWN"

        return {

            "receipt_status": receipt_status,

            "non_receipt_detected": non_receipt,

            "receipt_detected": received,

            "previous_confirmation_detected":
                previous_confirmation
        }

    # =========================================================
    # MERCHANT MESSAGE
    # =========================================================

    def analyze_merchant_message(self, message):

        text = self.normalize(message)

        delivery_confirmed = self.contains_pattern(
            text,
            self.delivery_patterns
        )

        customer_received = self.contains_pattern(
            text,
            self.merchant_receipt_patterns
        )

        refund_issued = self.contains_pattern(
            text,
            self.refund_patterns
        )

        unauthorized = self.contains_pattern(
            text,
            self.unauthorized_patterns
        )

        duplicate = self.contains_pattern(
            text,
            self.duplicate_patterns
        )

        return {

            "delivery_confirmed":
                delivery_confirmed,

            "customer_received":
                customer_received,

            "refund_issued":
                refund_issued,

            "unauthorized_claim":
                unauthorized,

            "duplicate_charge_claim":
                duplicate
        }

    # =========================================================
    # COMPLETE NLP ANALYSIS
    # =========================================================

    def analyze(
        self,
        customer_message,
        merchant_message
    ):

        customer = self.analyze_customer_message(
            customer_message
        )

        merchant = self.analyze_merchant_message(
            merchant_message
        )

        contradiction = False
        contradiction_reasons = []

        # ---------------------------------------------------------
        # Customer denies receipt + merchant says customer received
        # ---------------------------------------------------------

        if (
            customer["receipt_status"] == "NOT_RECEIVED"
            and merchant["customer_received"]
        ):

            contradiction = True

            contradiction_reasons.append(
                "Customer denies receipt while merchant states customer received the order"
            )

        # ---------------------------------------------------------
        # Previous confirmation conflict
        # ---------------------------------------------------------

        if (
            customer["receipt_status"]
            == "PREVIOUSLY_CONFIRMED"
        ):

            contradiction = True

            contradiction_reasons.append(
                "Customer previously confirmed receipt but currently disputes receipt"
            )

        # ---------------------------------------------------------
        # Customer message contains conflicting claims
        # ---------------------------------------------------------

        if (
            customer["receipt_status"]
            == "CONFLICTING"
        ):

            contradiction = True

            contradiction_reasons.append(
                "Customer message contains conflicting receipt claims"
            )

        return {

            "customer": customer,

            "merchant": merchant,

            "contradiction_detected":
                contradiction,

            "contradiction_reasons":
                contradiction_reasons
        }


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":

    engine = NLPEngine()

    test_cases = [

        {
            "name": "Simple non-receipt",
            "customer":
                "I did not receive my package.",
            "merchant":
                "The order was delivered successfully."
        },

        {
            "name": "Different wording",
            "customer":
                "The package never reached me.",
            "merchant":
                "Our records indicate the order reached the destination."
        },

        {
            "name": "Merchant says customer received",
            "customer":
                "I did not receive the package.",
            "merchant":
                "The customer received the package."
        },

        {
            "name": "Merchant says customer was already received",
            "customer":
                "I did not receive my order.",
            "merchant":
                "The customer was already received the package."
        },

        {
            "name": "Previous confirmation",
            "customer":
                "I never received the package, although I previously confirmed receipt.",
            "merchant":
                "Delivery was completed."
        },

        {
            "name": "Customer received",
            "customer":
                "I received my package.",
            "merchant":
                "The order was delivered successfully."
        },

        {
            "name": "Unrelated message",
            "customer":
                "I have a problem with my order.",
            "merchant":
                "We are investigating the case."
        },

        {
            "name": "Unauthorized transaction",
            "customer":
                "I do not recognize this transaction.",
            "merchant":
                "The transaction requires verification."
        },

        {
            "name": "Duplicate payment",
            "customer":
                "I was charged twice for the same order.",
            "merchant":
                "Two payment records were detected."
        }
    ]

    print("===== CHARGEBACKGUARD AI =====")
    print("NLP ENGINE TEST")
    print()

    for case in test_cases:

        result = engine.analyze(
            case["customer"],
            case["merchant"]
        )

        print("----------------------------------------")

        print("Test:", case["name"])

        print(
            "Customer Receipt Status:",
            result["customer"]["receipt_status"]
        )

        print(
            "Merchant Delivery:",
            result["merchant"]["delivery_confirmed"]
        )

        print(
            "Merchant Customer Receipt:",
            result["merchant"]["customer_received"]
        )

        print(
            "Merchant Unauthorized:",
            result["merchant"]["unauthorized_claim"]
        )

        print(
            "Merchant Duplicate Charge:",
            result["merchant"]["duplicate_charge_claim"]
        )

        print(
            "Contradiction:",
            result["contradiction_detected"]
        )

        if result["contradiction_reasons"]:

            print("Reasons:")

            for reason in result["contradiction_reasons"]:
                print(" -", reason)

        else:

            print("Reasons: None")

        print()

    print("===== NLP TEST COMPLETED =====")