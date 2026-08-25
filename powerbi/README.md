# ChurnGuard — Power BI Business Intelligence Dashboard

A 4-page Power BI report built on top of the IBM Telco Customer Churn dataset.
This dashboard provides executive-level visibility into churn patterns, customer risk scoring,
and data-driven retention targeting.

---

## Data Sources

Run the preparation script first to generate all required CSV tables:

```bash
python powerbi/prepare_data.py
```

This writes 10 CSV files to `powerbi/data/`:

| File | Used on Page | Description |
|---|---|---|
| `customers_base.csv` | All pages (slicer source) | Full cleaned dataset, 7,043 rows, 26 columns |
| `kpi_summary.csv` | Page 1 | Pre-aggregated executive KPIs |
| `churn_by_contract.csv` | Page 2 | Churn rate by contract type |
| `churn_by_tenure.csv` | Page 2 | Churn rate by tenure segment |
| `churn_by_payment.csv` | Page 2 | Churn rate by payment method |
| `churn_by_internet.csv` | Page 2 | Churn rate by internet service |
| `churn_by_techsupport.csv` | Page 2 | Churn rate by tech support availability |
| `customer_risk_table.csv` | Page 3 | All customers ranked by risk score |
| `retention_targets.csv` | Page 4 | High-risk, retained customers with recommended action |

---

## Dashboard Pages

### Page 1 — Executive Overview

**Goal:** Single-screen summary for management stakeholders.

**Visuals:**

| Visual | Type | Data |
|---|---|---|
| Total Customers | KPI Card | `kpi_summary[TotalCustomers]` |
| Churned Customers | KPI Card | `kpi_summary[ChurnedCustomers]` |
| Churn Rate % | KPI Card (red if >25%) | `kpi_summary[ChurnRate_pct]` |
| Retention Rate % | KPI Card (green) | `kpi_summary[RetentionRate_pct]` |
| Avg Monthly Charges | KPI Card | `kpi_summary[AvgMonthlyCharges]` |
| Monthly Revenue Lost to Churn | KPI Card | `kpi_summary[MonthlyRevenueLost]` |
| Annual Revenue at Risk | KPI Card | `kpi_summary[AnnualRevenueLost]` |
| Churn vs. Retained | Donut Chart | `customers_base[Churn]` |
| Monthly Charges Distribution | Histogram | `customers_base[MonthlyCharges]` by `Churn` |

**DAX Measures:**

```dax
ChurnRate = DIVIDE(
    COUNTROWS(FILTER(customers_base, customers_base[Churn] = "Yes")),
    COUNTROWS(customers_base),
    0
) * 100

MonthlyRevenueLost =
    CALCULATE(
        SUM(customers_base[MonthlyCharges]),
        customers_base[Churn] = "Yes"
    )

AnnualRevenueLost = [MonthlyRevenueLost] * 12
```

---

### Page 2 — Churn Drivers

**Goal:** Identify which customer segments have the highest churn risk.

**Visuals:**

| Visual | Type | Data | Key Insight |
|---|---|---|---|
| Churn Rate by Contract | Clustered Bar | `churn_by_contract` | Month-to-month ~43% vs Two-year ~3% |
| Churn Rate by Tenure | Line Chart | `churn_by_tenure` | New customers (1-12 mo) highest risk |
| Churn Rate by Payment Method | Bar Chart | `churn_by_payment` | Electronic check highest churn |
| Churn Rate by Internet Service | Bar Chart | `churn_by_internet` | Fiber optic higher than DSL |
| Churn Rate by Tech Support | Stacked Bar | `churn_by_techsupport` | No tech support = much higher churn |
| Filter: Gender / Senior Citizen | Slicer | `customers_base[gender]`, `[SeniorCitizen]` | Cross-filtering |

**DAX Measures:**

```dax
ChurnRateBySegment = DIVIDE(
    SUM(churn_by_contract[ChurnedCustomers]),
    SUM(churn_by_contract[TotalCustomers]),
    0
) * 100
```

---

### Page 3 — Customer Risk Analysis

**Goal:** Customer-level risk scoring — which active customers are most at risk right now?

**Visuals:**

| Visual | Type | Data |
|---|---|---|
| Risk Level Distribution | Donut Chart | `customer_risk_table[RiskLevel]` |
| High / Medium / Low Count | KPI Cards | Filtered `COUNTROWS` |
| Customer Risk Table | Table Visual | `customer_risk_table` — CustomerID, Contract, Tenure, MonthlyCharges, RiskLevel, EstLTV_2yr |
| Risk Score by Contract | Bar Chart | Avg `RiskScore` grouped by `Contract` |
| Avg Monthly Charges by Risk Level | Bar | `customers_base` grouped by `RiskLevel` |

**Slicers:** Contract type, Tenure Segment, Internet Service

**DAX Measures:**

```dax
HighRiskCount =
    CALCULATE(
        COUNTROWS(customer_risk_table),
        customer_risk_table[RiskLevel] = "High"
    )

AvgRiskScore = AVERAGE(customer_risk_table[RiskScore])

TotalLTVAtRisk =
    CALCULATE(
        SUM(customer_risk_table[EstLTV_2yr]),
        customer_risk_table[RiskLevel] = "High"
    )
```

---

### Page 4 — Retention Strategy

**Goal:** Actionable targeting — show which high-risk, high-value customers to call first.

**Visuals:**

| Visual | Type | Data |
|---|---|---|
| Retention Targets Count | KPI Card | `COUNTROWS(retention_targets)` |
| Revenue at Stake | KPI Card | `SUM(retention_targets[EstLTV_2yr])` |
| Targets by Contract | Bar | `retention_targets[Contract]` |
| Targets by Recommended Action | Bar | `retention_targets[RecommendedAction]` |
| High-Risk Customer Table | Table | CustomerID, Contract, Tenure, MonthlyCharges, RiskLevel, EstLTV_2yr, RecommendedAction |
| Avg Tenure of Targets | KPI Card | `AVERAGE(retention_targets[tenure])` |

**Recommended Action categories (from prep script):**

| Category | Criteria |
|---|---|
| Offer annual contract upgrade + tech support trial | Month-to-month + No TechSupport |
| Priority retention call + loyalty discount | Month-to-month only |
| Service quality review + outreach | Other high-risk |

---

## How to Build in Power BI Desktop

1. Open **Power BI Desktop**
2. **Get Data → Text/CSV** → import all files from `powerbi/data/`
3. Build relationships in the **Model view**:
   - `customers_base[customerID]` → `customer_risk_table[customerID]`
   - `customers_base[customerID]` → `retention_targets[customerID]`
4. Create the 4 pages following the visual/measure specifications above
5. Add a consistent **color theme**:
   - Churn / High Risk: `#ef4444` (red)
   - Retained / Low Risk: `#10b981` (green)
   - Neutral / Medium: `#f59e0b` (amber)
   - Background: `#f4f6f9` (light grey)
6. Apply page-level **slicers** for Contract, Tenure Segment, Gender, Internet Service
7. Publish to Power BI Service (optional — for shared access)

---

## Key Metrics Reference

| Metric | Value |
|---|---|
| Total Customers | 7,043 |
| Churned Customers | 1,869 |
| Churn Rate | 26.54% |
| Retention Rate | 73.46% |
| Avg Monthly Charges | $64.76 |
| Monthly Revenue Lost | ~$139,130 |
| Annual Revenue at Risk | ~$1.67M |
| High-Risk Retained Customers | 1,714 |
