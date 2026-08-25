"""
Power BI Data Preparation Script for ChurnGuard
================================================
Exports pre-aggregated tables from telco_churn.csv into CSV files
that can be loaded directly into Power BI as data sources.

Outputs (written to powerbi/data/):
  customers_base.csv         -- Full cleaned dataset for row-level tables
  kpi_summary.csv            -- Executive KPIs (Page 1)
  churn_by_contract.csv      -- Churn Drivers: by contract (Page 2)
  churn_by_tenure.csv        -- Churn Drivers: by tenure group (Page 2)
  churn_by_payment.csv       -- Churn Drivers: by payment method (Page 2)
  churn_by_internet.csv      -- Churn Drivers: by internet service (Page 2)
  churn_by_techsupport.csv   -- Churn Drivers: by tech support (Page 2)
  customer_risk_table.csv    -- Customer Risk table with risk scores (Page 3)
  retention_targets.csv      -- High-risk high-value customers (Page 4)

Usage:
    python powerbi/prepare_data.py
"""

import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH    = os.path.join(PROJECT_ROOT, "data", "telco_churn.csv")
OUT_DIR      = os.path.join(PROJECT_ROOT, "powerbi", "data")

os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Load & clean
# ---------------------------------------------------------------------------

def load_data():
    df = pd.read_csv(DATA_PATH)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    df["Churned"] = (df["Churn"] == "Yes").astype(int)
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

    # Tenure segment
    def tenure_seg(t):
        if t <= 12:   return "1-12 mo (New)"
        if t <= 24:   return "13-24 mo (Growing)"
        if t <= 48:   return "25-48 mo (Established)"
        return "49-72 mo (Loyal)"

    df["TenureSegment"] = df["tenure"].apply(tenure_seg)

    # Risk score (simple rule-based; SHAP-based scoring uses the ML model)
    def risk_score(row):
        score = 0
        if row["Contract"] == "Month-to-month": score += 3
        if row["tenure"] <= 12:                 score += 2
        if row["TechSupport"] == "No":          score += 1
        if row["OnlineSecurity"] == "No":       score += 1
        if row["PaymentMethod"] == "Electronic check": score += 1
        return score

    df["RiskScore"] = df.apply(risk_score, axis=1)
    df["RiskLevel"] = df["RiskScore"].apply(
        lambda s: "High" if s >= 5 else ("Medium" if s >= 3 else "Low")
    )

    # Estimated 2-year LTV
    df["EstLTV_2yr"] = (df["MonthlyCharges"] * 24).round(2)

    return df


# ---------------------------------------------------------------------------
# Export tables
# ---------------------------------------------------------------------------

def export_all(df):

    # 1. Full base table (for row-level visuals & slicers)
    base_cols = [
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
        "tenure", "TenureSegment", "PhoneService", "MultipleLines",
        "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
        "Contract", "PaperlessBilling", "PaymentMethod",
        "MonthlyCharges", "TotalCharges", "Churn", "Churned",
        "RiskScore", "RiskLevel", "EstLTV_2yr"
    ]
    df[base_cols].to_csv(os.path.join(OUT_DIR, "customers_base.csv"), index=False)
    print("  [OK] customers_base.csv")

    # 2. Executive KPIs
    total      = len(df)
    churned    = df["Churned"].sum()
    retained   = total - churned
    churn_rate = round(100 * churned / total, 2)
    kpi = pd.DataFrame([{
        "TotalCustomers":   total,
        "ChurnedCustomers": churned,
        "RetainedCustomers": retained,
        "ChurnRate_pct":    churn_rate,
        "RetentionRate_pct": round(100 - churn_rate, 2),
        "AvgMonthlyCharges": round(df["MonthlyCharges"].mean(), 2),
        "AvgTenureMonths":   round(df["tenure"].mean(), 1),
        "MonthlyRevenueLost": round(df[df["Churned"]==1]["MonthlyCharges"].sum(), 2),
        "AnnualRevenueLost":  round(df[df["Churned"]==1]["MonthlyCharges"].sum() * 12, 2),
    }])
    kpi.to_csv(os.path.join(OUT_DIR, "kpi_summary.csv"), index=False)
    print("  [OK] kpi_summary.csv")

    # 3. Churn Drivers
    def churn_by(col):
        g = df.groupby(col).agg(
            TotalCustomers=("Churned", "count"),
            ChurnedCustomers=("Churned", "sum"),
            AvgMonthlyCharges=("MonthlyCharges", "mean"),
        ).reset_index()
        g["ChurnRate_pct"] = (g["ChurnedCustomers"] / g["TotalCustomers"] * 100).round(2)
        g["AvgMonthlyCharges"] = g["AvgMonthlyCharges"].round(2)
        return g

    churn_by("Contract").to_csv(os.path.join(OUT_DIR, "churn_by_contract.csv"), index=False)
    churn_by("TenureSegment").to_csv(os.path.join(OUT_DIR, "churn_by_tenure.csv"), index=False)
    churn_by("PaymentMethod").to_csv(os.path.join(OUT_DIR, "churn_by_payment.csv"), index=False)
    churn_by("InternetService").to_csv(os.path.join(OUT_DIR, "churn_by_internet.csv"), index=False)
    churn_by("TechSupport").to_csv(os.path.join(OUT_DIR, "churn_by_techsupport.csv"), index=False)
    print("  [OK] churn_by_*.csv (5 files)")

    # 4. Customer risk table (Page 3 — filtered to active customers / sorted by risk)
    risk_cols = [
        "customerID", "Contract", "tenure", "TenureSegment",
        "MonthlyCharges", "TotalCharges", "EstLTV_2yr",
        "InternetService", "TechSupport", "OnlineSecurity",
        "PaymentMethod", "RiskScore", "RiskLevel", "Churn"
    ]
    risk_df = df[risk_cols].sort_values(["RiskScore", "MonthlyCharges"], ascending=[False, False])
    risk_df.to_csv(os.path.join(OUT_DIR, "customer_risk_table.csv"), index=False)
    print("  [OK] customer_risk_table.csv")

    # 5. Retention targets — high-risk, high-value, currently retained
    retention = df[
        (df["Churn"] == "No") &
        (df["RiskLevel"] == "High")
    ].sort_values("EstLTV_2yr", ascending=False)[risk_cols]
    retention["RecommendedAction"] = retention.apply(lambda r: (
        "Offer annual contract upgrade + tech support trial"
        if r["Contract"] == "Month-to-month" and r["TechSupport"] == "No"
        else "Priority retention call + loyalty discount"
        if r["Contract"] == "Month-to-month"
        else "Service quality review + outreach"
    ), axis=1)
    retention.to_csv(os.path.join(OUT_DIR, "retention_targets.csv"), index=False)
    print("  [OK] retention_targets.csv")

    print(f"\nAll exports written to: {OUT_DIR}")
    print(f"  Total customers: {total}")
    print(f"  Churn rate:      {churn_rate}%")
    print(f"  Retention targets (high-risk, retained): {len(retention)}")


if __name__ == "__main__":
    print("Loading dataset...")
    df = load_data()
    print(f"  Shape: {df.shape}\n")
    print("Exporting Power BI tables...")
    export_all(df)
    print("\nDone. Load the CSV files in powerbi/data/ into Power BI Desktop.")
