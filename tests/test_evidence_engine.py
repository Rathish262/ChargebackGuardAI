import pytest

from evidence_engine import EvidenceEngine


@pytest.fixture
def engine():
    return EvidenceEngine()


def test_normal_contradiction(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message": "I did not receive my order.",
        "merchant_message":
            "Customer previously confirmed that the order was received."
    }

    result = engine.analyze(case)

    assert result["contradiction_detected"] is True


def test_different_wording_contradiction(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message": "I did not receive my order.",
        "merchant_message":
            "The customer was already received the package."
    }

    result = engine.analyze(case)

    assert result["contradiction_detected"] is True


def test_delivery_only_is_not_contradiction(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message": "I never received the package.",
        "merchant_message":
            "Delivery was completed successfully."
    }

    result = engine.analyze(case)

    assert result["contradiction_detected"] is False


def test_previous_confirmation_conflict(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive the order. Earlier I confirmed receipt by mistake.",
        "merchant_message":
            "We are reviewing the dispute."
    }

    result = engine.analyze(case)

    assert result["contradiction_detected"] is True


def test_no_contradiction(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "unknown",
        "delivery_proof": "False",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "We do not have delivery confirmation."
    }

    result = engine.analyze(case)

    assert result["contradiction_detected"] is False


def test_customer_received(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message":
            "I received my package.",
        "merchant_message":
            "The order was delivered successfully."
    }

    result = engine.analyze(case)

    assert result["nlp_analysis"]["customer_receipt_status"] == "RECEIVED"


def test_strong_delivery_evidence_score(engine):

    case = {
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": "True",
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my package.",
        "merchant_message":
            "Delivery was completed and proof is available."
    }

    result = engine.analyze(case)

    assert result["evidence_score"] >= 90


def test_failed_delivery_score(engine):

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

    result = engine.analyze(case)

    assert result["evidence_score"] < 70