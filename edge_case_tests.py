from decision_engine import DecisionEngine


print("==========================================")
print("CHARGEBACKGUARD AI")
print("EDGE CASE TESTING")
print("==========================================")
print()


engine = DecisionEngine()


test_cases = [

    # ==========================================
    # 1. DELIVERY PROOF TRUE BUT NOT DELIVERED
    # ==========================================

    {
        "name": "Proof exists but delivery status failed",

        "case": {
            "dispute_id": "EDGE_001",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "failed",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Proof was generated."
        },

        "ml_prediction": "CONTEST",

        "expected": "DO_NOT_CONTEST"
    },


    # ==========================================
    # 2. DELIVERED BUT NO DELIVERY PROOF
    # ==========================================

    {
        "name": "Delivered but no proof",

        "case": {
            "dispute_id": "EDGE_002",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Order shows delivered."
        },

        "ml_prediction": "CONTEST",

        "expected": "CONTEST"
    },


    # ==========================================
    # 3. REFUND + STRONG DELIVERY
    # ==========================================

    {
        "name": "Refund issued despite strong delivery",

        "case": {
            "dispute_id": "EDGE_003",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Delivery proof is available."
        },

        "ml_prediction": "CONTEST",

        "expected": "DO_NOT_CONTEST"
    },


    # ==========================================
    # 4. CONTRADICTION + DELIVERY FAILURE
    # ==========================================

    {
        "name": "Contradiction with failed delivery",

        "case": {
            "dispute_id": "EDGE_004",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "failed",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": (
                "Customer previously confirmed "
                "that the order was received."
            )
        },

        "ml_prediction": "DO_NOT_CONTEST",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 5. UNKNOWN ML PREDICTION
    # ==========================================

    {
        "name": "Unknown ML prediction",

        "case": {
            "dispute_id": "EDGE_005",
            "amount": 5000,
            "reason": "product_not_received",
            "delivery_status": "unknown",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "",
            "merchant_message": ""
        },

        "ml_prediction": "UNKNOWN",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 6. EMPTY REASON
    # ==========================================

    {
        "name": "Missing dispute reason",

        "case": {
            "dispute_id": "EDGE_006",
            "amount": 5000,
            "reason": "",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "",
            "merchant_message": ""
        },

        "ml_prediction": "CONTEST",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 7. DESCRIPTION DISPUTE + CONTEST
    # ==========================================

    {
        "name": "Description dispute with ML contest",

        "case": {
            "dispute_id": "EDGE_007",
            "amount": 5000,
            "reason": "product_not_as_described",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "The product was completely different "
                "from the description."
            ),
            "merchant_message": (
                "The product was delivered successfully."
            )
        },

        "ml_prediction": "CONTEST",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 8. UNAUTHORIZED + STRONG DELIVERY
    # ==========================================

    {
        "name": "Unauthorized transaction with delivery proof",

        "case": {
            "dispute_id": "EDGE_008",
            "amount": 5000,
            "reason": "unauthorized_transaction",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "I did not authorize this transaction."
            ),
            "merchant_message": (
                "Delivery proof is available."
            )
        },

        "ml_prediction": "CONTEST",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 9. DUPLICATE + STRONG DELIVERY
    # ==========================================

    {
        "name": "Duplicate charge with delivery proof",

        "case": {
            "dispute_id": "EDGE_009",
            "amount": 5000,
            "reason": "duplicate_charge",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": (
                "I was charged twice for the same order."
            ),
            "merchant_message": (
                "Order was delivered successfully."
            )
        },

        "ml_prediction": "CONTEST",

        "expected": "HUMAN_REVIEW"
    },


    # ==========================================
    # 10. CASE INSENSITIVITY
    # ==========================================

    {
        "name": "Uppercase delivery fields",

        "case": {
            "dispute_id": "EDGE_010",
            "amount": 5000,
            "reason": "PRODUCT_NOT_RECEIVED",
            "delivery_status": "DELIVERED",
            "delivery_proof": "TRUE",
            "refund_status": "NOT_ISSUED",
            "customer_message": "I DID NOT RECEIVE MY ORDER.",
            "merchant_message": (
                "Delivery was completed."
            )
        },

        "ml_prediction": "CONTEST",

        "expected": "CONTEST"
    }
]


passed = 0
failed = 0


for test in test_cases:

    case = test["case"]

    result = engine.decide(
        case,
        test["ml_prediction"]
    )

    actual = result["decision"]
    expected = test["expected"]

    if actual == expected:
        status = "PASS"
        passed += 1
    else:
        status = "FAIL"
        failed += 1

    print("------------------------------------------")
    print("Test:", test["name"])
    print("Dispute ID:", case["dispute_id"])
    print("ML Prediction:", test["ml_prediction"])
    print("Evidence Score:", result["evidence_score"])
    print("Actual Decision:", actual)
    print("Expected Decision:", expected)
    print("STATUS:", status)

    if status == "FAIL":
        print("Reason:", result["reason"])

    print()


print("==========================================")
print("EDGE CASE TEST SUMMARY")
print("==========================================")

print("Total Tests:", len(test_cases))
print("Passed:", passed)
print("Failed:", failed)
print()

if failed == 0:

    print("ALL EDGE CASE TESTS PASSED")

else:

    print("EDGE CASE TESTS FAILED")
    print("Review the failed cases before changing the decision engine.")

print("==========================================")