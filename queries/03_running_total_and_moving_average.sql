-- Daily revenue, cumulative revenue and a 7-day moving average.
WITH daily AS (
    SELECT
        o.order_date                     AS day,
        SUM(oi.quantity * p.unit_price)  AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY o.order_date
)
SELECT
    day,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY day), 2) AS cumulative_revenue,
    ROUND(AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moving_avg_7d
FROM daily
ORDER BY day;
