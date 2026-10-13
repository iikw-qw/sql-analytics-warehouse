-- Monthly revenue and gross margin for completed orders, with growth over the previous month.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date)              AS month,
        SUM(oi.quantity * p.unit_price)              AS revenue,
        SUM(oi.quantity * (p.unit_price - p.unit_cost)) AS margin,
        COUNT(DISTINCT o.order_id)                   AS orders
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2)                                          AS revenue,
    ROUND(margin * 1.0 / revenue, 3)                           AS margin_rate,
    orders,
    ROUND(revenue * 1.0 / LAG(revenue) OVER (ORDER BY month) - 1, 3) AS mom_growth
FROM monthly
ORDER BY month;
