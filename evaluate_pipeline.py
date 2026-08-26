import pandas as pd
import joblib

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "models/chargeback_model.pkl"
TEST_FILE = "data/test/held_out_test.csv"

LABELS = [
    "CONTEST",
    "DO_NOT_CONTEST",
    "HUMAN_REVIEW"
]


print("===== CHARGEBACKGUARD AI =====")
print("COMPLETE PIPELINE EVALUATION")
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
# INITIALIZE ENGINES
# ==========================================

evidence_engine = EvidenceEngine()
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
# ANALYZE ONE CASE
# ==========================================

def analyze_case(case):

    # -----------------------------
    # ML prediction
    # -----------------------------

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    # -----------------------------
    # Evidence analysis
    # -----------------------------

    evidence = evidence_engine.analyze(case)

    # -----------------------------
    # Final safety decision
    # -----------------------------

    final_result = decision_engine.decide(
        case,
        ml_prediction
    )

    return {
        "ml_prediction": ml_prediction,
        "final_decision": final_result["decision"],
        "evidence_score": evidence["evidence_score"],
        "evidence_level": evidence["evidence_level"],
        "contradiction": evidence["contradiction_detected"]
    }


# ==========================================
# LOAD TEST DATA
# ==========================================

print("Loading held-out test dataset...")

test_df = pd.read_csv(TEST_FILE)

print(
    "Held-out test cases:",
    len(test_df)
)

print()


# ==========================================
# RUN PIPELINE
# ==========================================

ml_predictions = []
final_predictions = []
ground_truth = []

evidence_scores = []
contradictions = []


print("Running complete AI pipeline...")
print()


for _, row in test_df.iterrows():

    case = row.to_dict()

    result = analyze_case(case)

    ml_predictions.append(
        result["ml_prediction"]
    )

    final_predictions.append(
        result["final_decision"]
    )

    ground_truth.append(
        case["ground_truth"]
    )

    evidence_scores.append(
        result["evidence_score"]
    )

    contradictions.append(
        result["contradiction"]
    )


print("Pipeline evaluation completed.")
print()


# ==========================================
# ML MODEL RESULTS
# ==========================================

print("==========================================")
print("1. ML MODEL RESULTS")
print("==========================================")
print()

ml_accuracy = accuracy_score(
    ground_truth,
    ml_predictions
)

print(
    "ML Accuracy:",
    round(ml_accuracy, 4)
)

print()

print("ML Classification Report:")

print(
    classification_report(
        ground_truth,
        ml_predictions,
        labels=LABELS,
        zero_division=0
    )
)

print("ML Confusion Matrix:")

ml_matrix = confusion_matrix(
    ground_truth,
    ml_predictions,
    labels=LABELS
)

print("Labels:", LABELS)
print(ml_matrix)

print()


# ==========================================
# FINAL PIPELINE RESULTS
# ==========================================

print("==========================================")
print("2. FINAL SAFETY PIPELINE RESULTS")
print("==========================================")
print()

final_accuracy = accuracy_score(
    ground_truth,
    final_predictions
)

print(
    "Final Pipeline Accuracy:",
    round(final_accuracy, 4)
)

print()

print("Final Pipeline Classification Report:")

print(
    classification_report(
        ground_truth,
        final_predictions,
        labels=LABELS,
        zero_division=0
    )
)

print("Final Pipeline Confusion Matrix:")

final_matrix = confusion_matrix(
    ground_truth,
    final_predictions,
    labels=LABELS
)

print("Labels:", LABELS)
print(final_matrix)

print()


# ==========================================
# DECISION DISTRIBUTION
# ==========================================

print("==========================================")
print("3. FINAL DECISION DISTRIBUTION")
print("==========================================")
print()

print(
    "CONTEST:",
    final_predictions.count("CONTEST")
)

print(
    "DO_NOT_CONTEST:",
    final_predictions.count("DO_NOT_CONTEST")
)

print(
    "HUMAN_REVIEW:",
    final_predictions.count("HUMAN_REVIEW")
)

print()


# ==========================================
# ML DECISION DISTRIBUTION
# ==========================================

print("==========================================")
print("4. ML PREDICTION DISTRIBUTION")
print("==========================================")
print()

print(
    "CONTEST:",
    ml_predictions.count("CONTEST")
)

print(
    "DO_NOT_CONTEST:",
    ml_predictions.count("DO_NOT_CONTEST")
)

print(
    "HUMAN_REVIEW:",
    ml_predictions.count("HUMAN_REVIEW")
)

print()


# ==========================================
# CONTEST METRICS
# ==========================================

def calculate_contest_metrics(
    actual,
    predicted
):

    tp = 0
    fp = 0
    fn = 0

    for a, p in zip(actual, predicted):

        if (
            a == "CONTEST"
            and p == "CONTEST"
        ):

            tp += 1

        elif (
            a != "CONTEST"
            and p == "CONTEST"
        ):

            fp += 1

        elif (
            a == "CONTEST"
            and p != "CONTEST"
        ):

            fn += 1

    if tp + fp > 0:

        precision = tp / (tp + fp)

    else:

        precision = 0

    if tp + fn > 0:

        recall = tp / (tp + fn)

    else:

        recall = 0

    return tp, fp, fn, precision, recall


# ==========================================
# ML CONTEST METRICS
# ==========================================

ml_tp, ml_fp, ml_fn, ml_precision, ml_recall = (
    calculate_contest_metrics(
        ground_truth,
        ml_predictions
    )
)


print("==========================================")
print("5. ML CONTEST METRICS")
print("==========================================")
print()

print("True Positives:", ml_tp)
print("False Positives:", ml_fp)
print("False Negatives:", ml_fn)

print(
    "Contest Precision:",
    round(ml_precision, 3)
)

print(
    "Contest Recall:",
    round(ml_recall, 3)
)

print()


# ==========================================
# FINAL CONTEST METRICS
# ==========================================

final_tp, final_fp, final_fn, final_precision, final_recall = (
    calculate_contest_metrics(
        ground_truth,
        final_predictions
    )
)


print("==========================================")
print("6. FINAL PIPELINE CONTEST METRICS")
print("==========================================")
print()

print("True Positives:", final_tp)
print("False Positives:", final_fp)
print("False Negatives:", final_fn)

print(
    "Contest Precision:",
    round(final_precision, 3)
)

print(
    "Contest Recall:",
    round(final_recall, 3)
)

print()


# ==========================================
# SAFETY STATISTICS
# ==========================================

print("==========================================")
print("7. SAFETY STATISTICS")
print("==========================================")
print()

contradiction_count = sum(
    contradictions
)

print(
    "Cases with contradictions:",
    contradiction_count
)

print(
    "Cases sent to HUMAN_REVIEW:",
    final_predictions.count("HUMAN_REVIEW")
)

print(
    "Cases automatically CONTESTED:",
    final_predictions.count("CONTEST")
)

print(
    "Cases automatically NOT CONTESTED:",
    final_predictions.count("DO_NOT_CONTEST")
)

print()


# ==========================================
# FINAL SUMMARY
# ==========================================

print("==========================================")
print("8. FINAL SUMMARY")
print("==========================================")
print()

print(
    "ML Accuracy:",
    round(ml_accuracy, 4)
)

print(
    "Final Pipeline Accuracy:",
    round(final_accuracy, 4)
)

print(
    "ML Contest Recall:",
    round(ml_recall, 3)
)

print(
    "Final Contest Recall:",
    round(final_recall, 3)
)

print()

print("===== EVALUATION COMPLETED =====")