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