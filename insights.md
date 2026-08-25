# ChurnGuard — Business Insights & Recommendations

Detailed analysis findings from the IBM Telco Customer Churn dataset (7,043 customers).
These insights combine EDA, SQL analysis, and model output (Random Forest + SHAP) to translate
patterns into concrete business decisions.

> Model used for prediction: **Random Forest Classifier** (ROC-AUC: 83.78%, Precision: 65.52%)
> Alternative for high-recall needs: **Logistic Regression** (Recall: 78.07%)

---

## Section 1 — Contract Type

### Business Insight 1: Month-to-month customers churn at nearly 4x the rate of annual customers.

| Contract Type | Churn Rate |
|---|---|
| Month-to-month | ~43% |
| One year | ~11% |
| Two year | ~3% |

Month-to-month customers represent the single highest-risk segment and account for the largest share of monthly revenue loss. A customer on a month-to-month plan can leave at any time with zero penalty — this structural flexibility is the most significant business risk.

**Recommendation:** Introduce a targeted contract-upgrade programme for month-to-month customers within their first 6 months. Incentives can include a 10–15% discount on annual plans, a loyalty credit, or a free service add-on. The programme should be triggered automatically when a customer reaches month 3 without upgrading.

---

### Business Insight 2: Locking in month-to-month customers with annual contracts is the single highest-ROI retention lever.

Converting just 10% of month-to-month churners to one-year contracts would meaningfully reduce the overall churn rate and extend customer lifetime value by an average of 12+ months.

**Recommendation:** Equip the retention team with model scores (from `/predict`) to prioritize outreach. Focus contract-upgrade conversations on customers with ≥60% predicted churn probability who are still on month-to-month plans.

---

## Section 2 — Tenure & Onboarding

### Business Insight 3: Churn risk is highest in the first 12 months — after that, customers become significantly more loyal.

Tenure group 1–12 months is the 4th most important feature in the Random Forest model. The data shows a sharp drop in churn rate after the 12-month mark, consistent with a critical "settling in" period.

**Recommendation:** Implement a structured onboarding programme:
- **Month 1:** Welcome call + feature walkthrough
- **Month 3:** Usage check-in + satisfaction survey
- **Month 6:** Proactive value review — offer a loyalty discount or add-on trial if the customer hasn't yet upgraded
- **Month 12:** Contract upgrade conversation

Reducing first-year churn by even 5 percentage points would retain hundreds of additional customers annually.

---

### Business Insight 4: Long-tenure customers (48+ months) have a churn rate below 5% and represent the most stable revenue base.

These customers almost exclusively hold one-year or two-year contracts and are significantly more likely to have tech support and security add-ons.

**Recommendation:** Use the loyal customer profile as a target persona for new customer onboarding. Understand what services and touchpoints converted them into loyal customers — and replicate that journey for new cohorts.

---

## Section 3 — Service Add-ons

### Business Insight 5: Customers without tech support are approximately 2x more likely to churn than those with it.

Tech Support is the 6th most important feature. Customers who lack support when they encounter problems are far more likely to switch providers.

**Recommendation:** Offer a 3-month free trial of tech support to all new customers and high-risk segments (month-to-month, first year). The trial converts a key churn predictor into a retention anchor — and many customers will retain the add-on after the trial ends.

---

### Business Insight 6: Customers without online security have a substantially higher churn rate.

Online Security is the 5th most important feature in the model. Customers who feel their data is unprotected are less likely to stay long-term.

**Recommendation:** Bundle online security into the standard new customer package for the first 6 months. Frame it as a value-add during onboarding rather than an upsell — this reduces the perception of cost while addressing a key churn driver.

---

## Section 4 — Internet Service

### Business Insight 7: Fiber optic customers churn more than DSL customers, despite paying significantly more per month.

Fiber optic internet is the 7th most important churn predictor. These customers have higher monthly charges and may be reacting to a cost-to-value mismatch — especially if they experience service quality issues.

