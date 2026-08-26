import csv
import random
from datetime import datetime, timedelta


random.seed(42)


def create_case(case_id):

    amount = random.randint(500, 20000)

    scenario = random.choice([
        "strong_delivery_evidence",
        "missing_delivery_evidence",
        "refund_issued",
        "delivery_failure",
        "contradictory_evidence",
        "unauthorized_transaction",
        "duplicate_charge",
        "weak_evidence"
    ])

    transaction_date = datetime.now() - timedelta(
        days=random.randint(1, 180)
    )

    delivery_date = transaction_date + timedelta(
        days=random.randint(1, 10)
    )


    # -----------------------------------------
    # Scenario 1: Strong delivery evidence
    # -----------------------------------------

    if scenario == "strong_delivery_evidence":

        reason = "product_not_received"
        delivery_status = "delivered"
        delivery_proof = True
        refund_status = "not_issued"

        customer_message = (
            "I did not receive my order."
        )

        merchant_message = (
            "Delivery was completed and proof is available."
        )

        ground_truth = "CONTEST"


    # -----------------------------------------
    # Scenario 2: Missing evidence
    # -----------------------------------------

    elif scenario == "missing_delivery_evidence":

        reason = "product_not_received"
        delivery_status = "unknown"
        delivery_proof = False
        refund_status = "not_issued"

        customer_message = (
            "I did not receive my order."
        )

        merchant_message = (
            "We could not find delivery confirmation."
        )

        ground_truth = "HUMAN_REVIEW"


    # -----------------------------------------
    # Scenario 3: Refund already issued
    # -----------------------------------------

    elif scenario == "refund_issued":

        reason = "product_not_received"
        delivery_status = "delivered"
        delivery_proof = True
        refund_status = "issued"

        customer_message = (
            "I did not receive my order."
        )

        merchant_message = (
            "Refund has already been issued to the customer."
        )

        ground_truth = "DO_NOT_CONTEST"


    # -----------------------------------------
    # Scenario 4: Delivery failed
    # -----------------------------------------

    elif scenario == "delivery_failure":

        reason = "product_not_received"
        delivery_status = "failed"
        delivery_proof = False
        refund_status = "not_issued"

        customer_message = (
            "I did not receive my order."
        )

        merchant_message = (
            "Courier delivery attempt failed."
        )

        ground_truth = "DO_NOT_CONTEST"


    # -----------------------------------------
    # Scenario 5: Contradictory evidence
    # -----------------------------------------

    elif scenario == "contradictory_evidence":

        reason = "product_not_received"
        delivery_status = "delivered"
        delivery_proof = True
        refund_status = "not_issued"

        customer_message = (
            "I did not receive my order."
        )

        merchant_message = (
            "Customer previously confirmed that "
            "the order was received."
        )

        ground_truth = "HUMAN_REVIEW"


    # -----------------------------------------
    # Scenario 6: Unauthorized transaction
    # -----------------------------------------

    elif scenario == "unauthorized_transaction":

        reason = "unauthorized_transaction"
        delivery_status = "unknown"
        delivery_proof = False
        refund_status = "not_issued"

        customer_message = (
            "I do not recognize this transaction."
        )

        merchant_message = (
            "The transaction requires further verification."
        )

        ground_truth = "HUMAN_REVIEW"


    # -----------------------------------------
    # Scenario 7: Duplicate charge
    # -----------------------------------------

    elif scenario == "duplicate_charge":

        reason = "duplicate_charge"
        delivery_status = "delivered"
        delivery_proof = True
        refund_status = "not_issued"

        customer_message = (
            "I was charged twice for the same order."
        )

        merchant_message = (
            "Two payment records were detected."
        )

        ground_truth = "HUMAN_REVIEW"


    # -----------------------------------------
    # Scenario 8: Weak evidence
    # -----------------------------------------

    else:

        reason = "product_not_as_described"
        delivery_status = "delivered"
        delivery_proof = True
        refund_status = "not_issued"

        customer_message = (
            "The product I received was not as described."
        )

        merchant_message = (
            "No additional evidence is available."
        )

        ground_truth = "HUMAN_REVIEW"


    return {
        "dispute_id": f"CB{case_id:05d}",
        "amount": amount,
        "scenario": scenario,
        "reason": reason,
        "delivery_status": delivery_status,
        "delivery_proof": delivery_proof,
        "refund_status": refund_status,
        "customer_message": customer_message,
        "merchant_message": merchant_message,
        "transaction_date": transaction_date.strftime(
            "%Y-%m-%d"
        ),
        "delivery_date": delivery_date.strftime(
            "%Y-%m-%d"
        ),
        "ground_truth": ground_truth
    }


def generate_dataset(number_of_cases):

    cases = []

    for i in range(1, number_of_cases + 1):

        cases.append(create_case(i))

    return cases


def save_dataset(cases, filename):

    fieldnames = cases[0].keys()

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(cases)


if __name__ == "__main__":

    cases = generate_dataset(1000)

    save_dataset(
        cases,
        "data/raw/chargeback_cases_v2.csv"
    )

    print("V2 dataset generated successfully!")
    print(f"Total cases: {len(cases)}")