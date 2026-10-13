-- Share of customers who placed a second order within 90 days of the first, by signup quarter.
WITH ranked AS (
    SELECT
        o.customer_id,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id) AS n
    FROM orders o
    WHERE o.status = 'completed'
),
firsts AS (
    SELECT customer_id, order_date AS first_date FROM ranked WHERE n = 1
),
seconds AS (
    SELECT customer_id, order_date AS second_date FROM ranked WHERE n = 2
)
SELECT
    strftime('%Y', c.signup_date) || '-Q' || ((CAST(strftime('%m', c.signup_date) AS INTEGER) + 2) / 3) AS signup_quarter,
    COUNT(*) AS customers,
    SUM(CASE WHEN julianday(s.second_date) - julianday(f.first_date) <= 90 THEN 1 ELSE 0 END) AS repeat_90d,
    ROUND(AVG(CASE WHEN julianday(s.second_date) - julianday(f.first_date) <= 90 THEN 1.0 ELSE 0.0 END), 3) AS repeat_rate
FROM customers c
JOIN firsts f      ON f.customer_id = c.customer_id
LEFT JOIN seconds s ON s.customer_id = c.customer_id
GROUP BY signup_quarter
ORDER BY signup_quarter;
