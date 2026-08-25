# ChurnGuard — Customer Churn Intelligence Platform

A web-based analytics platform for predicting and analyzing customer churn in the telecommunications industry. Built with Flask and scikit-learn, it provides an interactive dashboard, a churn prediction tool, a live model comparison page, and a data explorer — enabling data-driven customer retention decisions.

**Business question:** Which customers are likely to leave, and what should the company do to retain them?

---

## Key Features

- **Analytics Dashboard** — KPI cards and interactive charts visualizing churn patterns by contract type, internet service, tenure, and payment method
- **Churn Prediction** — Form-based prediction tool using a Random Forest Classifier with real-time confidence scoring and risk assessment
- **Model Comparison** — Live side-by-side evaluation of Logistic Regression, Decision Tree, and Random Forest with metrics table, grouped bar chart, confusion matrices, and selection rationale
- **Data Explorer** — Browse, filter, sort, and paginate through 7,000+ customer records with CSV export
- **Feature Importance** — Visual breakdown of the top factors driving customer churn
- **Input Validation** — Server-side validation with meaningful error messages for all prediction inputs
- **Responsive Design** — Mobile-friendly layout with collapsible sidebar navigation
- **Modular Architecture** — Clean separation of ML model, data service, routes, and templates

---

## Tech Stack

| Layer           | Technology                                                                 |
| --------------- | -------------------------------------------------------------------------- |
| Backend         | Python, Flask                                                              |
| ML Models       | scikit-learn (Logistic Regression, Decision Tree, Random Forest)           |
| Data Processing | pandas, NumPy                                                              |
| Statistics      | scipy                                                                      |
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
│   ├── ml_model.py          # ML model wrapper with validation & comparison
│   ├── data_service.py      # Dataset analytics & filtering
│   ├── static/
│   │   ├── css/style.css    # Custom CSS design system
│   │   └── js/main.js       # Chart rendering & UI interaction
│   └── templates/
│       ├── base.html        # Base layout with navigation
│       ├── dashboard.html   # Analytics dashboard
│       ├── predict.html     # Churn prediction form
│       ├── models.html      # Model comparison page
│       └── explorer.html    # Data explorer with filters
├── data/
│   └── telco_churn.csv      # IBM Telco Customer Churn dataset
├── model/
│   ├── train_model.py       # Trains LR, DT & RF — outputs .pkl + metrics JSON
│   ├── churn_model.pkl      # Trained Random Forest (production model)
│   └── model_metrics.json   # Evaluation metrics for all three models
├── notebooks/
│   └── churn_analysis.ipynb # EDA, feature engineering, and experimentation
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

|                 | LR (TN/FP/FN/TP) | DT (TN/FP/FN/TP) | RF (TN/FP/FN/TP) |
| --------------- | ---------------- | ---------------- | ---------------- |
| Correctly retained (TN) | 741 | 741 | **935** |
| False alarms (FP)       | 294 | 294 | **100** |
| Missed churners (FN)    | **82** | 91 | 184 |
| Caught churners (TP)    | **292** | 283 | 190 |

**Why recall matters here:** Missing an actual churner (false negative) means losing that customer's lifetime value. Flagging a loyal customer as at-risk only costs a cheap retention offer. With a 26.5% churn rate, raw accuracy is deceptive — a classifier that always predicts "No Churn" scores 73.5% accuracy while catching zero churners. Logistic Regression catches the most churners (78.1% recall); Random Forest is the most precise and has the best ROC-AUC, making it the best choice when the retention budget is limited and targeting efficiency matters.

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
   Use `/predict` to score the active customer base monthly. Route customers flagged as High Risk (≥ 70% churn probability) to the retention team with a prioritized call list.

---

## Future Improvements

- Batch prediction via CSV file upload
- User authentication and role-based access
- Customer segmentation using clustering algorithms (K-Means on churn risk + tenure + spend)
- REST API with Swagger documentation for external integrations
- Hyperparameter tuning with cross-validated GridSearch for all three models
- Power BI report for stakeholder-facing analytics (connect to the same `telco_churn.csv`)

---

Built by **Rakesh** | BCA — Artificial Intelligence & Data Science