from decision_engine import DecisionEngine

engine = DecisionEngine()

test_cases = [

    {
        "name": "Strong delivery",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Delivery was completed and proof is available."
        },
        "ml_prediction": "CONTEST",
        "expected": "CONTEST"
    },

    {
        "name": "Strong delivery + ML HUMAN_REVIEW",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Delivery was completed and proof is available."
        },
        "ml_prediction": "HUMAN_REVIEW",
        "expected": "CONTEST"
    },

    {
        "name": "Contradictory evidence",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "Customer previously confirmed that the order was received."
        },
        "ml_prediction": "CONTEST",
        "expected": "HUMAN_REVIEW"
    },

    {
        "name": "Delivery failure",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "failed",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "The delivery attempt failed."
        },
        "ml_prediction": "DO_NOT_CONTEST",
        "expected": "DO_NOT_CONTEST"
    },

    {
        "name": "Weak evidence",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "unknown",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message": "We cannot confirm delivery."
        },
        "ml_prediction": "CONTEST",
        "expected": "HUMAN_REVIEW"
    }
]

print("===== CHARGEBACKGUARD AI =====")
print("DECISION ENGINE TEST")
print()

passed = 0

for test in test_cases:

    result = engine.decide(
        test["case"],
        test["ml_prediction"]
    )

    actual = result["decision"]

    status = "PASS" if actual == test["expected"] else "FAIL"

    if status == "PASS":
        passed += 1

    print("----------------------------------------")
    print("Test:", test["name"])
    print("ML Prediction:", test["ml_prediction"])
    print("Expected:", test["expected"])
    print("Actual:", actual)
    print("Result:", status)

print()
print("========================================")
print(f"PASSED: {passed}/{len(test_cases)}")
print("========================================")
