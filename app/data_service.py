"""
Data service for ChurnGuard.
Provides analytics, filtering, and export functionality for the dataset.
"""

import pandas as pd
import numpy as np


class DataService:
    """Service layer for dataset operations and analytics."""

    def __init__(self, data_path):
        """Load and prepare the dataset."""
        self.df = pd.read_csv(data_path)
        self._prepare_data()

    def _prepare_data(self):
        """Clean and prepare the dataset for analytics."""
        # Convert TotalCharges to numeric
        self.df["TotalCharges"] = pd.to_numeric(
            self.df["TotalCharges"], errors="coerce"
        )
        self.df["TotalCharges"] = self.df["TotalCharges"].fillna(0)

        # Create tenure groups for analysis
        labels = [f"{i}-{i + 11}" for i in range(1, 72, 12)]
        self.df["tenure_group"] = pd.cut(
            self.df["tenure"].astype(int),
            bins=range(1, 80, 12),
            right=False,
            labels=labels,
        )

    def get_summary_stats(self):
        """Return key performance indicators for the dashboard."""
        total = len(self.df)
        churned = len(self.df[self.df["Churn"] == "Yes"])
        churn_rate = (churned / total * 100) if total > 0 else 0

        return {
            "total_customers": total,
            "churned_customers": churned,
            "retained_customers": total - churned,
            "churn_rate": round(churn_rate, 1),
            "avg_monthly_charges": round(self.df["MonthlyCharges"].mean(), 2),
            "avg_tenure": round(self.df["tenure"].mean(), 1),
            "avg_total_charges": round(self.df["TotalCharges"].mean(), 2),
            "senior_pct": round(
                self.df["SeniorCitizen"].mean() * 100, 1
            ),
        }

    def get_churn_by_column(self, column):
        """Get churn rate grouped by a categorical column."""
        if column not in self.df.columns:
            return []

        grouped = self.df.groupby(column, observed=False)["Churn"].apply(
            lambda x: (x == "Yes").sum() / len(x) * 100
        ).round(1)

        return {
            "labels": [str(label) for label in grouped.index.tolist()],
            "values": grouped.values.tolist(),
        }

    def get_churn_distribution(self):
        """Get overall churn distribution."""
        counts = self.df["Churn"].value_counts()
        return {
            "labels": counts.index.tolist(),
            "values": counts.values.tolist(),
        }

    def get_monthly_charges_distribution(self):
        """Get monthly charges distribution by churn status."""
        churned = self.df[self.df["Churn"] == "Yes"]["MonthlyCharges"]
        retained = self.df[self.df["Churn"] == "No"]["MonthlyCharges"]

        # Create histogram bins
        bins = list(range(0, 125, 10))
        churned_hist = np.histogram(churned, bins=bins)[0].tolist()
        retained_hist = np.histogram(retained, bins=bins)[0].tolist()

        bin_labels = [f"${b}-{b + 10}" for b in bins[:-1]]

        return {
            "labels": bin_labels,
            "churned": churned_hist,
            "retained": retained_hist,
        }

    def get_filtered_data(self, filters=None, page=1, per_page=25, sort_by=None, sort_order="asc"):
        """Get paginated, filtered customer data for the explorer."""
        filtered = self.df.copy()

        if filters:
            for col, value in filters.items():
                if value and col in filtered.columns:
                    filtered = filtered[filtered[col] == value]

        # Sort
        if sort_by and sort_by in filtered.columns:
            ascending = sort_order != "desc"
            filtered = filtered.sort_values(by=sort_by, ascending=ascending)

        total_records = len(filtered)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        end = start + per_page
        page_data = filtered.iloc[start:end]

        # Select display columns
        display_cols = [
            "customerID", "gender", "SeniorCitizen", "Partner",
            "tenure", "Contract", "MonthlyCharges", "TotalCharges",
            "InternetService", "Churn",
        ]
        display_cols = [c for c in display_cols if c in page_data.columns]

        return {
            "records": page_data[display_cols].to_dict(orient="records"),
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
        }

    def get_filter_options(self):
        """Get unique values for filter dropdowns."""
        filter_cols = ["gender", "Contract", "InternetService", "Churn",
                       "PaymentMethod", "Partner", "Dependents"]
        options = {}
        for col in filter_cols:
            if col in self.df.columns:
                options[col] = sorted(self.df[col].dropna().unique().tolist())
        return options

    def export_csv(self, filters=None):
        """Export filtered data as CSV string."""
        filtered = self.df.copy()

        if filters:
            for col, value in filters.items():
                if value and col in filtered.columns:
                    filtered = filtered[filtered[col] == value]

        return filtered.to_csv(index=False)
