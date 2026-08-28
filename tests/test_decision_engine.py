import pytest

from decision_engine import DecisionEngine


@pytest.fixture
def engine():
    return DecisionEngine()


# =========================================================
# TEST 1 — STRONG DELIVERY
# =========================================================

def test_strong_delivery(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message": "I did not receive my order.",
        "merchant_message":
            "Delivery was completed and proof is available."
    }

    result = engine.decide(
        case,
        "CONTEST"
    )

    assert result["decision"] == "CONTEST"


# =========================================================
# TEST 2 — STRONG EVIDENCE SHOULD OVERRIDE ML REVIEW
# =========================================================

def test_strong_delivery_overrides_human_review(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message": "I did not receive my order.",
        "merchant_message":
            "Delivery was completed and proof is available."
    }

    result = engine.decide(
        case,
        "HUMAN_REVIEW"
    )

    assert result["decision"] == "CONTEST"


# =========================================================
# TEST 3 — CONTRADICTORY EVIDENCE
# =========================================================

def test_contradictory_evidence_requires_human_review(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "Customer previously confirmed that the order was received."
    }

    result = engine.decide(
        case,
        "CONTEST"
    )

    assert result["decision"] == "HUMAN_REVIEW"


# =========================================================
# TEST 4 — DELIVERY FAILURE
# =========================================================

def test_delivery_failure_should_not_contest(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "failed",
        "delivery_proof": "False",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "The delivery attempt failed."
    }

    result = engine.decide(
        case,
        "DO_NOT_CONTEST"
    )

    assert result["decision"] == "DO_NOT_CONTEST"


# =========================================================
# TEST 5 — WEAK EVIDENCE
# =========================================================

def test_weak_evidence_requires_human_review(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "unknown",
        "delivery_proof": "False",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "We cannot confirm delivery."
    }

    result = engine.decide(
        case,
        "CONTEST"
    )

    assert result["decision"] == "HUMAN_REVIEW"