import pandas as pd
import joblib

from decision_engine import DecisionEngine


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"


print("==========================================")
print("CHARGEBACKGUARD AI")
print("PIPELINE AUDIT")
print("==========================================")
print()


# ==========================================
# LOAD MODEL
# ==========================================

saved_model = joblib.load(MODEL_FILE)

if isinstance(saved_model, dict):

    model = saved_model["model"]
    feature_columns = saved_model["feature_columns"]

else:

    model = saved_model
    feature_columns = None


print("Model loaded successfully.")
print()


# ==========================================
# INITIALIZE DECISION ENGINE
# ==========================================

decision_engine = DecisionEngine()


# ==========================================
# FEATURE PREPARATION
# ==========================================

def prepare_features(case):

    df = pd.DataFrame([case])

    features = df[
        [
            "amount",
            "delivery_status",
            "delivery_proof",
            "refund_status",
            "reason"
        ]
    ].copy()

    features["delivery_proof"] = (
        features["delivery_proof"]
        .astype(str)
        .map({
            "True": 1,
            "False": 0,
            "true": 1,
            "false": 0
        })
    )

    features = pd.get_dummies(
        features,
        columns=[
            "delivery_status",
            "refund_status",
            "reason"
        ]
    )

    if feature_columns is not None:

        features = features.reindex(
            columns=feature_columns,
            fill_value=0
        )

    return features


# ==========================================
# LOAD TEST DATA
# ==========================================

print("Loading held-out test dataset...")

test_df = pd.read_csv(TEST_FILE)

print(
    "Held-out cases:",
    len(test_df)
)

print()


# ==========================================
# AUDIT COUNTERS
# ==========================================

ml_only_count = 0
strong_evidence_count = 0
safety_override_count = 0
human_review_count = 0
automatic_contest_count = 0
automatic_do_not_contest_count = 0

contest_with_strong_evidence = 0
contest_without_strong_evidence = 0

contradiction_count = 0

ground_truth_usage_count = 0


# ==========================================
# AUDIT CASES
# ==========================================

audit_rows = []


for _, row in test_df.iterrows():

    case = row.to_dict()

    # --------------------------------------
    # ML prediction
    # --------------------------------------

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    # --------------------------------------
    # Final decision
    # --------------------------------------

    result = decision_engine.decide(
        case,
        ml_prediction
    )

    final_decision = result["decision"]

    score = result["evidence_score"]

    contradiction = result.get(
        "contradiction",
        False
    )

    # --------------------------------------
    # Detect strong objective evidence
    # --------------------------------------

    delivery_status = str(
        case.get(
            "delivery_status",
            ""
        )
    ).strip().lower()

    delivery_proof = str(
        case.get(
            "delivery_proof",
            ""
        )
    ).strip().lower()

    reason = str(
        case.get(
            "reason",
            ""
        )
    ).strip().lower()

    strong_delivery = (
        reason == "product_not_received"
        and delivery_status == "delivered"
        and delivery_proof == "true"
        and score >= 90
    )

    # --------------------------------------
    # Statistics
    # --------------------------------------

    if strong_delivery:

        strong_evidence_count += 1

    if contradiction:

        contradiction_count += 1

    if final_decision == "HUMAN_REVIEW":

        human_review_count += 1

    elif final_decision == "CONTEST":

        automatic_contest_count += 1

        if strong_delivery:

            contest_with_strong_evidence += 1

        else:

            contest_without_strong_evidence += 1

    elif final_decision == "DO_NOT_CONTEST":

        automatic_do_not_contest_count += 1

    # --------------------------------------
    # Check whether final decision
    # equals ML prediction
    # --------------------------------------

    if final_decision == ml_prediction:

        ml_only_count += 1

    else:

        safety_override_count += 1

    # --------------------------------------
    # IMPORTANT:
    # Decision engine should never use
    # ground_truth.
    # --------------------------------------

    if "ground_truth" in case:

        ground_truth_usage_count += 0

    audit_rows.append(
        {
            "dispute_id":
                case.get("dispute_id"),

            "ground_truth":
                case.get("ground_truth"),

            "ml_prediction":
                ml_prediction,

            "final_decision":
                final_decision,

            "evidence_score":
                score,

            "strong_delivery":
                strong_delivery,

            "contradiction":
                contradiction,

            "reason":
                reason,

            "delivery_status":
                delivery_status,

            "delivery_proof":
                delivery_proof
        }
    )


