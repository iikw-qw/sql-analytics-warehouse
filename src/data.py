import sqlite3

import numpy as np
import pandas as pd

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    signup_date TEXT NOT NULL,
    country TEXT NOT NULL,
    segment TEXT NOT NULL
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL NOT NULL,
    unit_price REAL NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
"""

COUNTRIES = ["DE", "FR", "ES", "IT", "PL", "NL"]
CATEGORIES = ["coffee", "tea", "equipment", "accessories", "snacks"]


def build_database(path=":memory:", n_customers=1500, n_products=60, n_orders=9000, seed=3):
    rng = np.random.default_rng(seed)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)

    signup = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 540, n_customers), unit="D")
    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, n_customers + 1),
            "signup_date": signup.strftime("%Y-%m-%d"),
            "country": rng.choice(COUNTRIES, n_customers),
            "segment": rng.choice(["consumer", "business"], n_customers, p=[0.8, 0.2]),
        }
    )

    cost = np.round(rng.uniform(2, 60, n_products), 2)
    products = pd.DataFrame(
        {
            "product_id": np.arange(1, n_products + 1),
            "name": [f"item_{i:03d}" for i in range(1, n_products + 1)],
            "category": rng.choice(CATEGORIES, n_products),
            "unit_cost": cost,
            "unit_price": np.round(cost * rng.uniform(1.3, 2.2, n_products), 2),
        }
    )

    # orders per customer are skewed; each customer's orders follow each other with random gaps
    activity = rng.pareto(2.0, n_customers) + 0.3
    cust_idx = np.sort(rng.choice(n_customers, size=n_orders, p=activity / activity.sum()))
    gaps = rng.exponential(110, n_orders)
    gaps = pd.Series(gaps).groupby(cust_idx).cumsum().values
    dates = signup[cust_idx] + pd.to_timedelta(gaps, unit="D")
    keep = dates <= pd.Timestamp("2025-06-30")
    cust_idx, dates = cust_idx[keep], dates[keep]
    n_orders = len(cust_idx)
    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, n_orders + 1),
            "customer_id": customers["customer_id"].values[cust_idx],
            "order_date": pd.DatetimeIndex(dates).strftime("%Y-%m-%d"),
            "status": rng.choice(["completed", "returned", "cancelled"], n_orders, p=[0.9, 0.06, 0.04]),
        }
    )

    items = []
    for oid in orders["order_id"]:
        n_lines = rng.integers(1, 5)
        for pid in rng.choice(products["product_id"], n_lines, replace=False):
            items.append((oid, int(pid), int(rng.integers(1, 4))))
    order_items = pd.DataFrame(items, columns=["order_id", "product_id", "quantity"])

    for name, frame in [
        ("customers", customers),
        ("products", products),
        ("orders", orders),
        ("order_items", order_items),
    ]:
        frame.to_sql(name, conn, if_exists="append", index=False)
    conn.commit()
    return conn
