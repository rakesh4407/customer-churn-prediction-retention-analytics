-- ============================================================
-- 05_advanced_queries.sql
-- Advanced SQL: window functions, CTEs, cohort analysis
-- Dataset: IBM Telco Customer Churn (7,043 records)
-- ============================================================

-- 1. CTE: Churn rate by segment with running total of at-risk revenue
WITH segment_stats AS (
    SELECT
        Contract,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
        ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_lost
    FROM customers
    GROUP BY Contract
)
SELECT
    *,
    SUM(monthly_revenue_lost) OVER (ORDER BY churn_rate DESC) AS cumulative_revenue_lost
FROM segment_stats
ORDER BY churn_rate DESC;

-- 2. Window function: rank customers within each contract type by monthly spend
SELECT
    customerID,
    Contract,
    MonthlyCharges,
    Churn,
    RANK() OVER (PARTITION BY Contract ORDER BY MonthlyCharges DESC) AS spend_rank_in_contract,
    ROUND(AVG(MonthlyCharges) OVER (PARTITION BY Contract), 2) AS avg_charges_in_contract,
    MonthlyCharges - AVG(MonthlyCharges) OVER (PARTITION BY Contract) AS deviation_from_avg
FROM customers
ORDER BY Contract, spend_rank_in_contract
LIMIT 30;

-- 3. CTE: High-value churned customers — estimated lifetime value lost
WITH customer_ltv AS (
    SELECT
        customerID,
        Contract,
        InternetService,
        tenure,
        MonthlyCharges,
        TotalCharges,
        Churn,
        ROUND(MonthlyCharges * 24, 2) AS estimated_2yr_value
    FROM customers
    WHERE Churn = 'Yes'
)
SELECT
    customerID,
    Contract,
    InternetService,
    tenure,
    MonthlyCharges,
    TotalCharges,
    estimated_2yr_value,
    RANK() OVER (ORDER BY estimated_2yr_value DESC) AS value_rank
FROM customer_ltv
ORDER BY estimated_2yr_value DESC
LIMIT 15;

-- 4. Cohort-style: Monthly charges percentile and churn correlation
SELECT
    NTILE(4) OVER (ORDER BY MonthlyCharges) AS spend_quartile,
    MIN(MonthlyCharges) AS min_charges,
    MAX(MonthlyCharges) AS max_charges,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY spend_quartile
ORDER BY spend_quartile;

-- 5. CTE: Service bundle analysis — do more services = less churn?
WITH service_score AS (
    SELECT
        customerID,
        Churn,
        MonthlyCharges,
        (CASE WHEN PhoneService = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN MultipleLines = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN InternetService != 'No' THEN 1 ELSE 0 END
         + CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN OnlineBackup = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN DeviceProtection = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN StreamingTV = 'Yes' THEN 1 ELSE 0 END
         + CASE WHEN StreamingMovies = 'Yes' THEN 1 ELSE 0 END) AS services_subscribed
    FROM customers
)
SELECT
    services_subscribed,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM service_score
GROUP BY services_subscribed
ORDER BY services_subscribed;

-- 6. Rolling churn risk: cumulative churn by tenure (survival-style)
SELECT
    tenure,
    COUNT(*) AS customers_at_tenure,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_at_tenure,
    SUM(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)) OVER (ORDER BY tenure) AS cumulative_churned,
    SUM(COUNT(*)) OVER (ORDER BY tenure) AS cumulative_customers,
    ROUND(
        100.0 * SUM(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)) OVER (ORDER BY tenure)
        / SUM(COUNT(*)) OVER (ORDER BY tenure),
        2
    ) AS cumulative_churn_rate
FROM customers
GROUP BY tenure
ORDER BY tenure;