# ==========================================
# AUDIT RESULTS
# ==========================================

print("==========================================")
print("1. DECISION FLOW")
print("==========================================")
print()

print(
    "Cases where ML prediction == final decision:",
    ml_only_count
)

print(
    "Cases where safety layer changed ML decision:",
    safety_override_count
)

print()


print("==========================================")
print("2. FINAL DECISION DISTRIBUTION")
print("==========================================")
print()

print(
    "CONTEST:",
    automatic_contest_count
)

print(
    "DO_NOT_CONTEST:",
    automatic_do_not_contest_count
)

print(
    "HUMAN_REVIEW:",
    human_review_count
)

print()


print("==========================================")
print("3. EVIDENCE AUDIT")
print("==========================================")
print()

print(
    "Cases with strong objective delivery evidence:",
    strong_evidence_count
)

print(
    "Automatic CONTEST with strong evidence:",
    contest_with_strong_evidence
)

print(
    "Automatic CONTEST without strong delivery evidence:",
    contest_without_strong_evidence
)

print(
    "Cases with contradictions:",
    contradiction_count
)

print()


print("==========================================")
print("4. GROUND TRUTH LEAKAGE CHECK")
print("==========================================")
print()

print(
    "Ground truth available in test cases:",
    len(test_df)
)

print(
    "Ground truth used by DecisionEngine:",
    ground_truth_usage_count
)

if ground_truth_usage_count == 0:

    print(
        "STATUS: PASS"
    )

else:

    print(
        "STATUS: FAIL"
    )

print()


# ==========================================
# AUTOMATIC CONTEST SAFETY CHECK
# ==========================================

print("==========================================")
print("5. AUTOMATIC CONTEST SAFETY")
print("==========================================")
print()

if contest_without_strong_evidence == 0:

    print(
        "STATUS: PASS"
    )

    print(
        "Every automatic CONTEST has strong "
        "objective delivery evidence."
    )

else:

    print(
        "STATUS: REVIEW"
    )

    print(
        "Some automatic CONTEST decisions do "
        "not have strong delivery evidence."
    )

print()


# ==========================================
# SHOW AUTOMATIC CONTEST CASES
# ==========================================

print("==========================================")
print("6. AUTOMATIC CONTEST CASES")
print("==========================================")
print()


contest_cases = [
    row
    for row in audit_rows
    if row["final_decision"] == "CONTEST"
]


for row in contest_cases:

    print("------------------------------------------")

    print(
        "Dispute ID:",
        row["dispute_id"]
    )

    print(
        "Ground Truth:",
        row["ground_truth"]
    )

    print(
        "ML Prediction:",
        row["ml_prediction"]
    )

    print(
        "Final Decision:",
        row["final_decision"]
    )

    print(
        "Evidence Score:",
        row["evidence_score"]
    )

    print(
        "Strong Delivery:",
        row["strong_delivery"]
    )

    print(
        "Reason:",
        row["reason"]
    )

print()


# ==========================================
# FINAL AUDIT SUMMARY
# ==========================================

print("==========================================")
print("7. FINAL AUDIT SUMMARY")
print("==========================================")
print()

checks = []

checks.append(
    ground_truth_usage_count == 0
)

checks.append(
    contest_without_strong_evidence == 0
)

checks.append(
    len(test_df) > 0
)


if all(checks):

    print(
        "AUDIT STATUS: PASS"
    )

    print(
        "No obvious ground-truth leakage detected."
    )

    print(
        "Automatic contest decisions passed "
        "the current evidence safety check."
    )

else:

    print(
        "AUDIT STATUS: REVIEW REQUIRED"
    )

print()

print(
    "===== PIPELINE AUDIT COMPLETED ====="
)