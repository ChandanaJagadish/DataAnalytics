"""
SQL Multi-Table Analysis Project
---------------------------------
Builds a small SQLite database (sellers -> orders -> shipments) and runs
JOIN / GROUP BY / aggregate queries to find which sellers have the
highest late-shipment rate.

Run with:  python3 sql_analysis.py
"""

import sqlite3
import random

DB_FILE = "shipments.db"

# ----------------------------------------------------------------------
# PART A: Build schema + generate sample data
# ----------------------------------------------------------------------

def build_database():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Start fresh every run
    cur.executescript("""
    DROP TABLE IF EXISTS shipments;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS sellers;

    CREATE TABLE sellers (
        seller_id   INTEGER PRIMARY KEY,
        seller_name TEXT NOT NULL
    );

    CREATE TABLE orders (
        order_id   INTEGER PRIMARY KEY,
        seller_id  INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
    );

    CREATE TABLE shipments (
        shipment_id   INTEGER PRIMARY KEY,
        order_id      INTEGER NOT NULL,
        expected_days INTEGER NOT NULL,
        actual_days   INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """)

    # --- 10 sellers, each with a "reliability" score baked in on purpose
    # so the late-rate query has something real to uncover.
    seller_names = [
        "Acme Supply Co", "Northwind Traders", "Pinecrest Goods",
        "Bluebird Imports", "Summit Wholesale", "Riverside Mercantile",
        "Cascade Distribution", "Harbor & Co", "Ironwood Traders",
        "Golden Gate Supply"
    ]
    # Lower = more reliable (less likely to ship late)
    reliability = [0.05, 0.10, 0.15, 0.20, 0.25,
                   0.30, 0.35, 0.45, 0.55, 0.65]

    random.seed(42)  # reproducible results

    sellers = list(enumerate(seller_names, start=1))
    cur.executemany(
        "INSERT INTO sellers (seller_id, seller_name) VALUES (?, ?)",
        sellers
    )

    order_id = 1
    shipment_id = 1
    order_rows = []
    shipment_rows = []

    for seller_id, _ in sellers:
        late_prob = reliability[seller_id - 1]
        num_orders = random.randint(15, 25)  # ~200 orders total across 10 sellers

        for _ in range(num_orders):
            order_date = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            order_rows.append((order_id, seller_id, order_date))

            expected_days = random.randint(2, 7)
            is_late = random.random() < late_prob
            if is_late:
                actual_days = expected_days + random.randint(1, 6)
            else:
                actual_days = random.randint(1, expected_days)

            shipment_rows.append((shipment_id, order_id, expected_days, actual_days))

            order_id += 1
            shipment_id += 1

    cur.executemany(
        "INSERT INTO orders (order_id, seller_id, order_date) VALUES (?, ?, ?)",
        order_rows
    )
    cur.executemany(
        "INSERT INTO shipments (shipment_id, order_id, expected_days, actual_days) "
        "VALUES (?, ?, ?, ?)",
        shipment_rows
    )

    conn.commit()
    print(f"Database built: {len(sellers)} sellers, {len(order_rows)} orders, "
          f"{len(shipment_rows)} shipments.\n")
    return conn


# ----------------------------------------------------------------------
# PART B: The core query — late-shipment rate per seller
# ----------------------------------------------------------------------

LATE_RATE_QUERY = """
SELECT
    s.seller_name,
    COUNT(sh.shipment_id)                                   AS total_shipments,
    SUM(CASE WHEN sh.actual_days > sh.expected_days THEN 1 ELSE 0 END) AS late_shipments,
    ROUND(
        100.0 * SUM(CASE WHEN sh.actual_days > sh.expected_days THEN 1 ELSE 0 END)
        / COUNT(sh.shipment_id),
        1
    ) AS late_rate_pct
FROM sellers s
JOIN orders    o  ON o.seller_id = s.seller_id
JOIN shipments sh ON sh.order_id = o.order_id
GROUP BY s.seller_id, s.seller_name
ORDER BY late_rate_pct DESC;
"""


# ----------------------------------------------------------------------
# PART C: Simpler warm-up query — just WHERE + COUNT (no JOIN yet)
# Counts late shipments overall, without breaking out by seller.
# Useful as a stepping stone before tackling the full JOIN version above.
# ----------------------------------------------------------------------

SIMPLE_LATE_COUNT_QUERY = """
SELECT
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN actual_days > expected_days THEN 1 ELSE 0 END) AS late_shipments
FROM shipments
WHERE expected_days IS NOT NULL;
"""


# ----------------------------------------------------------------------
# PART D (optional tweak): average delay per seller instead of late-rate
# Shows how much of the same JOIN/GROUP BY skeleton can be reused to
# answer a *different* question — proof you understand the query.
# ----------------------------------------------------------------------

AVG_DELAY_QUERY = """
SELECT
    s.seller_name,
    ROUND(AVG(sh.actual_days - sh.expected_days), 2) AS avg_delay_days
FROM sellers s
JOIN orders    o  ON o.seller_id = s.seller_id
JOIN shipments sh ON sh.order_id = o.order_id
GROUP BY s.seller_id, s.seller_name
ORDER BY avg_delay_days DESC;
"""


def run_query(conn, label, query):
    print(f"--- {label} ---")
    cur = conn.cursor()
    cur.execute(query)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()

    # simple column-aligned print
    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) if rows else len(str(c))
              for i, c in enumerate(cols)]
    header = " | ".join(c.ljust(w) for c, w in zip(cols, widths))
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(v).ljust(w) for v, w in zip(r, widths)))
    print()
    return rows


if __name__ == "__main__":
    conn = build_database()

    run_query(conn, "Part C: Simple WHERE + COUNT (overall late count)",
               SIMPLE_LATE_COUNT_QUERY)

    run_query(conn, "Part B: Late-shipment rate per seller (main query)",
               LATE_RATE_QUERY)

    run_query(conn, "Part D: Average delay per seller (tweak / alt question)",
               AVG_DELAY_QUERY)

    conn.close()
    print(f"Done. Database saved as {DB_FILE} in the current folder.")