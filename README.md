# ChurnGuard — Customer Churn Intelligence Platform

A web-based analytics platform for predicting and analyzing customer churn in the telecommunications industry. Built with Flask and scikit-learn, it provides an interactive dashboard, a churn prediction tool, a live model comparison page, and a data explorer — enabling data-driven customer retention decisions.

**Business question:** Which customers are likely to leave, and what should the company do to retain them?

---

## Key Features

- **Analytics Dashboard** — KPI cards and interactive charts visualizing churn patterns by contract type, internet service, tenure, and payment method
- **Churn Prediction** — Form-based prediction tool using a Random Forest Classifier with real-time confidence scoring, risk assessment, and **SHAP-powered individual explanations**
- **Model Comparison** — Live side-by-side evaluation of Logistic Regression, Decision Tree, and Random Forest with metrics table, grouped bar chart, confusion matrices, and selection rationale
- **Data Explorer** — Browse, filter, sort, and paginate through 7,000+ customer records with CSV export
- **Feature Importance** — Visual breakdown of the top factors driving customer churn
- **SHAP Explanations** — Per-prediction explanation showing which features pushed toward churn and which toward retention, with directional bar chart
- **SQL Analysis Layer** — 5 SQL scripts (25+ queries) covering customer segmentation, churn rate analysis, revenue impact, retention targeting, and advanced window functions
- **Input Validation** — Server-side validation with meaningful error messages for all prediction inputs
- **Responsive Design** — Mobile-friendly layout with collapsible sidebar navigation
- **Modular Architecture** — Clean separation of ML model, data service, routes, and templates

---

## Tech Stack

| Layer           | Technology                                                                 |
| --------------- | -------------------------------------------------------------------------- |
| Backend         | Python, Flask                                                              |
| ML Models       | scikit-learn (Logistic Regression, Decision Tree, Random Forest)           |
| Explainability  | SHAP (SHapley Additive exPlanations) — per-prediction factor analysis      |
| Data Processing | pandas, NumPy                                                              |
| Statistics      | scipy                                                                      |
| SQL Analysis    | SQLite / standard SQL (6 scripts, 30+ business queries)                    |
| BI Dashboard    | Power BI (4-page report — Executive, Churn Drivers, Risk, Retention)        |
| Frontend        | HTML5, CSS3 (custom design system), JavaScript                             |
| Charts          | Chart.js                                                                   |
| Configuration   | python-dotenv                                                              |

---

## Project Architecture

```
ChurnGuard/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Environment-based configuration
│   ├── routes.py            # Route handlers & API endpoints
│   ├── ml_model.py          # ML model wrapper — prediction, SHAP & comparison
│   ├── data_service.py      # Dataset analytics & filtering
│   ├── static/
│   │   ├── css/style.css    # Custom CSS design system
│   │   └── js/main.js       # Chart rendering & UI interaction
│   └── templates/
│       ├── base.html        # Base layout with navigation
│       ├── dashboard.html   # Analytics dashboard
│       ├── predict.html     # Churn prediction form + SHAP explanation panel
│       ├── models.html      # Model comparison page
│       └── explorer.html    # Data explorer with filters
├── data/
│   └── telco_churn.csv      # IBM Telco Customer Churn dataset
├── model/
│   ├── train_model.py       # Trains LR, DT & RF — outputs pkl, metrics JSON & SHAP
│   ├── churn_model.pkl      # Trained Random Forest (production model)
│   ├── model_metrics.json   # Evaluation metrics for all three models
│   └── shap_explainer.pkl   # SHAP TreeExplainer for live prediction explanations
├── sql/
│   ├── 01_customer_analysis.sql   # Demographics & segmentation
│   ├── 02_churn_analysis.sql      # Churn rate by all dimensions
│   ├── 03_revenue_analysis.sql    # Revenue impact & ARPU
│   ├── 04_customer_segments.sql   # Customer tiers: Loyal / High-Risk / High-Value
│   ├── 05_retention_analysis.sql  # Intervention targeting queries
│   └── 06_advanced_queries.sql    # CTEs, window functions, cohort analysis
├── powerbi/
│   ├── prepare_data.py            # Exports 10 CSVs for Power BI data sources
│   ├── README.md                  # 4-page dashboard spec, DAX measures, build guide
│   └── data/                      # Auto-generated CSV exports (git-ignored)
├── notebooks/
│   └── churn_analysis.ipynb # EDA, feature engineering, and experimentation
├── insights.md              # Business insights & recommendations (structured)
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── .gitignore
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/rakesh4407/customer-churn-prediction-retention-analytics.git
cd customer-churn-prediction-retention-analytics

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

---

## Environment Variables

| Variable      | Description                | Default                 |
| ------------- | -------------------------- | ----------------------- |
| `FLASK_DEBUG` | Enable debug mode          | `false`                 |
| `SECRET_KEY`  | Flask session secret key   | `dev-secret-key-...`    |
| `MODEL_PATH`  | Path to trained model file | `model/churn_model.pkl` |
| `DATA_PATH`   | Path to dataset CSV        | `data/telco_churn.csv`  |

---

## Usage

```bash
# Retrain all three models and regenerate model_metrics.json (optional — pre-trained artifacts included)
python model/train_model.py

