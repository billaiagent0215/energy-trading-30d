"""
Generate 3 charts for the backtest README.

Outputs to outputs/charts/:
    1. monthly_revenue.png      — bar chart, realistic vs ceiling, by month
    2. revenue_vs_spread.png    — scatter, daily revenue vs daily spread
    3. cumulative_revenue.png   — line chart, $ accumulated through the year
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).parent
OUTPUTS = HERE / "outputs"
CHARTS = OUTPUTS / "charts"
CHARTS.mkdir(exist_ok=True)

# Load both backtest CSVs
realistic = pd.read_csv(OUTPUTS / "daily_revenue_realistic.csv", parse_dates=["date"])
ceiling = pd.read_csv(OUTPUTS / "daily_revenue_ceiling.csv", parse_dates=["date"])

# Add month column to both
for df in (realistic, ceiling):
    df["month"] = df["date"].dt.to_period("M").astype(str)


# ---------- Chart 1: Monthly revenue bar chart ----------
fig, ax = plt.subplots(figsize=(12, 5))

monthly_realistic = realistic.groupby("month")["revenue"].sum()
monthly_ceiling = ceiling.groupby("month")["revenue"].sum()

x = range(len(monthly_realistic))
width = 0.4
ax.bar([i - width/2 for i in x], monthly_ceiling.values, width,
       label=f"Ceiling ($0 cycling): ${monthly_ceiling.sum():,.0f} total",
       color="#94a3b8", alpha=0.85)
ax.bar([i + width/2 for i in x], monthly_realistic.values, width,
       label=f"Realistic ($46.30 cycling): ${monthly_realistic.sum():,.0f} total",
       color="#dc2626", alpha=0.85)

ax.set_xticks(list(x))
ax.set_xticklabels(monthly_realistic.index, rotation=45, ha="right")
ax.set_ylabel("Monthly revenue ($)")
ax.set_title("CAISO NP15 Perfect-Foresight Arbitrage — Monthly Revenue\n"
             "Realistic cycling cost vs theoretical ceiling, May 2025 – April 2026",
             fontsize=12)
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(CHARTS / "monthly_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"✓ saved {CHARTS / 'monthly_revenue.png'}")


# ---------- Chart 2: Revenue vs spread scatter ----------
fig, ax = plt.subplots(figsize=(10, 6))

# Realistic: cycled days red, uncycled gray
cycled = realistic[realistic["cycles"] > 0]
uncycled = realistic[realistic["cycles"] == 0]

ax.scatter(uncycled["spread"], uncycled["revenue"], s=20,
           color="#94a3b8", alpha=0.5, label=f"Did not cycle ({len(uncycled)} days)")
ax.scatter(cycled["spread"], cycled["revenue"], s=60,
           color="#dc2626", alpha=0.85, label=f"Cycled ({len(cycled)} days)",
           edgecolors="black", linewidth=0.5)

# Annotate the standout day
top = realistic.loc[realistic["revenue"].idxmax()]
ax.annotate(f"{top['date'].date()}\n${top['revenue']:,.0f}",
            xy=(top["spread"], top["revenue"]),
            xytext=(top["spread"] - 30, top["revenue"] - 2000),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

# Threshold line at $54.5 (cycling cost / RTE)
ax.axvline(54.5, color="#1e3a8a", linestyle="--", linewidth=1,
           label="Spread threshold ($54.5/MWh = $46.30 / 0.85 RTE)")

ax.set_xlabel("Daily price spread ($/MWh)")
ax.set_ylabel("Realistic daily revenue ($)")
ax.set_title("Daily revenue vs daily price spread (realistic cycling cost)\n"
             "Cycles only happen when spread clears the wear threshold",
             fontsize=12)
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CHARTS / "revenue_vs_spread.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"✓ saved {CHARTS / 'revenue_vs_spread.png'}")


# ---------- Chart 3: Cumulative revenue line chart ----------
fig, ax = plt.subplots(figsize=(12, 5))

realistic_sorted = realistic.sort_values("date").copy()
ceiling_sorted = ceiling.sort_values("date").copy()
realistic_sorted["cumulative"] = realistic_sorted["revenue"].cumsum()
ceiling_sorted["cumulative"] = ceiling_sorted["revenue"].cumsum()

ax.plot(ceiling_sorted["date"], ceiling_sorted["cumulative"],
        color="#94a3b8", linewidth=2,
        label=f"Ceiling ($0 cycling): ${ceiling_sorted['cumulative'].iloc[-1]:,.0f}")
ax.plot(realistic_sorted["date"], realistic_sorted["cumulative"],
        color="#dc2626", linewidth=2,
        label=f"Realistic ($46.30 cycling): ${realistic_sorted['cumulative'].iloc[-1]:,.0f}")

# Annotate the March 20 step-up in realistic
march20 = realistic_sorted[realistic_sorted["date"] == "2026-03-20"]
if len(march20) > 0:
    ax.annotate("2026-03-20\nSingle day = 15% of year",
                xy=(march20["date"].iloc[0], march20["cumulative"].iloc[0]),
                xytext=(pd.Timestamp("2025-09-01"), march20["cumulative"].iloc[0] + 8000),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

ax.set_xlabel("Date")
ax.set_ylabel("Cumulative revenue ($)")
ax.set_title("Cumulative arbitrage revenue through the year\n"
             "Notice how a handful of event days drive most of the realistic revenue",
             fontsize=12)
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CHARTS / "cumulative_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"✓ saved {CHARTS / 'cumulative_revenue.png'}")


print(f"\nAll 3 charts saved to {CHARTS}/")
