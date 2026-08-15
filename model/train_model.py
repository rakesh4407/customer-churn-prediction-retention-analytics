"""
Model Training Script for ChurnGuard
Trains a Random Forest Classifier on the Telco Customer Churn dataset.
Run this script to generate a fresh model compatible with the current
scikit-learn version.

Usage:
    python model/train_model.py
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)


def load_and_clean_data(filepath):
    """Load dataset and perform initial cleaning."""
    df = pd.read_csv(filepath)

    # Drop customerID — not a predictive feature
    df.drop(columns=["customerID"], inplace=True)

    # TotalCharges has some blank strings — convert to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Fill missing TotalCharges with 0 (new customers with tenure=0)
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    # Convert SeniorCitizen to string for consistent one-hot encoding
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

    return df


def engineer_features(df):
    """Create tenure groups and encode categorical variables."""
    # Bin tenure into 12-month groups
    labels = [f"{i}-{i + 11}" for i in range(1, 72, 12)]
    df["tenure_group"] = pd.cut(
        df["tenure"].astype(int), bins=range(1, 80, 12), right=False, labels=labels
    )

    # Drop raw tenure — replaced by tenure_group
    df.drop(columns=["tenure"], inplace=True)

    # Encode target variable
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # Separate features and target
    target = df["Churn"]
    features = df.drop(columns=["Churn"])

    # Identify numeric and categorical columns
    numeric_cols = ["MonthlyCharges", "TotalCharges"]
    categorical_cols = [c for c in features.columns if c not in numeric_cols]

    # One-hot encode categorical features
    features_encoded = pd.get_dummies(features, columns=categorical_cols)

    return features_encoded, target


def train_model(X_train, y_train):
    """Train a Random Forest Classifier."""
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Print model evaluation metrics."""
    y_pred = model.predict(X_test)

    print("\n" + "=" * 50)
    print("MODEL EVALUATION RESULTS")
    print("=" * 50)
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Retained", "Churned"]))


def save_model(model, feature_columns, output_path):
    """Save model and feature columns together."""
    model_data = {
        "model": model,
        "feature_columns": list(feature_columns),
    }
    with open(output_path, "wb") as f:
        pickle.dump(model_data, f)
    print(f"\nModel saved to: {output_path}")
    print(f"Feature count: {len(feature_columns)}")


def main():
    # Resolve paths relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "data", "telco_churn.csv")
    model_path = os.path.join(project_root, "model", "churn_model.pkl")

    print("Loading dataset...")
    df = load_and_clean_data(data_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Churn distribution:\n{df['Churn'].value_counts()}")

    print("\nEngineering features...")
    X, y = engineer_features(df)
    print(f"Feature matrix shape: {X.shape}")

    print("\nSplitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")

    print("\nTraining Random Forest...")
    model = train_model(X_train, y_train)

    evaluate_model(model, X_test, y_test)

    save_model(model, X.columns, model_path)

    # Print top 10 feature importances
    importances = pd.Series(model.feature_importances_, index=X.columns)
    top_features = importances.nlargest(10)
    print("\nTop 10 Feature Importances:")
    for feat, imp in top_features.items():
        print(f"  {feat:40s} {imp:.4f}")

    print("\nTraining complete!")


if __name__ == "__main__":
    main()
