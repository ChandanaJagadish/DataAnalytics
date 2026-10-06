"""
Metric Anomaly Monitor
Tracks a daily operational metric, calculates a rolling baseline,
and flags days that deviate significantly from normal.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------- PART A: Simulate realistic daily data ----------
np.random.seed(42)  # so results are reproducible while you're testing

num_days = 90
dates = pd.date_range(start="2026-06-01", periods=num_days, freq="D")

# Base pattern: orders hover around 500/day with normal random noise
base_orders = np.random.normal(loc=500, scale=30, size=num_days)

# Inject a few deliberate anomalies so the detector has something to catch
base_orders[20] = 720   # sudden spike
base_orders[45] = 280   # sudden drop
base_orders[70] = 650   # moderate spike

df = pd.DataFrame({"date": dates, "orders": base_orders})

# ---------- PART B: Rolling baseline ----------
window = 7
df["rolling_mean"] = df["orders"].rolling(window=window, min_periods=1).mean()
df["rolling_std"] = df["orders"].rolling(window=window, min_periods=1).std()

# ---------- PART C: Flag anomalies ----------
THRESHOLD = 1.5  # number of standard deviations that counts as "unusual"

df["deviation"] = (df["orders"] - df["rolling_mean"]) / df["rolling_std"]
df["is_anomaly"] = df["deviation"].abs() > THRESHOLD

# ---------- PART D: Log alerts with context ----------
anomalies = df[df["is_anomaly"]]

print(f"Checked {num_days} days of data. Found {len(anomalies)} anomalies.\n")

for _, row in anomalies.iterrows():
    direction = "HIGH" if row["deviation"] > 0 else "LOW"
    print(
        f"[{row['date'].date()}] ANOMALY ({direction}): "
        f"orders={row['orders']:.0f}, "
        f"expected~{row['rolling_mean']:.0f}, "
        f"deviation={row['deviation']:.2f} std devs"
    )

# ---------- PART E: Visualize ----------
plt.figure(figsize=(12, 5))
plt.plot(df["date"], df["orders"], label="Daily Orders", color="steelblue")
plt.plot(df["date"], df["rolling_mean"], label="7-day Rolling Average", color="orange", linestyle="--")

# Shaded "normal" band = rolling_mean +/- threshold * rolling_std
plt.fill_between(
    df["date"],
    df["rolling_mean"] - THRESHOLD * df["rolling_std"],
    df["rolling_mean"] + THRESHOLD * df["rolling_std"],
    color="orange",
    alpha=0.15,
    label="Normal Range",
)

# Mark anomalies
plt.scatter(anomalies["date"], anomalies["orders"], color="red", zorder=5, label="Anomaly")

plt.title("Daily Orders with Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Orders")
plt.legend()
plt.tight_layout()
plt.savefig("anomaly_chart.png")
print("\nChart saved as anomaly_chart.png")
plt.show()