# Run the application
python run.py

# Open in browser
# http://127.0.0.1:5000
```

---

## Dataset

IBM Telco Customer Churn dataset — 7,043 customer records with 21 attributes including demographics, services subscribed, account information, and churn status.

**Target variable:** `Churn` (Yes/No) — imbalanced at roughly **26.5% churn rate** (1,869 churners / 5,174 retained).

Explore the raw data at [`data/telco_churn.csv`](data/telco_churn.csv) or interactively via the Data Explorer page.

---

## Methodology

### 1. Data Cleaning

- Handled blank values in `TotalCharges` (stored as empty strings for new customers with `tenure = 0`) — converted to numeric, filled missing as `0`
- Dropped `customerID` — not predictive
- Mapped `SeniorCitizen` integer flag (0/1) to "No"/"Yes" for consistent one-hot encoding

### 2. Exploratory Data Analysis

Key findings from [`notebooks/churn_analysis.ipynb`](notebooks/churn_analysis.ipynb):

- **Contract type** is the strongest single churn driver: month-to-month customers churn at ~43% vs. ~11% for one-year and ~3% for two-year contracts
- **Tenure** is strongly inversely correlated with churn — the first 12 months carry the highest risk
- **Fiber optic internet** customers churn more than DSL or no-internet customers, likely due to cost
- **Electronic check** payers have the highest churn rate among payment methods
- **No tech support / no online security** are among the top service-level churn predictors
- `MonthlyCharges` and `TotalCharges` are right-skewed; churners cluster at higher monthly charges

### 3. Feature Engineering

| Transformation | Rationale |
| --- | --- |
| Tenure → `tenure_group` (12-month bins) | Non-linear relationship with churn; bucketing captures lifecycle stage |
| One-hot encoding for all categorical columns | Required for scikit-learn estimators |
| `StandardScaler` pipeline for Logistic Regression | LR is sensitive to feature scale; RF and DT are not |

Final feature matrix: **51 columns** after encoding (from 20 raw features).

### 4. Models Trained

| Model                | Purpose                                               |
| -------------------- | ----------------------------------------------------- |
| Logistic Regression  | Interpretable baseline; `class_weight='balanced'`     |
| Decision Tree        | Non-linear interpretable baseline; depth-limited      |
| Random Forest        | Production model — ensemble robustness and best AUC   |

### 5. Model Evaluation

All metrics below are on the held-out test set (1,409 customers, 80/20 stratified split, `random_state=42`).

| Metric        | Logistic Regression | Decision Tree | Random Forest  |
| ------------- | ------------------- | ------------- | -------------- |
| **Accuracy**  | 73.31%              | 72.68%        | **79.84%** ★   |
| **Precision** | 49.83%              | 49.05%        | **65.52%** ★   |
| **Recall**    | **78.07%** ★        | 75.67%        | 50.80%         |
| **F1 Score**  | **60.83%** ★        | 59.52%        | 57.23%         |
| **ROC-AUC**   | 83.58%              | 80.33%        | **83.78%** ★   |

★ = best in class for that metric

**Confusion matrices (test set, n=1,409):**

| | LR (TN/FP/FN/TP) | DT (TN/FP/FN/TP) | RF (TN/FP/FN/TP) |
| --------------- | ---------------- | ---------------- | ---------------- |
| Correctly retained (TN) | 741 | 741 | **935** |
| False alarms (FP) | 294 | 294 | **100** |
| Missed churners (FN) | **82** | 91 | 184 |
| Caught churners (TP) | **292** | 283 | 190 |

**Why recall matters here:** Missing an actual churner (false negative) means losing that customer's lifetime value. Flagging a loyal customer as at-risk only costs a cheap retention offer. With a 26.5% churn rate, raw accuracy is deceptive — a classifier that always predicts "No Churn" scores 73.5% accuracy while catching zero churners.

**Production model chosen: Random Forest** — because it achieves the highest ROC-AUC (83.78%) and precision (65.52%), minimizing wasted retention spend on customers who would not have churned anyway. When the retention budget is constrained, targeting efficiency matters more than raw recall.

**Alternative: Logistic Regression** — when the goal is to maximize the number of churners caught (e.g., broad low-cost outreach campaigns), LR's 78.07% recall substantially outperforms Random Forest's 50.80% and should be preferred. The right model depends on the cost structure of the retention programme — not just the accuracy number.

See the live comparison at `/models` in the running application.


### 6. Feature Importance (Random Forest)

Top 10 features ranked by Gini importance:

| Rank | Feature                       | Importance |
| ---- | ----------------------------- | ---------- |
| 1    | TotalCharges                  | 12.63%     |
| 2    | Contract: Month-to-month      | 10.22%     |
| 3    | MonthlyCharges                | 8.60%      |
| 4    | Tenure group: 1–12 months     | 6.64%      |
| 5    | OnlineSecurity: No            | 6.30%      |
| 6    | TechSupport: No               | 5.90%      |
| 7    | InternetService: Fiber optic  | 5.58%      |
| 8    | PaymentMethod: Electronic check | 5.45%    |
| 9    | Contract: Two year            | 3.24%      |
| 10   | InternetService: DSL          | 1.97%      |

---

## Business Recommendations

Translating model findings into retention strategy:

1. **Target month-to-month customers early.**
   Month-to-month contracts are the #2 churn driver. Offer incentives (discount, loyalty pricing, free upgrade) to convert them to annual contracts before month 12 — the highest-risk tenure window.

2. **Bundle tech support and online security.**
   Features 5 and 6 in the importance ranking. Customers without these add-ons churn significantly more. Consider offering a 3-month free trial to high-risk segments identified by the model.

3. **Prioritize new customers (0–12 months tenure).**
   Tenure group 1–12 is the 4th most important feature. Implement a structured onboarding programme: proactive check-ins at months 1, 3, and 6 to address dissatisfaction before it becomes churn.

4. **Investigate fiber optic pricing.**
   Fiber optic internet is the 7th most important churn predictor. High monthly charges + fiber optic is a high-risk combination. Targeted price reviews or retention offers for this segment are warranted.

5. **Flag electronic check payers for outreach.**
   Electronic check payment correlates with higher churn (8th feature). Proactively encouraging customers to switch to automatic payment methods can increase stickiness.

6. **Operationalize the prediction tool.**
   Use `/predict` to score the active customer base monthly. Route customers flagged as High Risk (>= 70% churn probability) to the retention team with a prioritized call list.

---

## Business Intelligence Dashboard (Power BI)

A 4-page Power BI report is documented in [`powerbi/README.md`](powerbi/README.md).
Data exports for all pages are generated by running:

```bash
python powerbi/prepare_data.py
```

This produces 10 pre-aggregated CSV files in `powerbi/data/` ready to load into Power BI Desktop.

| Page | Content |
|---|---|
| **Page 1 — Executive Overview** | KPI cards: total customers, churn rate (26.54%), retention rate, monthly revenue lost (~$139K), annual revenue at risk (~$1.67M) |
| **Page 2 — Churn Drivers** | Churn rate by contract, tenure segment, payment method, internet service, and tech support availability |
| **Page 3 — Customer Risk** | Risk score ranking table, High/Medium/Low distribution, LTV at risk, sliceable by contract and segment |
| **Page 4 — Retention Strategy** | 1,714 high-risk retained customers prioritized by LTV with recommended action per customer |

See [`powerbi/README.md`](powerbi/README.md) for DAX measures, visual specifications, color theme, and step-by-step build instructions.

---

## Future Improvements

- Batch prediction via CSV file upload
- User authentication and role-based access
- Customer segmentation using clustering algorithms (K-Means on churn risk + tenure + spend)
- REST API with Swagger documentation for external integrations
- Hyperparameter tuning with cross-validated GridSearch for all three models
- Global SHAP summary (beeswarm plot) in the analytics dashboard
- Publish Power BI report to Power BI Service for shared stakeholder access

---

Built by **Rakesh** | BCA — Artificial Intelligence & Data Science
