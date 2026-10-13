-- Product pairs that appear in the same order most often, with a simple lift against independence.
WITH n_orders AS (
    SELECT COUNT(DISTINCT order_id) AS total FROM order_items
),
product_orders AS (
    SELECT product_id, COUNT(*) AS cnt FROM order_items GROUP BY product_id
),
pairs AS (
    SELECT a.product_id AS product_a, b.product_id AS product_b, COUNT(*) AS together
    FROM order_items a
    JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
    GROUP BY a.product_id, b.product_id
)
SELECT
    pa.name AS product_a,
    pb.name AS product_b,
    pairs.together,
    ROUND(pairs.together * 1.0 * n.total / (poa.cnt * pob.cnt), 2) AS lift
FROM pairs
JOIN n_orders n
JOIN product_orders poa ON poa.product_id = pairs.product_a
JOIN product_orders pob ON pob.product_id = pairs.product_b
JOIN products pa ON pa.product_id = pairs.product_a
JOIN products pb ON pb.product_id = pairs.product_b
WHERE pairs.together >= 5
ORDER BY pairs.together DESC, lift DESC
LIMIT 15;
