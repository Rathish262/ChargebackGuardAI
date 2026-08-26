from evidence_engine import EvidenceEngine


engine = EvidenceEngine()


test_cases = [

    {
        "name": "Normal contradiction",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message":
                "Customer previously confirmed that the order was received."
        },
        "expected": True
    },

    {
        "name": "Different wording - customer received package",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message":
                "The customer was already received the package."
        },
        "expected": True
    },

    {
        "name": "Customer denies receipt - merchant confirms delivery only",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message": "I never received the package.",
            "merchant_message":
                "Delivery was completed successfully."
        },
        "expected": False
    },

    {
        "name": "Customer previously confirmed receipt",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "delivered",
            "delivery_proof": "True",
            "refund_status": "not_issued",
            "customer_message":
                "I did not receive the order. Earlier I confirmed receipt by mistake.",
            "merchant_message":
                "We are reviewing the dispute."
        },
        "expected": True
    },

    {
        "name": "No contradiction",
        "case": {
            "reason": "product_not_received",
            "delivery_status": "unknown",
            "delivery_proof": "False",
            "refund_status": "not_issued",
            "customer_message": "I did not receive my order.",
            "merchant_message":
                "We do not have delivery confirmation."
        },
        "expected": False
    }
]


print("===== CHARGEBACKGUARD AI =====")
print("EDGE CASE TEST")
print()

passed = 0

for test in test_cases:

    result = engine.analyze(test["case"])

    actual = result["contradiction_detected"]

    status = "PASS" if actual == test["expected"] else "FAIL"

    if status == "PASS":
        passed += 1

    print("----------------------------------------")
    print("Test:", test["name"])
    print("Expected:", test["expected"])
    print("Actual:", actual)
    print("Result:", status)

print()
print("========================================")
print(f"PASSED: {passed}/{len(test_cases)}")
print("========================================")