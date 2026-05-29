import pandas as pd
from pathlib import Path

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

def run_backtest(cycling_cost, label):
    """Run the full backtest with a given cycling cost. Returns results DataFrame."""
    results = []
    for date, day_df in df.groupby("local_date"):
        if len(day_df) != 24:
            continue
        day_df = day_df.sort_values("interval_start")
        prices = day_df["lmp"].values

        out = solve_day(prices, CYCLING_COST=cycling_cost)

        results.append({
            "date": date,
            "revenue": out["revenue"],
            "gross": out["gross"],
            "cycling": out["cycling"],
            "cycles": out["cycles"],
            "spread": prices.max() - prices.min(),
        })

    results_df = pd.DataFrame(results)
    annual_revenue = results_df["revenue"].sum()
    per_kw_year = annual_revenue / 100_000
    days_cycled = (results_df["cycles"] > 0).sum()
    total_cycles = results_df["cycles"].sum()

    print(f"\n{label}")
    print(f"  Annual revenue:  ${annual_revenue:>15,.2f}")
    print(f"  $/kW-year:       ${per_kw_year:>15.2f}")
    print(f"  Total cycles:    {total_cycles:>16.1f}")
    print(f"  Days cycled:     {days_cycled:>11} / {len(results_df)}")
    return results_df

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

print("=" * 60)
realistic = run_backtest(46.30, "WITH cycling cost ($46.30/MWh, realistic)")
realistic.to_csv(output_dir / "daily_revenue_realistic.csv", index=False)

ceiling = run_backtest(0.0, "WITHOUT cycling cost ($0/MWh, theoretical ceiling)")
ceiling.to_csv(output_dir / "daily_revenue_ceiling.csv", index=False)
print("=" * 60)

print(f"\nSaved daily results to {output_dir}/")