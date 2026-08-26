import pandas as pd
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


TRAIN_FILE = "data/processed/train.csv"
VALIDATION_FILE = "data/processed/validation.csv"
MODEL_FILE = "models/chargeback_model.pkl"


def prepare_features(df):

    features = df[
        [
            "amount",
            "delivery_status",
            "delivery_proof",
            "refund_status",
            "reason"
        ]
    ].copy()

    # Convert boolean values
    features["delivery_proof"] = (
        features["delivery_proof"]
        .astype(str)
        .map({
            "True": 1,
            "False": 0
        })
    )

    # Convert categorical columns to numbers
    features = pd.get_dummies(
        features,
        columns=[
            "delivery_status",
            "refund_status",
            "reason"
        ]
    )

    return features


def main():

    print("Loading datasets...")

    train_df = pd.read_csv(TRAIN_FILE)
    validation_df = pd.read_csv(VALIDATION_FILE)

    print("Training rows:", len(train_df))
    print("Validation rows:", len(validation_df))

    X_train = prepare_features(train_df)
    X_validation = prepare_features(validation_df)

    # Make sure validation has same columns as training
    X_validation = X_validation.reindex(
        columns=X_train.columns,
        fill_value=0
    )

    y_train = train_df["ground_truth"]
    y_validation = validation_df["ground_truth"]

    print()
    print("Training Random Forest...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    print("Training completed!")

    # Validation prediction
    predictions = model.predict(X_validation)

    print()
    print("===== VALIDATION RESULTS =====")

    print(
        classification_report(
            y_validation,
            predictions,
            zero_division=0
        )
    )

    print("===== CONFUSION MATRIX =====")

    labels = [
        "CONTEST",
        "DO_NOT_CONTEST",
        "HUMAN_REVIEW"
    ]

    matrix = confusion_matrix(
        y_validation,
        predictions,
        labels=labels
    )

    print("Labels:", labels)
    print(matrix)

    # Create models folder
    os.makedirs("models", exist_ok=True)

    # Save trained model and feature columns
    model_package = {
        "model": model,
        "feature_columns": list(X_train.columns)
    }

    joblib.dump(model_package, MODEL_FILE)

    print()
    print("===== MODEL SAVED =====")
    print("Model:", MODEL_FILE)


if __name__ == "__main__":
    main()