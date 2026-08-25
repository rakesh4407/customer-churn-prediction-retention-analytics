-- ============================================================
-- 01_customer_analysis.sql
-- Customer demographics and segmentation analysis
-- Dataset: IBM Telco Customer Churn (7,043 records)
-- ============================================================

-- 1. Overall customer base summary
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) AS male_customers,
    SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS female_customers,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_total_charges
FROM customers;

-- 2. Customer distribution by gender and senior citizen status
SELECT
    gender,
    SeniorCitizen,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS pct_of_total
FROM customers
GROUP BY gender, SeniorCitizen
ORDER BY gender, SeniorCitizen;

-- 3. Customers with dependents and partners — family profile
SELECT
    Partner,
    Dependents,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
GROUP BY Partner, Dependents
ORDER BY customer_count DESC;

-- 4. Customer tenure distribution — lifecycle segments
SELECT
    CASE
        WHEN tenure BETWEEN 1 AND 12 THEN '1-12 months (New)'
        WHEN tenure BETWEEN 13 AND 24 THEN '13-24 months (Growing)'
        WHEN tenure BETWEEN 25 AND 48 THEN '25-48 months (Established)'
        WHEN tenure > 48 THEN '49-72 months (Loyal)'
        ELSE '0 months (Just joined)'
    END AS tenure_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS pct_of_total,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(SUM(TotalCharges), 2) AS segment_total_revenue
FROM customers
GROUP BY tenure_segment
ORDER BY MIN(tenure);

-- 5. Senior citizen analysis — demographics and spend
SELECT
    CASE WHEN SeniorCitizen = 1 THEN 'Senior' ELSE 'Non-Senior' END AS citizen_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_total_charges,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY citizen_type;
