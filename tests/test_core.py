import pytest

from src import core, data


@pytest.fixture(scope="module")
def conn():
    return data.build_database(n_customers=300, n_products=25, n_orders=1500, seed=1)


def test_all_queries_run(conn):
    for name in core.list_queries():
        frame = core.run_query(conn, name)
        assert len(frame) > 0, name


def test_monthly_revenue_matches_direct_sum(conn):
    monthly = core.run_query(conn, "01_monthly_revenue")
    direct = conn.execute(
        """SELECT SUM(oi.quantity * p.unit_price)
           FROM orders o JOIN order_items oi USING(order_id) JOIN products p USING(product_id)
           WHERE o.status = 'completed'"""
    ).fetchone()[0]
    assert monthly["revenue"].sum() == pytest.approx(direct, rel=1e-4)


def test_cumulative_revenue_is_monotone(conn):
    daily = core.run_query(conn, "03_running_total_and_moving_average")
    assert daily["cumulative_revenue"].is_monotonic_increasing


def test_country_ranks_start_at_one(conn):
    top = core.run_query(conn, "02_top_customers")
    assert top.groupby("country")["country_rank"].min().eq(1).all()


def test_repeat_rate_is_a_share(conn):
    rate = core.run_query(conn, "04_repeat_purchase_rate")["repeat_rate"]
    assert rate.between(0, 1).all()


def test_no_orphan_order_items(conn):
    orphans = conn.execute(
        "SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o USING(order_id) WHERE o.order_id IS NULL"
    ).fetchone()[0]
    assert orphans == 0
