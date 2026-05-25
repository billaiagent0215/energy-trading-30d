"""
Day 12 — Stochastic LP with CVaR constraint.

Extends Day 10's stacking LP by:
  - Generating K price scenarios from a base forecast + Gaussian noise
  - Committing to ONE schedule (c, d, s, r) before uncertainty resolves
  - Adding the Rockafellar-Uryasev CVaR LP reformulation
  - Constraining CVaR_5% >= CVAR_FLOOR

Compare against the deterministic LP run on the noise-free base prices.
The gap = the "insurance premium" you pay for tail protection.
"""

import numpy as np
import pulp

# ---------- Battery & market parameters ----------
P_MAX = 100              # MW (power rating)
E_MAX = 400              # MWh (energy rating)
RTE = 0.85               # round-trip efficiency
S_0 = 200                # initial SOC (MWh)
T = 24                   # hourly day-ahead horizon
CYCLING_COST = 0.0       # $/MWh discharged (set 0 to isolate CVaR effect)
REG_RES_HOURS = 0.5      # SOC headroom per MW of regulation

# ---------- Scenario / CVaR parameters ----------
K = 50                   # number of price scenarios
NOISE_STD = 0.15         # multiplicative noise (15%)
ALPHA = 0.05             # tail probability (worst 5%)
CVAR_FLOOR = 0.0         # require avg of worst 5% >= $0

# ---------- Base prices (a realistic CAISO-shaped day) ----------
base_prices = np.array([
    25, 22, 20, 19, 21, 28, 45, 55, 50, 42, 38, 35,
    33, 32, 35, 40, 55, 75, 85, 70, 55, 45, 35, 28
], dtype=float)
base_reg = np.full(T, 15.0)  # flat regulation price

np.random.seed(42)
# K x T matrix of price scenarios: each scenario gets independent multiplicative noise
scenarios = base_prices[None, :] * (1 + np.random.normal(0, NOISE_STD, size=(K, T)))
scenarios = np.maximum(scenarios, 0.0)  # floor at $0 (no negative prices today)


