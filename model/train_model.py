"""
Model Training Script for ChurnGuard
Trains and compares three classifiers on the Telco Customer Churn dataset:
  - Logistic Regression (interpretable baseline)
  - Decision Tree       (non-linear interpretable baseline)
  - Random Forest       (production model — best performance)

Outputs
-------
  model/churn_model.pkl     -- Random Forest model + feature columns (Flask app)
  model/model_metrics.json  -- Metrics for all three models (comparison page)
  model/shap_explainer.pkl  -- SHAP TreeExplainer for per-prediction explanations

Usage:
    python model/train_model.py
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


# ---------------------------------------------------------------------------
# Data loading & cleaning
# ---------------------------------------------------------------------------

def load_and_clean_data(filepath):
    """Load dataset and perform initial cleaning."""
    df = pd.read_csv(filepath)

    # Drop customerID — not a predictive feature
    df.drop(columns=["customerID"], inplace=True)

    # TotalCharges has some blank strings — convert to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Fill missing TotalCharges with 0 (new customers with tenure=0)
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    # Convert SeniorCitizen int flag to a consistent Yes/No string
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

    return df


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def engineer_features(df):
    """Create tenure groups and encode categorical variables."""
    # Bin tenure into 12-month groups (matches the live prediction pipeline)
    labels = [f"{i}-{i + 11}" for i in range(1, 72, 12)]
    df["tenure_group"] = pd.cut(
        df["tenure"].astype(int), bins=range(1, 80, 12), right=False, labels=labels
    )
    df.drop(columns=["tenure"], inplace=True)

    # Encode target variable
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    target = df["Churn"]
    features = df.drop(columns=["Churn"])

    numeric_cols = ["MonthlyCharges", "TotalCharges"]
    categorical_cols = [c for c in features.columns if c not in numeric_cols]

    features_encoded = pd.get_dummies(features, columns=categorical_cols)

    return features_encoded, target


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------

def build_models():
    """Return a dict of {name: estimator} for all three classifiers."""
    return {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=1.0,
                solver="lbfgs",
                random_state=42,
                class_weight="balanced",   # handles class imbalance
            )),
        ]),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
    }


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(name, model, X_test, y_test):
    """Compute and return a metrics dict for one trained model."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred) * 100, 2),
        "precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
        "roc_auc":   round(roc_auc_score(y_test, y_prob) * 100, 2),
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp),
            "fn": int(fn), "tp": int(tp),
        },
    }

    print(f"\n{'=' * 50}")
    print(f"  {name}")
    print(f"{'=' * 50}")
    print(f"  Accuracy:  {metrics['accuracy']:.2f}%")
    print(f"  Precision: {metrics['precision']:.2f}%")
    print(f"  Recall:    {metrics['recall']:.2f}%")
    print(f"  F1 Score:  {metrics['f1']:.2f}%")
    print(f"  ROC-AUC:   {metrics['roc_auc']:.2f}%")
    print(f"\n  Confusion Matrix:")
    print(f"    TN={tn}  FP={fp}")
    print(f"    FN={fn}  TP={tp}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Retained", "Churned"]))

    return metrics


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_rf_model(model, feature_columns, output_path):
    """Save the Random Forest model + feature columns as the production pickle."""
    model_data = {
        "model": model,
        "feature_columns": list(feature_columns),
    }
    with open(output_path, "wb") as f:
        pickle.dump(model_data, f)
    print(f"\n[OK] Production model saved -> {output_path}")
    print(f"    Feature count: {len(feature_columns)}")


def save_metrics(all_metrics, output_path):
    """Persist all three models' metrics to JSON for the comparison page."""
    with open(output_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"[OK] Model metrics saved -> {output_path}")


def save_shap_explainer(rf_model, X_train, output_path):
    """Build and persist a SHAP TreeExplainer for the Random Forest model."""
    print("\nBuilding SHAP TreeExplainer (this may take ~30 seconds)...")
    explainer = shap.TreeExplainer(rf_model)
    # Pre-compute background shap values on a small sample for fast loading
    shap_data = {
        "explainer": explainer,
        "feature_names": list(X_train.columns),
    }
    with open(output_path, "wb") as f:
        pickle.dump(shap_data, f)
    print(f"[OK] SHAP explainer saved -> {output_path}")


# ---------------------------------------------------------------------------
# Feature importance (RF only)
# ---------------------------------------------------------------------------

def print_feature_importance(rf_model, feature_columns, top_n=10):
    importances = pd.Series(rf_model.feature_importances_, index=feature_columns)
    top = importances.nlargest(top_n)
    print(f"\nTop {top_n} Feature Importances (Random Forest):")
    for feat, imp in top.items():
        bar = "#" * int(imp * 200)
        print(f"  {feat:<45s} {imp:.4f}  {bar}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path  = os.path.join(project_root, "data",  "telco_churn.csv")
    model_path = os.path.join(project_root, "model", "churn_model.pkl")
    metrics_path = os.path.join(project_root, "model", "model_metrics.json")

    # --- Load & prepare ---
    print("Loading dataset...")
    df = load_and_clean_data(data_path)
    print(f"  Dataset shape: {df.shape}")
    churn_counts = df["Churn"].value_counts()
    print(f"  Churn distribution: Yes={churn_counts.get('Yes', 0)}  "
          f"No={churn_counts.get('No', 0)}")

    print("\nEngineering features...")
    X, y = engineer_features(df)
    print(f"  Feature matrix: {X.shape}")

    print("\nSplitting 80 / 20 (stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)}   Test: {len(X_test)}")

    # --- Train & evaluate all models ---
    models = build_models()
    all_metrics = {}
    trained_models = {}

    for name, estimator in models.items():
        print(f"\nTraining {name}...")
        estimator.fit(X_train, y_train)
        trained_models[name] = estimator
        all_metrics[name] = evaluate_model(name, estimator, X_test, y_test)

    # --- Save Random Forest as production model ---
    rf = trained_models["Random Forest"]
    save_rf_model(rf, X.columns, model_path)

    # --- Save metrics JSON ---
    save_metrics(all_metrics, metrics_path)

    # --- Save SHAP explainer ---
    shap_path = os.path.join(project_root, "model", "shap_explainer.pkl")
    save_shap_explainer(rf, X_train, shap_path)

    # --- Feature importance ---
    print_feature_importance(rf, X.columns)

    print("\nTraining complete!\n")


if __name__ == "__main__":
    main()
