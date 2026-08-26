import csv
import random
from datetime import datetime, timedelta

random.seed(42)


REASONS = [
    "product_not_received",
    "product_not_as_described",
    "duplicate_charge",
    "unauthorized_transaction"
]

DELIVERY_STATUS = [
    "delivered",
    "failed",
    "unknown"
]

REFUND_STATUS = [
    "not_issued",
    "issued"
]


def generate_case(case_number):

    amount = random.randint(500, 15000)

    reason = random.choice(REASONS)

    delivery_status = random.choice(DELIVERY_STATUS)

    refund_status = random.choice(REFUND_STATUS)

    delivery_proof = random.choice([True, False])

    customer_messages = [
        "I did not receive my order.",
        "I received the product but there is an issue.",
        "I don't recognize this transaction.",
        "I was charged twice.",
        "The product I received is different from what I ordered."
    ]

    merchant_messages = [
        "Order was processed normally.",
        "Customer contacted support.",
        "Delivery was completed.",
        "Refund request was received.",
        "No customer communication was received."
    ]

    customer_message = random.choice(customer_messages)

    merchant_message = random.choice(merchant_messages)

    transaction_date = datetime.now() - timedelta(
        days=random.randint(1, 180)
    )

    delivery_date = transaction_date + timedelta(
        days=random.randint(1, 10)
    )

    # Synthetic ground truth

    if refund_status == "issued":

        ground_truth = "DO_NOT_CONTEST"

    elif delivery_status == "delivered" and delivery_proof:

        ground_truth = "CONTEST"

    elif delivery_status == "failed":

        ground_truth = "DO_NOT_CONTEST"

    else:

        ground_truth = "HUMAN_REVIEW"

    return {
        "dispute_id": f"CB{case_number:05d}",
        "amount": amount,
        "reason": reason,
        "delivery_status": delivery_status,
        "delivery_proof": delivery_proof,
        "refund_status": refund_status,
        "customer_message": customer_message,
        "merchant_message": merchant_message,
        "transaction_date": transaction_date.strftime("%Y-%m-%d"),
        "delivery_date": delivery_date.strftime("%Y-%m-%d"),
        "ground_truth": ground_truth
    }


def generate_dataset(number_of_cases):

    cases = []

    for i in range(1, number_of_cases + 1):

        case = generate_case(i)

        cases.append(case)

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

    dataset = generate_dataset(200)

    save_dataset(
        dataset,
        "data/raw/chargeback_cases.csv"
    )

    print("Dataset generated successfully!")
    print(f"Total cases: {len(dataset)}")