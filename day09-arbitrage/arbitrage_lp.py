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


# ---------- 3. BUILD THE LP -------------------------------------------------
model = pulp.LpProblem("battery_arbitrage", pulp.LpMaximize)

# Decision variables — one per hour for charge, discharge, SOC.
c = [pulp.LpVariable(f"charge_{t}",    lowBound=0, upBound=P_MAX) for t in range(T)]
d = [pulp.LpVariable(f"discharge_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
s = [pulp.LpVariable(f"soc_{t}",       lowBound=0, upBound=E_MAX) for t in range(T)]

# Objective: revenue = sum of (sold − bought).
model += pulp.lpSum(prices[t] * d[t] - prices[t] * c[t] for t in range(T))

# SOC dynamics constraints.
for t in range(T):
    prev = S_0 if t == 0 else s[t-1]
    model += s[t] == prev + RTE * c[t] - d[t], f"soc_dynamics_{t}"

# End-of-day SOC must be ≥ starting SOC (so we can repeat tomorrow).
model += s[T-1] >= S_0, "eod_soc_balance"


# ---------- 4. SOLVE --------------------------------------------------------
model.solve(pulp.PULP_CBC_CMD(msg=0))     # msg=0 silences the solver log
print(f"Solver status: {pulp.LpStatus[model.status]}")

charge_sched    = [pulp.value(c[t]) for t in range(T)]
discharge_sched = [pulp.value(d[t]) for t in range(T)]
soc_traj        = [pulp.value(s[t]) for t in range(T)]
revenue         = pulp.value(model.objective)

print(f"\nOptimal daily revenue: ${revenue:,.2f}")
print(f"Total charge:    {sum(charge_sched):>6.1f} MWh")
print(f"Total discharge: {sum(discharge_sched):>6.1f} MWh")
print(f"Implied RTE:     {sum(discharge_sched)/sum(charge_sched):>6.2%}")


# ---------- 5. VISUALIZE ----------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

ax1.bar(range(T), prices, color="lightgray", label="DA price")
ax1.set_ylabel("$/MWh")
ax1.legend(loc="upper left")
ax1b = ax1.twinx()
ax1b.bar(range(T), charge_sched,    color="C0", alpha=0.7, label="charge (MW)")
ax1b.bar(range(T), [-d for d in discharge_sched], color="C3", alpha=0.7,
         label="discharge (MW, plotted negative)")
ax1b.set_ylabel("MW (charge +, discharge −)")
ax1b.legend(loc="upper right")
ax1.set_title(f"CAISO NP15 — perfect-foresight arbitrage — {target_day}")

ax2.plot(range(T), soc_traj, "o-", color="C2")
ax2.fill_between(range(T), 0, soc_traj, alpha=0.2, color="C2")
ax2.set_ylabel("SOC (MWh)")
ax2.set_xlabel("Hour of day")
ax2.set_ylim(-10, E_MAX + 20)
ax2.set_xticks(range(0, 24, 2))
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("schedule.png", dpi=140)
plt.show()