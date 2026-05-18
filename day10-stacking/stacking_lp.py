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
def solve_day(prices, reg_prices, P_max=100, E_max=400, RTE=0.90, S_0=0,
              cycling_cost=0.0, reg_reservation_hours=0.25):
    """
    Single-day battery LP co-optimizing energy + Regulation.
    Returns a dict with revenue breakdown and schedules.
    """
    T = len(prices)
    model = pulp.LpProblem("battery_stacking", pulp.LpMaximize)

    c = [pulp.LpVariable(f"c_{t}", lowBound=0, upBound=P_max) for t in range(T)]
    d = [pulp.LpVariable(f"d_{t}", lowBound=0, upBound=P_max) for t in range(T)]
    r = [pulp.LpVariable(f"r_{t}", lowBound=0, upBound=P_max) for t in range(T)]
    s = [pulp.LpVariable(f"s_{t}", lowBound=0, upBound=E_max) for t in range(T)]

    # Objective: energy revenue + reg revenue − cycling cost
    model += pulp.lpSum(
          prices[t] * d[t]
        - prices[t] * c[t]
        + reg_prices[t] * r[t]
        - cycling_cost * d[t]
        for t in range(T)
    )

    for t in range(T):
        prev = S_0 if t == 0 else s[t-1]
        # SOC dynamics
        model += s[t] == prev + RTE * c[t] - d[t]
        # Power-budget: Reg shares the 100 MW with charge/discharge
        model += c[t] + r[t] <= P_max
        model += d[t] + r[t] <= P_max
        # SOC headroom for potential Reg deployment
        model += prev >= reg_reservation_hours * r[t]
        model += prev <= E_max - reg_reservation_hours * r[t]

    model += s[T-1] >= S_0  # end-of-day balance

    model.solve(pulp.PULP_CBC_CMD(msg=0))

    cv = [pulp.value(c[t]) for t in range(T)]
    dv = [pulp.value(d[t]) for t in range(T)]
    rv = [pulp.value(r[t]) for t in range(T)]
    sv = [pulp.value(s[t]) for t in range(T)]

    energy_rev = sum(prices[t] * dv[t] - prices[t] * cv[t] for t in range(T))
    reg_rev    = sum(reg_prices[t] * rv[t] for t in range(T))

    return {
        "total":      pulp.value(model.objective),
        "energy":     energy_rev,
        "reg":        reg_rev,
        "cycle_cost": cycling_cost * sum(dv),
        "charge":     cv,
        "discharge":  dv,
        "reg_sched":  rv,
        "soc":        sv,
    }


# ---------- 4. SINGLE-DAY COMPARISON ---------------------------------------
REG_PRICE_FLAT = 50.0
reg_flat = [REG_PRICE_FLAT] * 24
reg_zero = [0.0] * 24

arb_only = solve_day(prices, reg_zero, cycling_cost=46.30)
stacked  = solve_day(prices, reg_flat, cycling_cost=46.30)

print(f"\n{'Scenario':<26}{'Total':>12}{'Energy':>12}{'Reg':>12}")
print(f"{'-'*62}")
print(f"{'Arbitrage only':<26}${arb_only['total']:>11,.2f}"
      f"${arb_only['energy']:>11,.2f}${arb_only['reg']:>11,.2f}")
print(f"{'Stacked (energy + Reg)':<26}${stacked['total']:>11,.2f}"
      f"${stacked['energy']:>11,.2f}${stacked['reg']:>11,.2f}")

uplift_abs = stacked['total'] - arb_only['total']
uplift_pct = uplift_abs / max(arb_only['total'], 1)
print(f"\nStacking uplift on this day: ${uplift_abs:,.2f} ({uplift_pct:.0%})")


# ---------- 5. 30-DAY BACKTEST ---------------------------------------------
totals = {"arb_only": 0, "stk_total": 0, "stk_energy": 0, "stk_reg": 0}
for date_val, day_df in df.groupby("date"):
    day_prices = day_df.sort_values("hour")["LMP"].tolist()
    if len(day_prices) != 24:
        continue
    r_arb = solve_day(day_prices, reg_zero, cycling_cost=46.30)
    r_stk = solve_day(day_prices, reg_flat, cycling_cost=46.30)
    totals["arb_only"]  += r_arb["total"]
    totals["stk_total"] += r_stk["total"]
    totals["stk_energy"] += r_stk["energy"]
    totals["stk_reg"]   += r_stk["reg"]

print(f"\n{'='*60}")
print(f"30-DAY STACKING BACKTEST — CAISO NP15 (May), Reg @ $10/MW-h")
print(f"{'='*60}")
print(f"Arbitrage-only revenue:    ${totals['arb_only']:>10,.0f}")
print(f"Stacked revenue (total):   ${totals['stk_total']:>10,.0f}")
print(f"   from energy:            ${totals['stk_energy']:>10,.0f}")
print(f"   from regulation:        ${totals['stk_reg']:>10,.0f}")
print(f"Stacking uplift:           ${totals['stk_total'] - totals['arb_only']:>10,.0f}"
      f"  ({(totals['stk_total']-totals['arb_only'])/max(totals['arb_only'],1):.1%})")