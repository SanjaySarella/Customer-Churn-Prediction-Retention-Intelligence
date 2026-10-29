-- Data-quality checks for the churn case study.
SELECT COUNT(*) AS source_rows,
       COUNT(*) - COUNT(DISTINCT customerID) AS duplicate_customer_ids,
       SUM(CASE WHEN tenure IS NULL OR MonthlyCharges IS NULL OR Contract IS NULL
                     OR InternetService IS NULL OR PaymentMethod IS NULL THEN 1 ELSE 0 END) AS incomplete_model_rows
FROM read_csv_auto('data/telco_churn.csv');

-- Descriptive segment comparison used by the application.
SELECT Contract, InternetService,
       COUNT(*) AS customer_records,
       AVG(CASE WHEN Churn = 'Yes' THEN 1.0 ELSE 0.0 END) AS observed_churn_rate
FROM read_csv_auto('data/telco_churn.csv')
GROUP BY Contract, InternetService
ORDER BY customer_records DESC;
