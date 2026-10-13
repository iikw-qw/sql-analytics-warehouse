import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import core, data

OUT = Path("reports")


def main():
    OUT.mkdir(exist_ok=True)
    conn = data.build_database()
    results = {name: core.run_query(conn, name) for name in core.list_queries()}
    for name, frame in results.items():
        frame.to_csv(OUT / f"{name}.csv", index=False)

    monthly = results["01_monthly_revenue"]
    daily = results["03_running_total_and_moving_average"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].bar(monthly["month"], monthly["revenue"], color="grey")
    axes[0].set_title("Monthly revenue (completed orders)")
    axes[0].tick_params(axis="x", rotation=90, labelsize=7)
    axes[1].plot(daily["day"], daily["moving_avg_7d"], color="black")
    axes[1].set_title("7-day moving average of daily revenue")
    axes[1].set_xticks(daily["day"][::90])
    axes[1].tick_params(axis="x", rotation=30, labelsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "revenue.png", dpi=130)

    repeat = results["04_repeat_purchase_rate"]
    pairs = results["05_frequently_bought_together"]
    summary = {
        "tables": {
            t: int(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
            for t in ["customers", "products", "orders", "order_items"]
        },
        "queries": core.list_queries(),
        "months_covered": int(len(monthly)),
        "best_month": monthly.loc[monthly["revenue"].idxmax(), "month"],
        "avg_repeat_rate_90d": round(float(repeat["repeat_rate"].mean()), 3),
        "top_pair": [pairs.iloc[0]["product_a"], pairs.iloc[0]["product_b"], int(pairs.iloc[0]["together"])],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