**Recommendation:** Conduct a targeted satisfaction survey for fiber optic customers who:
1. Are on month-to-month contracts
2. Have been customers for less than 24 months
3. Do not have tech support

This 3-way overlap represents the highest-risk fiber optic segment. Proactive service quality improvements and pricing reviews for this group could significantly reduce churn.

---

## Section 5 — Payment Method

### Business Insight 8: Electronic check payers have the highest churn rate among all payment methods.

Payment Method is the 8th most important feature. Electronic check customers appear less "locked in" — the payment method requires active re-authorization each billing cycle, unlike automatic bank transfer or credit card payments.

**Recommendation:** Run a campaign to encourage electronic check payers to switch to automatic payment. Incentivize the switch with a small discount or billing credit. Customers on automatic payment have measurably lower churn and longer tenures.

---

## Section 6 — Revenue at Risk

### Business Insight 9: Churned customers generate significantly higher monthly charges than retained customers on average.

The model shows that churners cluster in higher monthly charge brackets — they are often fiber optic + multiple service subscribers paying $70–$100/month who leave before realizing their full lifetime value.

**Recommendation:** Model the expected 2-year lifetime value (LTV) for at-risk customers and use that figure — not just churn probability — to size retention offers. A customer paying $90/month has a 2-year LTV of $2,160. A $50 retention voucher is a strong economic decision if it prevents churn.

---

## Section 7 — Model Selection Rationale

### Business Insight 10: Model choice should be driven by the business cost of each error type — not raw accuracy.

| Model | Accuracy | Recall | ROC-AUC | Best For |
|---|---|---|---|---|
| Logistic Regression | 73.31% | **78.07%** | 83.58% | Maximum churn detection; unlimited retention budget |
| Decision Tree | 72.68% | 75.67% | 80.33% | Explainable decisions; stakeholder walkthroughs |
| **Random Forest** | **79.84%** | 50.80% | **83.78%** | **Precision targeting; limited retention budget** |

**Production model chosen: Random Forest** — because it achieves the best ROC-AUC (83.78%) and highest precision (65.52%), minimizing wasted retention spend on customers who would not have churned anyway. When the retention budget is constrained, targeting efficiency matters more than raw recall.

**Alternative: Logistic Regression** — when the business goal is to maximize the number of churners caught (e.g., broad retention campaigns, low-cost outreach), LR's 78.07% recall outperforms Random Forest's 50.80% and should be used instead.

> This distinction — selecting a model based on the cost of false negatives vs. false positives rather than accuracy — is the difference between a data project and a data-driven business decision.

---

## Section 8 — SHAP Individual Explanations

The model includes SHAP (SHapley Additive exPlanations) to explain **why** any individual customer received their churn probability score. This turns the prediction from a black-box number into an actionable explanation.

**Example: High-Risk Customer**

```
Predicted churn probability: 82%
Risk Level: HIGH

Main factors driving risk UP (toward churn):
  [+] Contract = Month-to-month       +0.31 SHAP
  [+] MonthlyCharges = $94.25         +0.18 SHAP
  [+] TechSupport = No                +0.14 SHAP
  [+] tenure_group = 1-12 months      +0.12 SHAP

Main factors driving risk DOWN (toward retention):
  [-] InternetService = Fiber optic    -0.04 SHAP (minor stabilizer)

Recommended action: Priority retention campaign
  -> Offer annual contract upgrade with discount
  -> Include 3-month tech support trial
```

**Example: Low-Risk Customer**

```
Predicted churn probability: 12%
Risk Level: LOW

Main factors driving risk DOWN (toward retention):
  [-] Contract = Two year             -0.28 SHAP
  [-] tenure_group = 49-72 months     -0.22 SHAP
  [-] TechSupport = Yes               -0.11 SHAP

Recommended action: Standard loyalty touchpoint only
```

SHAP explanations are shown live in the `/predict` page for every prediction made.