# ============================================================
# Stochastic LP with CVaR constraint
# ============================================================
def solve_stochastic(scenarios, reg_prices, cvar_floor=CVAR_FLOOR, alpha=ALPHA):
    Ks, T = scenarios.shape
    m = pulp.LpProblem("stochastic_bess", pulp.LpMaximize)

    # Single schedule committed before uncertainty resolves
    c = [pulp.LpVariable(f"c_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    d = [pulp.LpVariable(f"d_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    s = [pulp.LpVariable(f"s_{t}", lowBound=0, upBound=E_MAX) for t in range(T)]
    r = [pulp.LpVariable(f"r_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]

    # Physics — same across all scenarios
    for t in range(T):
        prev = S_0 if t == 0 else s[t-1]
        m += s[t] == prev + RTE * c[t] - d[t]
        m += c[t] + r[t] <= P_MAX
        m += d[t] + r[t] <= P_MAX
        m += prev >= REG_RES_HOURS * r[t]
        m += prev <= E_MAX - REG_RES_HOURS * r[t]
    m += s[T-1] >= S_0  # end-of-day SOC

    # Revenue per scenario (linear in decision vars)
    R = []
    for k in range(Ks):
        rev_k = pulp.lpSum(
            scenarios[k, t] * d[t] - scenarios[k, t] * c[t]
            + reg_prices[t] * r[t] - CYCLING_COST * d[t]
            for t in range(T)
        )
        R.append(rev_k)

    # Rockafellar-Uryasev CVaR LP reformulation
    eta = pulp.LpVariable("eta")                            # will equal VaR at optimum
    u = [pulp.LpVariable(f"u_{k}", lowBound=0) for k in range(Ks)]
    for k in range(Ks):
        m += u[k] >= eta - R[k]                             # slack below VaR

    # CVaR_alpha = eta - (1/(alpha*K)) * sum(u_k) >= floor
    m += eta - (1.0 / (alpha * Ks)) * pulp.lpSum(u) >= cvar_floor

    # Objective: maximize expected revenue
    m += (1.0 / Ks) * pulp.lpSum(R)

    m.solve(pulp.PULP_CBC_CMD(msg=False))

    sched = {
        "c": [pulp.value(x) for x in c],
        "d": [pulp.value(x) for x in d],
        "s": [pulp.value(x) for x in s],
        "r": [pulp.value(x) for x in r],
    }
    realized = sorted([pulp.value(R[k]) for k in range(Ks)])
    n_tail = max(1, int(alpha * Ks))
    cvar = sum(realized[:n_tail]) / n_tail
    expected = sum(realized) / Ks
    return {
        "expected": expected,
        "cvar": cvar,
        "var_eta": pulp.value(eta),
        "worst": realized[0],
        "best": realized[-1],
        "schedule": sched,
        "realized": realized,
        "status": pulp.LpStatus[m.status],
    }


# ============================================================
# Deterministic LP (same as Day 10) on base prices
# ============================================================
def solve_deterministic(prices, reg_prices):
    T = len(prices)
    m = pulp.LpProblem("det_bess", pulp.LpMaximize)
    c = [pulp.LpVariable(f"cd_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    d = [pulp.LpVariable(f"dd_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    s = [pulp.LpVariable(f"sd_{t}", lowBound=0, upBound=E_MAX) for t in range(T)]
    r = [pulp.LpVariable(f"rd_{t}", lowBound=0, upBound=P_MAX) for t in range(T)]
    for t in range(T):
        prev = S_0 if t == 0 else s[t-1]
        m += s[t] == prev + RTE * c[t] - d[t]
        m += c[t] + r[t] <= P_MAX
        m += d[t] + r[t] <= P_MAX
        m += prev >= REG_RES_HOURS * r[t]
        m += prev <= E_MAX - REG_RES_HOURS * r[t]
    m += s[T-1] >= S_0
    m += pulp.lpSum(prices[t]*d[t] - prices[t]*c[t] + reg_prices[t]*r[t]
                    - CYCLING_COST*d[t] for t in range(T))
    m.solve(pulp.PULP_CBC_CMD(msg=False))
    return pulp.value(m.objective)


# ============================================================
# Run and report
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(f"Day 12 — Stochastic LP with CVaR ({int(ALPHA*100)}%) constraint")
    print("=" * 60)
    print(f"K = {K} scenarios, noise std = {NOISE_STD*100:.0f}%, "
          f"CVaR floor = ${CVAR_FLOOR}")
    print()

    det_rev = solve_deterministic(base_prices, base_reg)

    # --- Run 1: CVaR floor = $0 ---
    out0 = solve_stochastic(scenarios, base_reg, cvar_floor=0.0)

    # --- Run 2: CVaR floor = $1,000 (tighter) ---
    out1 = solve_stochastic(scenarios, base_reg, cvar_floor=1000.0)

    # --- Run 3: collapse-to-deterministic sanity check ---
    single = base_prices[None, :]  # K=1 scenario = base prices, no noise
    out_sanity = solve_stochastic(single, base_reg, cvar_floor=-1e9, alpha=1.0)

    print(f"Deterministic LP (no noise):          ${det_rev:>10,.2f}")
    print("-" * 60)
    print(f"Stochastic LP, CVaR_5% floor = $0:")
    print(f"   Status:                            {out0['status']}")
    print(f"   Expected revenue:                  ${out0['expected']:>10,.2f}")
    print(f"   Worst scenario:                    ${out0['worst']:>10,.2f}")
    print(f"   Best scenario:                     ${out0['best']:>10,.2f}")
    print(f"   VaR_5% (eta):                      ${out0['var_eta']:>10,.2f}")
    print(f"   CVaR_5%:                           ${out0['cvar']:>10,.2f}")
    print(f"   Insurance premium (det - E[stoch]):${det_rev - out0['expected']:>10,.2f}")
    print("-" * 60)
    print(f"Stochastic LP, CVaR_5% floor = $1,000 (tighter):")
    print(f"   Status:                            {out1['status']}")
    print(f"   Expected revenue:                  ${out1['expected']:>10,.2f}")
    print(f"   CVaR_5%:                           ${out1['cvar']:>10,.2f}")
    print(f"   Premium over deterministic:        ${det_rev - out1['expected']:>10,.2f}")
    print("-" * 60)
    print(f"Sanity check (K=1, alpha=1.0):")
    print(f"   Expected revenue:                  ${out_sanity['expected']:>10,.2f}")
    print(f"   (Should match deterministic LP    = ${det_rev:>10,.2f})")
    print("=" * 60)
