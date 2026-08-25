-- ============================================================
-- 04_retention_analysis.sql
-- Retention strategy targeting — identify at-risk segments
-- Dataset: IBM Telco Customer Churn (7,043 records)
-- ============================================================

-- 1. High-risk profile: Month-to-month + No tech support + First year
SELECT
    COUNT(*) AS high_risk_customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS pct_of_total,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS already_churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
WHERE Contract = 'Month-to-month'
  AND TechSupport = 'No'
  AND tenure <= 12;

-- 2. Retention priority segments — ranked by churn rate and volume
SELECT
    Contract,
    TechSupport,
    OnlineSecurity,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_at_risk
FROM customers
GROUP BY Contract, TechSupport, OnlineSecurity
HAVING COUNT(*) >= 50
ORDER BY churn_rate DESC
LIMIT 10;

-- 3. Customers who are still retained but high-risk (intervention targets)
SELECT
    customerID,
    Contract,
    tenure,
    MonthlyCharges,
    TechSupport,
    OnlineSecurity,
    InternetService,
    PaymentMethod
FROM customers
WHERE Churn = 'No'
  AND Contract = 'Month-to-month'
  AND tenure <= 12
  AND TechSupport = 'No'
ORDER BY MonthlyCharges DESC
LIMIT 20;

-- 4. Impact of tech support on retention — before/after style analysis
SELECT
    TechSupport,
    Contract,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
WHERE InternetService != 'No'
GROUP BY TechSupport, Contract
ORDER BY Contract, churn_rate DESC;

-- 5. Onboarding window analysis — churn risk in first 6 months
SELECT
    tenure,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
WHERE tenure <= 12
GROUP BY tenure
ORDER BY tenure;

-- 6. Long-term loyal customer profile (benchmark for retention)
SELECT
    COUNT(*) AS loyal_customers,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_total_charges,
    SUM(CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END) AS with_tech_support,
    SUM(CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END) AS with_security,
    SUM(CASE WHEN Contract = 'Two year' THEN 1 ELSE 0 END) AS two_year_contracts
FROM customers
WHERE tenure >= 48
  AND Churn = 'No';

-- 7. Payment method upgrade opportunity — electronic check churners still retained
SELECT
    PaymentMethod,
    COUNT(*) AS retained_customers,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
WHERE Churn = 'No'
GROUP BY PaymentMethod
ORDER BY avg_tenure ASC;
