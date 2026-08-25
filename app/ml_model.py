"""
ML Model service for ChurnGuard.
Handles model loading, feature engineering, prediction, feature importance,
and multi-model comparison metrics.
"""

import json
import os
import pickle
import shap
import pandas as pd
import numpy as np


class ChurnModel:
    """Wrapper around the trained Random Forest model."""

    # Valid values for each categorical input field
    VALID_OPTIONS = {
        "gender": ["Male", "Female"],
        "SeniorCitizen": ["Yes", "No"],
        "Partner": ["Yes", "No"],
        "Dependents": ["Yes", "No"],
        "PhoneService": ["Yes", "No"],
        "MultipleLines": ["Yes", "No", "No phone service"],
        "InternetService": ["DSL", "Fiber optic", "No"],
        "OnlineSecurity": ["Yes", "No", "No internet service"],
        "OnlineBackup": ["Yes", "No", "No internet service"],
        "DeviceProtection": ["Yes", "No", "No internet service"],
        "TechSupport": ["Yes", "No", "No internet service"],
        "StreamingTV": ["Yes", "No", "No internet service"],
        "StreamingMovies": ["Yes", "No", "No internet service"],
        "Contract": ["Month-to-month", "One year", "Two year"],
        "PaperlessBilling": ["Yes", "No"],
        "PaymentMethod": [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
    }

    NUMERIC_FIELDS = {
        "MonthlyCharges": {"min": 0, "max": 500, "type": float},
        "TotalCharges": {"min": 0, "max": 10000, "type": float},
        "tenure": {"min": 0, "max": 72, "type": int},
    }

    def __init__(self, model_path):
        """Load the trained model, feature columns, and SHAP explainer from disk."""
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)
        self.model = model_data["model"]
        self.feature_columns = model_data["feature_columns"]

        # Load SHAP explainer if available
        shap_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "model", "shap_explainer.pkl"
        )
        self._shap_explainer = None
        if os.path.exists(shap_path):
            with open(shap_path, "rb") as f:
                shap_data = pickle.load(f)
            self._shap_explainer = shap_data["explainer"]

    def validate_input(self, form_data):
        """Validate user input and return cleaned data dict or error messages."""
        errors = []
        cleaned = {}

        # Validate categorical fields
        for field, valid_values in self.VALID_OPTIONS.items():
            value = form_data.get(field, "").strip()
            if not value:
                errors.append(f"{field} is required.")
            elif value not in valid_values:
                errors.append(
                    f"Invalid value for {field}: '{value}'. "
                    f"Must be one of: {', '.join(valid_values)}"
                )
            else:
                cleaned[field] = value

        # Validate numeric fields
        for field, rules in self.NUMERIC_FIELDS.items():
            value = form_data.get(field, "").strip()
            if not value:
                errors.append(f"{field} is required.")
            else:
                try:
                    num_value = rules["type"](value)
                    if num_value < rules["min"] or num_value > rules["max"]:
                        errors.append(
                            f"{field} must be between {rules['min']} and {rules['max']}."
                        )
                    else:
                        cleaned[field] = num_value
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number.")

        return cleaned, errors

    def predict(self, cleaned_data):
        """
        Run churn prediction on validated input.
        Returns (prediction_label, confidence_percentage).
        """
        # Build a single-row DataFrame
        df = pd.DataFrame([cleaned_data])

        # Feature engineering: bin tenure into groups
        labels = [f"{i}-{i + 11}" for i in range(1, 72, 12)]
        df["tenure_group"] = pd.cut(
            df["tenure"].astype(int),
            bins=range(1, 80, 12),
            right=False,
            labels=labels,
        )
        df.drop(columns=["tenure"], inplace=True)

        # Identify categorical columns for encoding
        numeric_cols = ["MonthlyCharges", "TotalCharges"]
        categorical_cols = [c for c in df.columns if c not in numeric_cols]

        # One-hot encode
        df_encoded = pd.get_dummies(df, columns=categorical_cols)

        # Align columns with training features
        # Add missing columns as 0, drop extra columns
        for col in self.feature_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[self.feature_columns]

        # Predict
        prediction = self.model.predict(df_encoded)[0]
        probability = self.model.predict_proba(df_encoded)[0]

        churn_prob = probability[1] * 100  # probability of churning
        retain_prob = probability[0] * 100  # probability of staying

        result = {
            "prediction": "Churn" if prediction == 1 else "Retain",
            "is_churn": bool(prediction == 1),
            "churn_probability": round(churn_prob, 1),
            "retain_probability": round(retain_prob, 1),
            "confidence": round(max(churn_prob, retain_prob), 1),
            "risk_level": self._get_risk_level(churn_prob),
            "shap_explanation": self.get_shap_explanation(df_encoded),
        }
        return result

    def _get_risk_level(self, churn_prob):
        """Categorize churn probability into risk levels."""
        if churn_prob >= 70:
            return "High"
        elif churn_prob >= 40:
            return "Medium"
        else:
            return "Low"

    def get_feature_importance(self, top_n=10):
        """Return top N most important features for the model."""
        importances = pd.Series(
            self.model.feature_importances_, index=self.feature_columns
        )
        top = importances.nlargest(top_n)

        # Clean up feature names for display
        results = []
        for feat, imp in top.items():
            display_name = feat.replace("_", " ").title()
            results.append({
                "feature": feat,
                "display_name": display_name,
                "importance": round(imp * 100, 2),
            })
        return results

    def get_model_comparison(self):
        """
        Load and return model comparison metrics from model_metrics.json.
        Returns a dict with model names as keys and metric dicts as values,
        plus a 'best' sub-dict highlighting the winner per metric.
        """
        metrics_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "model", "model_metrics.json"
        )
        if not os.path.exists(metrics_path):
            return None

        with open(metrics_path, "r") as f:
            data = json.load(f)

        metric_keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        best = {}
        for metric in metric_keys:
            best[metric] = max(data, key=lambda m: data[m][metric])

        return {"models": data, "best": best}

    def get_shap_explanation(self, df_encoded, top_n=5):
        """
        Compute SHAP values for a single encoded customer row.
        Returns a list of top_n factors with direction, label, and SHAP value.
        Each factor: {label, raw_feature, shap_value, direction ('up'|'down')}
        """
        if self._shap_explainer is None:
            return None

        try:
            shap_values = self._shap_explainer.shap_values(df_encoded)
            # For binary classification, shap_values is a list [class0, class1]
            # We want class 1 (churn) values
            if isinstance(shap_values, list):
                sv = shap_values[1][0]  # churn class, first (only) row
            else:
                sv = shap_values[0]

            feature_names = list(df_encoded.columns)
            shap_series = pd.Series(sv, index=feature_names)

            # Get top factors by absolute SHAP value
            top_features = shap_series.abs().nlargest(top_n).index

            factors = []
            for feat in top_features:
                val = float(shap_series[feat])
                # Build human-readable label from feature name
                label = feat.replace("_", " ").title()
                factors.append({
                    "raw_feature": feat,
                    "label": label,
                    "shap_value": round(abs(val), 4),
                    "direction": "up" if val > 0 else "down",
                })

            return factors
        except Exception:
            return None
