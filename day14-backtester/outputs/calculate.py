"""
Verification analysis for Day 14 backtest.

Q1: Of the 15 days where cycles > 0 in the realistic run, which months are they in?
Q2: In the ceiling run, what are the top 10 highest-revenue days and their spreads?
"""

import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent

# Load the two CSVs (note: dates are stored as strings in CSV; parse them back)
realistic = pd.read_csv(HERE / "daily_revenue_realistic.csv", parse_dates=["date"])
ceiling = pd.read_csv(HERE / "daily_revenue_ceiling.csv", parse_dates=["date"])


# ---------- Question 1 ----------
print("=" * 60)
print("Q1: Days that cycled in the realistic run ($46.30 cycling cost)")
print("=" * 60)

# Filter to only cycled days
cycled = realistic[realistic["cycles"] > 0].copy()

# Add a month column for grouping
cycled["month"] = cycled["date"].dt.to_period("M")

# Show every cycled day, sorted by revenue (biggest first)
print("\nAll cycled days, sorted by revenue:")
print(cycled[["date", "revenue", "cycles", "spread"]]
      .sort_values("revenue", ascending=False)
      .to_string(index=False))

# Count days cycled per month
print("\nCycled days per month:")
print(cycled.groupby("month").size().to_string())


# ---------- Question 2 ----------
print("\n" + "=" * 60)
print("Q2: Top 10 highest-revenue days in the ceiling run ($0 cycling cost)")
print("=" * 60)

top10 = (ceiling
         .sort_values("revenue", ascending=False)
         .head(10)
         [["date", "revenue", "cycles", "spread"]])
print(top10.to_string(index=False))

# Also show top-10 months
print("\nMonth-of-year for the top-10 ceiling-run days:")
top10_with_month = top10.copy()
top10_with_month["month"] = top10_with_month["date"].dt.month_name()
print(top10_with_month["month"].value_counts().to_string())
