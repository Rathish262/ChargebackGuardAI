import pandas as pd
from evaluate_pipeline import analyze_case


df = pd.read_csv("data/test/held_out_test.csv")

print("MISSED TRUE CONTEST CASES")
print("=" * 100)

for i, r in df.iterrows():

    result = analyze_case(r.to_dict())

    if (
        r["ground_truth"] == "CONTEST"
        and result["final_decision"] != "CONTEST"
    ):

        print(f"ROW {i + 1}")
        print("GROUND TRUTH:", r["ground_truth"])
        print("ML:", result["ml_prediction"])
        print("FINAL:", result["final_decision"])
        print("SCORE:", result["evidence_score"])
        print("CONTRADICTION:", result["contradiction"])
        print("REASON:", r["reason"])
        print("DELIVERY:", r["delivery_status"])
        print("PROOF:", r["delivery_proof"])
        print("REFUND:", r["refund_status"])
        print("CUSTOMER:", r["customer_message"])
        print("MERCHANT:", r["merchant_message"])
        print("-" * 100)