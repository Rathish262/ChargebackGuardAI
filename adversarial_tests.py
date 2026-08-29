from decision_engine import DecisionEngine


engine = DecisionEngine()


# ==========================================
# ADVERSARIAL TEST CASES
# ==========================================

test_cases = [

    # --------------------------------------
    # 1. STRONG DELIVERY + ML CONTEST
    # Expected: CONTEST
    # --------------------------------------

    {
        "name": "Strong delivery evidence",

        "case": {
            "dispute_id": "ADV_001",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": (
                "Delivery was completed and proof is available."
            )
        },

        "ml_prediction": "CONTEST",
        "expected": "CONTEST"
    },


    # --------------------------------------
    # 2. STRONG DELIVERY + ML HUMAN REVIEW
    # Expected: CONTEST
    # --------------------------------------

    {
        "name": "Strong evidence overrides ML review",

        "case": {
            "dispute_id": "ADV_002",
            "amount": 7500,
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I never received my order.",
            "merchant_message": (
                "Package was delivered successfully "
                "with delivery proof."
            )
        },

        "ml_prediction": "HUMAN_REVIEW",
        "expected": "CONTEST"
    },


    # --------------------------------------
    # 3. CONTRADICTION
    # Expected: HUMAN_REVIEW
    # --------------------------------------

    {
        "name": "Customer and merchant contradiction",

        "case": {
            "dispute_id": "ADV_003",
            "amount": 4000,
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

        "ml_prediction": "CONTEST",
        "expected": "HUMAN_REVIEW"
    },


    # --------------------------------------
    # 4. DELIVERY FAILED
    # Expected: DO_NOT_CONTEST
    # --------------------------------------

    {
        "name": "Delivery failure",

        "case": {
            "dispute_id": "ADV_004",
            "amount": 3000,
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

        "ml_prediction": "CONTEST",
        "expected": "DO_NOT_CONTEST"
    },


    # --------------------------------------
    # 5. REFUND ALREADY ISSUED
    # Expected: DO_NOT_CONTEST
    # --------------------------------------

    {
        "name": "Refund already issued",

        "case": {
            "dispute_id": "ADV_005",
            "amount": 2500,
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "issued",
            "customer_message": (
                "I did not receive my order."
            ),
            "merchant_message": (
                "Delivery was completed."
            )
        },

        "ml_prediction": "CONTEST",
        "expected": "DO_NOT_CONTEST"
    },


    # --------------------------------------
    # 6. UNAUTHORIZED TRANSACTION
    # Expected: HUMAN_REVIEW
    # --------------------------------------

    {
        "name": "Unauthorized transaction",

        "case": {
            "dispute_id": "ADV_006",
            "amount": 9000,
            "reason": "unauthorized_transaction",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "I did not authorize this transaction."
            ),
            "merchant_message": (
                "Transaction was successfully processed."
            )
        },

        "ml_prediction": "CONTEST",
        "expected": "HUMAN_REVIEW"
    },


    # --------------------------------------
    # 7. DUPLICATE CHARGE
    # Expected: HUMAN_REVIEW
    # --------------------------------------

    {
        "name": "Duplicate charge",

        "case": {
            "dispute_id": "ADV_007",
            "amount": 6000,
            "reason": "duplicate_charge",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "I was charged twice for the same order."
            ),
            "merchant_message": (
                "Order was successfully processed."
            )
        },

        "ml_prediction": "CONTEST",
        "expected": "HUMAN_REVIEW"
    },


    # --------------------------------------
    # 8. PRODUCT NOT AS DESCRIBED
    # Expected: HUMAN_REVIEW
    # --------------------------------------

    {
        "name": "Product not as described",

        "case": {
            "dispute_id": "ADV_008",
            "amount": 5000,
            "reason": "product_not_as_described",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "The product I received was not as described."
            ),
            "merchant_message": (
                "The product was delivered successfully."
            )
        },

        "ml_prediction": "HUMAN_REVIEW",
        "expected": "HUMAN_REVIEW"
    },


    # --------------------------------------
    # 9. PRODUCT NOT AS DESCRIBED + ML
    # Expected: DO_NOT_CONTEST
    # --------------------------------------

    {
        "name": "Description dispute with ML not contest",

        "case": {
            "dispute_id": "ADV_009",
            "amount": 5000,
            "reason": "product_not_as_described",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "The product does not match the description."
            ),
            "merchant_message": (
                "Product was delivered."
            )
        },

        "ml_prediction": "DO_NOT_CONTEST",
        "expected": "DO_NOT_CONTEST"
    },


    # --------------------------------------
    # 10. WEAK EVIDENCE
    # Expected: HUMAN_REVIEW
    # --------------------------------------

    {
        "name": "Weak evidence",

        "case": {
            "dispute_id": "ADV_010",
            "amount": 1000,
            "reason": "product_not_received",
            "delivery_status": "unknown",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": (
                "I have an issue with my order."
            ),
            "merchant_message": (
                "We are checking the order."
            )
        },

        "ml_prediction": "HUMAN_REVIEW",
        "expected": "HUMAN_REVIEW"
    }

]


# ==========================================
# RUN TESTS
# ==========================================

print("==========================================")
print("CHARGEBACKGUARD AI")
print("ADVERSARIAL TESTING")
print("==========================================")
print()


passed = 0
failed = 0


for test in test_cases:

    result = engine.decide(
        test["case"],
        test["ml_prediction"]
    )

    actual = result["decision"]
    expected = test["expected"]

    print("------------------------------------------")
    print("Test:", test["name"])
    print("Dispute ID:", test["case"]["dispute_id"])
    print("ML Prediction:", test["ml_prediction"])
    print("Evidence Score:", result["evidence_score"])
    print("Actual Decision:", actual)
    print("Expected Decision:", expected)

    if actual == expected:

        print("STATUS: PASS")
        passed += 1

    else:

        print("STATUS: FAIL")
        failed += 1

    print()


# ==========================================
# SUMMARY
# ==========================================

total = len(test_cases)

print("==========================================")
print("ADVERSARIAL TEST SUMMARY")
print("==========================================")

print("Total Tests:", total)
print("Passed:", passed)
print("Failed:", failed)

if failed == 0:

    print()
    print("ALL ADVERSARIAL TESTS PASSED")
    print("Pipeline safety rules are behaving as expected.")

else:

    print()
    print("SOME ADVERSARIAL TESTS FAILED")
    print("Review the failed cases before modifying the pipeline.")

print()
print("==========================================")