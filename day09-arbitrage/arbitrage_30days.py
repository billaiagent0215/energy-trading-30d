"""
Day 9 — single-day battery arbitrage as a perfect-foresight LP.

Inputs:
    prices : list of 24 hourly DA prices ($/MWh)
    battery specs (P_max, E_max, RTE, S_0)

Outputs:
    charge schedule, discharge schedule, SOC trajectory, total revenue
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pulp


# ---------- 1. LOAD PRICES (from your weekend project's cache) -------------
CACHE = Path("../day06-07-price-shape/data/caiso_np15_da_30d.parquet")
df = pd.read_parquet(CACHE)
df["date"] = df["Time"].dt.date
df["hour"] = df["Time"].dt.hour

# Pick a single day to optimize — let's use the most expensive day on average,
# which is where arbitrage value is highest.
daily_mean = df.groupby("date")["LMP"].mean()
target_day = daily_mean.idxmax()
day_df     = df[df["date"] == target_day].sort_values("hour").reset_index(drop=True)
prices     = day_df["LMP"].tolist()

print(f"Optimizing for {target_day}  (mean ${daily_mean[target_day]:.2f}/MWh)")
print(f"24 hourly prices: min ${min(prices):.2f}, max ${max(prices):.2f}")


# ---------- 2. BATTERY PARAMETERS ------------------------------------------
P_MAX = 100     # MW  — power rating
E_MAX = 400     # MWh — energy capacity
RTE   = 0.90    # round-trip efficiency
S_0   = 0       # starting SOC (MWh)
T     = 24      # hours


# ---------- 3. SOLVE FUNCTION ----------------------------------------------
def solve_day(prices, P_max=100, E_max=400, RTE=0.90, S_0=0,
              cycling_cost=0.0):
    """
    Solve single-day battery arbitrage LP.
    cycling_cost: $/MWh penalty applied to discharge (per-MWh throughput cost).
    Returns: (revenue, charge_sched, discharge_sched, soc_traj)
    """
    T = len(prices)
    model = pulp.LpProblem("battery_arbitrage", pulp.LpMaximize)

    c = [pulp.LpVariable(f"c_{t}", lowBound=0, upBound=P_max) for t in range(T)]
    d = [pulp.LpVariable(f"d_{t}", lowBound=0, upBound=P_max) for t in range(T)]
    s = [pulp.LpVariable(f"s_{t}", lowBound=0, upBound=E_max) for t in range(T)]

    # Objective now includes cycling-cost penalty on discharge
    model += pulp.lpSum(
        prices[t] * d[t]                       # revenue from discharge
        - prices[t] * c[t]                     # cost of charging
        - cycling_cost * d[t]                  # degradation cost
        for t in range(T)
    )

    for t in range(T):
        prev = S_0 if t == 0 else s[t-1]
        model += s[t] == prev + RTE * c[t] - d[t]
    model += s[T-1] >= S_0

    model.solve(pulp.PULP_CBC_CMD(msg=0))

    return (
        pulp.value(model.objective),
        [pulp.value(c[t]) for t in range(T)],
        [pulp.value(d[t]) for t in range(T)],
        [pulp.value(s[t]) for t in range(T)],
    )


# ---------- 4. RUN BOTH SCENARIOS ON THE TARGET DAY -------------------------
rev_no_cost, _, _, _      = solve_day(prices, cycling_cost=0.0)
rev_with_cost, c_w, d_w, s_w = solve_day(prices, cycling_cost=46.30)

print(f"\n{'Scenario':<30}{'Revenue':>12}")
print(f"{'No cycling cost':<30}${rev_no_cost:>11,.2f}")
print(f"{'$46.30/MWh cycling cost':<30}${rev_with_cost:>11,.2f}")
print(f"{'Total discharge w/ cost':<30}{sum(d_w):>11.1f} MWh")

# ---------- 5. 30-DAY BACKTEST ----------------------------------------------
results = []
for date_val, day_df in df.groupby("date"):
    day_prices = day_df.sort_values("hour")["LMP"].tolist()
    if len(day_prices) != 24:
        continue  # skip DST-incomplete days

    r_no, _, d_no, _   = solve_day(day_prices, cycling_cost=0.0)
    r_cc, _, d_cc, _   = solve_day(day_prices, cycling_cost=46.30)

    results.append({
        "date":            date_val,
        "rev_no_cost":     r_no,
        "rev_with_cost":   r_cc,
        "discharge_no":    sum(d_no),
        "discharge_cc":    sum(d_cc),
        "day_spread":      max(day_prices) - min(day_prices),
    })

bt = pd.DataFrame(results)

# ---------- 6. HEADLINE NUMBERS --------------------------------------------
total_no  = bt["rev_no_cost"].sum()
total_cc  = bt["rev_with_cost"].sum()
days_active_cc = (bt["rev_with_cost"] > 0.01).sum()

# Back-of-envelope from weekend project: $20.12 spread × 100MW × 4h × 0.9
backenv_per_day = 20.12 * 100 * 4 * 0.9
backenv_total   = backenv_per_day * len(bt)

print(f"\n{'='*55}")
print(f"30-DAY BACKTEST — CAISO NP15")
print(f"{'='*55}")
print(f"Days in dataset:                 {len(bt)}")
print(f"Back-of-envelope (May avg):      ${backenv_total:>10,.0f}")
print(f"LP, no cycling cost:             ${total_no:>10,.0f}")
print(f"LP, with $46.30/MWh cycling cost:${total_cc:>10,.0f}")
print(f"Days the LP chose to cycle:      {days_active_cc} of {len(bt)}")
print(f"Avg daily revenue (no cost):     ${total_no/len(bt):>10,.0f}")
print(f"LP / back-of-envelope ratio:     {total_no/backenv_total:.2f}x")

# Save and visualize
bt.to_csv("backtest_results.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(range(len(bt)), bt["rev_no_cost"],   color="C0", alpha=0.6, label="No cycling cost")
ax.bar(range(len(bt)), bt["rev_with_cost"], color="C3", alpha=0.9, label="$46.30/MWh cycling cost")
ax.set_xlabel("Day index (chronological)")
ax.set_ylabel("Daily LP revenue ($)")
ax.set_title("Perfect-foresight arbitrage — CAISO NP15 — 30 days")
ax.legend()
plt.tight_layout()
plt.savefig("backtest.png", dpi=140)
plt.show()