-- ============================================================
-- 03_revenue_analysis.sql
-- Revenue impact analysis — quantifying the cost of churn
-- Dataset: IBM Telco Customer Churn (7,043 records)
-- ============================================================

-- 1. Total revenue lost to churn
SELECT
    Churn,
    COUNT(*) AS customer_count,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(SUM(TotalCharges), 2) AS total_lifetime_revenue,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_lifetime_revenue
FROM customers
GROUP BY Churn;

-- 2. Monthly revenue at risk — customers who churned
SELECT
    ROUND(SUM(MonthlyCharges), 2) AS monthly_revenue_lost,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_per_churner,
    COUNT(*) AS churned_customers
FROM customers
WHERE Churn = 'Yes';

-- 3. Revenue segmentation by monthly charges tier
SELECT
    CASE
        WHEN MonthlyCharges < 30 THEN 'Low ($0-29)'
        WHEN MonthlyCharges BETWEEN 30 AND 60 THEN 'Medium ($30-60)'
        WHEN MonthlyCharges BETWEEN 61 AND 90 THEN 'High ($61-90)'
        ELSE 'Premium ($90+)'
    END AS charge_tier,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_at_risk
FROM customers
GROUP BY charge_tier
ORDER BY MIN(MonthlyCharges);

-- 4. Average revenue per user (ARPU) — churned vs. retained
SELECT
    Churn,
    ROUND(AVG(MonthlyCharges), 2) AS arpu_monthly,
    ROUND(AVG(TotalCharges / NULLIF(tenure, 0)), 2) AS arpu_per_month_of_tenure,
    ROUND(AVG(TotalCharges), 2) AS avg_customer_lifetime_value
FROM customers
GROUP BY Churn;

-- 5. Revenue impact by contract type
SELECT
    Contract,
    Churn,
    COUNT(*) AS customer_count,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(SUM(TotalCharges), 2) AS total_revenue
FROM customers
GROUP BY Contract, Churn
ORDER BY Contract, Churn;

-- 6. Top 10 highest-value customers who churned
SELECT
    customerID,
    Contract,
    tenure,
    MonthlyCharges,
    TotalCharges,
    InternetService,
    PaymentMethod
FROM customers
WHERE Churn = 'Yes'
ORDER BY TotalCharges DESC
LIMIT 10;

-- 7. Estimated annual revenue at risk from current churn rate
SELECT
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END) * 12, 2) AS estimated_annual_revenue_loss,
    ROUND(SUM(MonthlyCharges) * 12, 2) AS total_annual_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
        / SUM(MonthlyCharges),
        2
    ) AS pct_revenue_at_risk
FROM customers;
