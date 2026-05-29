import pandas as pd
import pathlib as Path

from data_loader import load_year
from optimizer import solve_day

df = load_year()

print(df.head())
print(f"Total rows: {len(df)}")

# Convert UTC → Pacific Time
df["interval_start"] = df["interval_start"].dt.tz_convert("America/Los_Angeles")

# Add a column with just the local date (no time-of-day)
df["local_date"] = df["interval_start"].dt.date

print(df[["interval_start", "local_date", "lmp"]].head())
print(f"Unique local dates: {df['local_date'].nunique()}")

hours_per_day = df.groupby("local_date").size()
print(hours_per_day.value_counts())

# Collect results across all valid days
results = []

for date, day_df in df.groupby("local_date"):
    if len(day_df) != 24:
        continue  # skip DST days

    day_df = day_df.sort_values("interval_start")
    prices = day_df["lmp"].values

    out = solve_day(prices)

    results.append({
        "date": date,
        "revenue": out["revenue"],
        "gross": out["gross"],
        "cycling": out["cycling"],
        "cycles": out["cycles"],
        "spread": prices.max() - prices.min(),
    })

print(f"Solved {len(results)} days")
print(f"First day:  {results[0]}")
print(f"Last day:   {results[-1]}")


results_df = pd.DataFrame(results)

annual_revenue = results_df["revenue"].sum()
total_cycles = results_df["cycles"].sum()
days_cycled = (results_df["cycles"] > 0).sum()
per_kw_year = annual_revenue / 100_000   # 100 MW = 100,000 kW

print()
print(f"Annual revenue:   ${annual_revenue:>15,.2f}")
print(f"$/kW-year:        ${per_kw_year:>15.2f}")
print(f"Total cycles:     {total_cycles:>16.1f}")
print(f"Days cycled:      {days_cycled:>11} / {len(results_df)}")