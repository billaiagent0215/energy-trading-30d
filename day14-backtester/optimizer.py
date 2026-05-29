"""
Layer 4: single-day perfect-foresight arbitrage LP.

Lightly refactored from Day 9's arbitrage_lp.py to expose a clean
solve_day(prices, **params) interface for the backtest loop.
"""

import numpy as np
import pulp


# ---------- Default battery parameters ----------
DEFAULT_PARAMS = dict(
    P_MAX=100,             # MW (power rating)
    E_MAX=400,             # MWh (energy rating)
    RTE=0.85,              # round-trip efficiency
    S_0=200,               # initial SOC in MWh (50% — neutral start)
    CYCLING_COST=46.30,    # $/MWh discharged (Day 8 calculation)
)


def solve_day(prices, **overrides):
    """
    Solve a 24-hour perfect-foresight arbitrage LP.

    Args:
        prices: array-like of length 24, hourly LMPs in $/MWh
        overrides: any of P_MAX, E_MAX, RTE, S_0, CYCLING_COST

    Returns:
        dict with:
            revenue:    total daily revenue in $ (gross arbitrage minus cycling cost)
            gross:      gross arbitrage revenue before cycling cost
            cycling:    total cycling cost charged
            cycles:     equivalent full cycles for the day (discharged MWh / E_MAX)
            charge:     list of 24 charge MW values
            discharge:  list of 24 discharge MW values
            soc:        list of 24 end-of-hour SOC MWh values
            status:     solver status string
    """
    p = dict(DEFAULT_PARAMS)
    p.update(overrides)
    P_MAX, E_MAX, RTE = p["P_MAX"], p["E_MAX"], p["RTE"]
    S_0, CYCLING_COST = p["S_0"], p["CYCLING_COST"]

    prices = np.asarray(prices, dtype=float)
    T = len(prices)
    assert T == 24, f"Expected 24 hourly prices, got {T}"

    m = pulp.LpProblem("arbitrage", pulp.LpMaximize)
    c = [pulp.LpVariable(f"c_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    d = [pulp.LpVariable(f"d_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    s = [pulp.LpVariable(f"s_{t}", lowBound=0, upBound=E_MAX) for t in range(T)]

    for t in range(T):
        prev = S_0 if t == 0 else s[t-1]
        m += s[t] == prev + RTE * c[t] - d[t]
    m += s[T-1] >= S_0  # end-of-day SOC ≥ start

    m += pulp.lpSum(prices[t]*d[t] - prices[t]*c[t] - CYCLING_COST*d[t]
                    for t in range(T))

    m.solve(pulp.PULP_CBC_CMD(msg=False))

    charge = [pulp.value(x) or 0.0 for x in c]
    discharge = [pulp.value(x) or 0.0 for x in d]
    soc = [pulp.value(x) or 0.0 for x in s]
    total_discharged = sum(discharge)
    gross = sum(prices[t] * (discharge[t] - charge[t]) for t in range(T))
    cycling = CYCLING_COST * total_discharged

    return {
        "revenue": gross - cycling,
        "gross": gross,
        "cycling": cycling,
        "cycles": total_discharged / E_MAX,
        "charge": charge,
        "discharge": discharge,
        "soc": soc,
        "status": pulp.LpStatus[m.status],
    }


if __name__ == "__main__":
    # quick smoke test
    test_prices = [25, 22, 20, 19, 21, 28, 45, 55, 50, 42, 38, 35,
                   33, 32, 35, 40, 55, 75, 85, 70, 55, 45, 35, 28]
    out = solve_day(test_prices)
    print(f"Status:   {out['status']}")
    print(f"Revenue:  ${out['revenue']:,.2f}")
    print(f"Gross:    ${out['gross']:,.2f}")
    print(f"Cycling:  ${out['cycling']:,.2f}")
    print(f"Cycles:   {out['cycles']:.2f}")
