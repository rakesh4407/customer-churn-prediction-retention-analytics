-- ============================================================
-- 04_customer_segments.sql
-- Customer segmentation analysis — RFM-style and value tiers
-- Dataset: IBM Telco Customer Churn (7,043 records)
-- ============================================================

-- 1. Segment customers by tenure + monthly spend (2x2 matrix)
SELECT
    CASE WHEN tenure > 24 THEN 'Long-term' ELSE 'Short-term' END AS tenure_type,
    CASE WHEN MonthlyCharges > 65 THEN 'High-spend' ELSE 'Low-spend' END AS spend_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly,
    ROUND(AVG(TotalCharges), 2) AS avg_lifetime_value,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY tenure_type, spend_type
ORDER BY churn_rate DESC;

-- 2. High-value customer segment (top 25% by TotalCharges)
SELECT
    'High-Value' AS segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly,
    ROUND(AVG(TotalCharges), 2) AS avg_lifetime,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
WHERE TotalCharges > (
    SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY TotalCharges)
    FROM customers
);

-- 3. At-risk segment: month-to-month + no online security + no tech support
SELECT
    'At-Risk Segment' AS segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_at_risk,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
WHERE Contract = 'Month-to-month'
  AND OnlineSecurity = 'No'
  AND TechSupport = 'No';

-- 4. Loyal customer segment: 2-year contract + tenure > 36
SELECT
    'Loyal Segment' AS segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly,
    ROUND(AVG(TotalCharges), 2) AS avg_lifetime,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
WHERE Contract = 'Two year'
  AND tenure > 36;

-- 5. CTE: Segment all customers into 4 business tiers
WITH customer_segments AS (
    SELECT
        customerID,
        Contract,
        tenure,
        MonthlyCharges,
        TotalCharges,
        Churn,
        CASE
            WHEN Contract = 'Two year' AND tenure > 24          THEN 'Loyal'
            WHEN Contract = 'Month-to-month' AND tenure <= 12   THEN 'High-Risk New'
            WHEN MonthlyCharges > 80                            THEN 'High-Value'
            ELSE 'Standard'
        END AS CustomerSegment
    FROM customers
)
SELECT
    CustomerSegment,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly,
    ROUND(SUM(TotalCharges), 2) AS total_revenue,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customer_segments
GROUP BY CustomerSegment
ORDER BY churn_rate DESC;

-- 6. Window function: RANK customers within segment by monthly spend
WITH customer_segments AS (
    SELECT
        customerID,
        Contract,
        tenure,
        MonthlyCharges,
        TotalCharges,
        Churn,
        CASE
            WHEN Contract = 'Two year' AND tenure > 24        THEN 'Loyal'
            WHEN Contract = 'Month-to-month' AND tenure <= 12 THEN 'High-Risk New'
            WHEN MonthlyCharges > 80                          THEN 'High-Value'
            ELSE 'Standard'
        END AS CustomerSegment
    FROM customers
)
SELECT
    customerID,
    CustomerSegment,
    Contract,
    tenure,
    MonthlyCharges,
    Churn,
    RANK() OVER (
        PARTITION BY CustomerSegment
        ORDER BY MonthlyCharges DESC
    ) AS spend_rank_in_segment,
    ROUND(AVG(MonthlyCharges) OVER (PARTITION BY CustomerSegment), 2) AS segment_avg_charges
FROM customer_segments
ORDER BY CustomerSegment, spend_rank_in_segment
LIMIT 40;
