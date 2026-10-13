-- Top customers by lifetime revenue, with rank inside their country and share of the country total.
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.country,
        c.segment,
        SUM(oi.quantity * p.unit_price) AS revenue,
        COUNT(DISTINCT o.order_id)      AS orders
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id AND o.status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    GROUP BY c.customer_id
)
SELECT *
FROM (
    SELECT
        customer_id,
        country,
        segment,
        ROUND(revenue, 2) AS revenue,
        orders,
        RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS country_rank,
        ROUND(revenue * 1.0 / SUM(revenue) OVER (PARTITION BY country), 4) AS country_share
    FROM customer_revenue
)
WHERE country_rank <= 3
ORDER BY country, country_rank;
