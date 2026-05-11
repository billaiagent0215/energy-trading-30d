"""
Day 5 — battery daily P&L computation.
Decomposes total revenue into DA arbitrage + RT correction.
"""
import pandas as pd


# === 1. CREATE the data =====================================================
# A DataFrame from a dict: each key becomes a column, each list becomes the
# column's values. Row indices auto-number 0,1,2,...
df = pd.DataFrame({
    "hour":       [2, 3, 4, 5, 17, 18, 19, 20],
    "da_price":   [30, 32, 35, 33, 150, 200, 250, 180],
    "rt_price":   [25, 28, 30, 40, 130, 280, 230, 160],
    "da_commit":  [-100, -100, -100, -100, +90, +90, +90, +90],
    "rt_actual":  [-100, -100, -100, -100, +90, +70, +110, +90],
})

print("Input data:")
print(df)
print()


# === 2. COMPUTE settlement columns (vectorized) =============================
# These look like single-value operations but pandas applies them to every
# row at once. df["da_commit"] is a whole column; multiplying it by
# df["da_price"] (also a column) gives a new column of the same length.
df["da_settlement"] = df["da_commit"] * df["da_price"]
df["deviation"]     = df["rt_actual"] - df["da_commit"]
df["rt_settlement"] = df["deviation"] * df["rt_price"]
df["total"]         = df["da_settlement"] + df["rt_settlement"]

print("With settlements:")
print(df)
print()


# === 3. AGGREGATE — total revenue & decomposition ===========================
# .sum() on a column collapses it to a single number.
da_arbitrage   = df["da_settlement"].sum()
rt_correction  = df["rt_settlement"].sum()
total_revenue  = da_arbitrage + rt_correction

print(f"DA arbitrage:  ${da_arbitrage:>10,.0f}")
print(f"RT correction: ${rt_correction:>10,.0f}")
print(f"Total revenue: ${total_revenue:>10,.0f}")
print()


# === 4. INSPECT — which hours had the biggest RT impact? ====================
# Filter to only hours where deviation != 0, then sort by absolute RT impact
# to find the most important deviations.
deviated = df[df["deviation"] != 0].copy()
deviated["abs_rt_impact"] = deviated["rt_settlement"].abs()
deviated = deviated.sort_values("abs_rt_impact", ascending=False)

print("Hours where actual delivery differed from DA commitment:")
print(deviated[["hour", "da_commit", "rt_actual", "deviation",
                "rt_price", "rt_settlement"]])
print()


# === 5. SANITY CHECK — energy balance & implied RTE =========================
# Negative rt_actual = charging (energy into battery)
# Positive rt_actual = discharging (energy out of battery)
charged_mwh    = -df.loc[df["rt_actual"] < 0, "rt_actual"].sum()
discharged_mwh =  df.loc[df["rt_actual"] > 0, "rt_actual"].sum()

print(f"Energy charged:    {charged_mwh:>6.0f} MWh")
print(f"Energy discharged: {discharged_mwh:>6.0f} MWh")
print(f"Implied RTE:       {discharged_mwh / charged_mwh:>6.2%}")