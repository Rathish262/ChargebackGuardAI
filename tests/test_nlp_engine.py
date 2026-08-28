import pytest

from nlp_engine import NLPEngine


@pytest.fixture
def engine():
    return NLPEngine()


test_cases = [

    (
        "Simple non receipt",
        "I did not receive my package.",
        "The order was delivered successfully.",
        "NOT_RECEIVED",
        False
    ),

    (
        "Never got package",
        "I never got my package.",
        "The order was delivered.",
        "NOT_RECEIVED",
        False
    ),

    (
        "Package never arrived",
        "My package never arrived.",
        "The order was delivered.",
        "NOT_RECEIVED",
        False
    ),

    (
        "Shipment did not reach customer",
        "The shipment did not reach me.",
        "The order was delivered.",
        "NOT_RECEIVED",
        False
    ),

    (
        "Customer received package",
        "I received my package.",
        "The order was delivered successfully.",
        "RECEIVED",
        False
    ),

    (
        "Customer got order",
        "I got my order.",
        "The order was delivered.",
        "RECEIVED",
        False
    ),

    (
        "Package arrived",
        "My package arrived.",
        "Delivery was completed.",
        "RECEIVED",
        False
    ),

    (
        "Previous confirmation conflict",
        "I never received the package, although I previously confirmed receipt.",
        "Delivery was completed.",
        "CONFLICTING",
        True
    ),

    (
        "Merchant says customer received",
        "I did not receive the package.",
        "The customer received the package.",
        "NOT_RECEIVED",
        True
    ),

    (
        "Merchant confirms customer got order",
        "I never got the order.",
        "The customer got the order.",
        "NOT_RECEIVED",
        True
    ),

    (
        "Unrelated message",
        "I have a problem with my order.",
        "We are investigating the case.",
        "UNKNOWN",
        False
    ),

    (
        "Unauthorized transaction",
        "I do not recognize this transaction.",
        "The transaction requires verification.",
        "UNKNOWN",
        False
    ),

    (
        "Duplicate payment",
        "I was charged twice for the same order.",
        "Two payment records were detected.",
        "UNKNOWN",
        False
    ),
]


@pytest.mark.parametrize(
    "name,customer,merchant,expected_status,expected_conflict",
    test_cases
)
def test_nlp_analysis(
    engine,
    name,
    customer,
    merchant,
    expected_status,
    expected_conflict
):

    result = engine.analyze(
        customer,
        merchant
    )

    actual_status = result["customer"]["receipt_status"]

    actual_conflict = result["contradiction_detected"]

    assert actual_status == expected_status, (
        f"{name}: expected status "
        f"{expected_status}, got {actual_status}"
    )

    assert actual_conflict == expected_conflict, (
        f"{name}: expected conflict "
        f"{expected_conflict}, got {actual_conflict}"
    )


def test_merchant_delivery_detection(engine):

    result = engine.analyze(
        "I did not receive my package.",
        "The order was delivered successfully."
    )

    assert result["merchant"]["delivery_confirmed"] is True


def test_merchant_customer_received_detection(engine):

    result = engine.analyze(
        "I did not receive my package.",
        "The customer received the package."
    )

    assert result["merchant"]["customer_received"] is True


def test_refund_detection(engine):

    result = engine.analyze(
        "I did not receive my package.",
        "The refund has already been issued."
    )

    assert result["merchant"]["refund_issued"] is True


def test_unauthorized_detection(engine):

    result = engine.analyze(
        "I do not recognize this transaction.",
        "The transaction requires verification."
    )

    assert result["merchant"]["unauthorized_claim"] is True


def test_duplicate_charge_detection(engine):

    result = engine.analyze(
        "I was charged twice for the same order.",
        "Two payment records were detected."
    )

    assert result["merchant"]["duplicate_charge_claim"] is True