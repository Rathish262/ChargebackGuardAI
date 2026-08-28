import pandas as pd
import joblib

from evaluate_pipeline import prepare_features, analyze_case
from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"


def test_model_exists():

    package = joblib.load(MODEL_FILE)

    assert package is not None


def test_held_out_dataset_exists():

    df = pd.read_csv(TEST_FILE)

    assert len(df) == 150


def test_strong_delivery_case():

    case = {
        "dispute_id": "TEST_STRONG",
        "amount": 5000,
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": True,
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "Delivery was completed and proof is available."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "CONTEST"


def test_contradiction_case():

    case = {
        "dispute_id": "TEST_CONTRADICTION",
        "amount": 5000,
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": True,
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "Customer previously confirmed that the order was received."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "HUMAN_REVIEW"


def test_refund_case():

    case = {
        "dispute_id": "TEST_REFUND",
        "amount": 5000,
        "reason": "product_not_received",
        "delivery_status": "delivered",
        "delivery_proof": True,
        "refund_status": "issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "Refund has already been issued."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "DO_NOT_CONTEST"


def test_delivery_failure_case():

    case = {
        "dispute_id": "TEST_FAILURE",
        "amount": 5000,
        "reason": "product_not_received",
        "delivery_status": "failed",
        "delivery_proof": False,
        "refund_status": "not_issued",
        "customer_message":
            "I did not receive my order.",
        "merchant_message":
            "Delivery attempt failed."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "DO_NOT_CONTEST"


def test_unauthorized_transaction():

    case = {
        "dispute_id": "TEST_UNAUTHORIZED",
        "amount": 5000,
        "reason": "unauthorized_transaction",
        "delivery_status": "unknown",
        "delivery_proof": False,
        "refund_status": "not_issued",
        "customer_message":
            "I do not recognize this transaction.",
        "merchant_message":
            "The transaction requires further verification."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "HUMAN_REVIEW"


def test_duplicate_charge():

    case = {
        "dispute_id": "TEST_DUPLICATE",
        "amount": 5000,
        "reason": "duplicate_charge",
        "delivery_status": "delivered",
        "delivery_proof": True,
        "refund_status": "not_issued",
        "customer_message":
            "I was charged twice for the same order.",
        "merchant_message":
            "Two payment records were detected."
    }

    result = analyze_case(case)

    assert result["final_decision"] == "HUMAN_REVIEW"