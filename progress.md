# Energy Trading — Progress Tracker

> Companion to `path.md`. Claude reads this file at the start of every session to know where you are. You and Claude both update it as you go.

---

## Quick status

- **Start date:** 2026-05-05
- **Target finish:** 2026-06-04 (Day 30)
- **Today's day number:** 1 complete → starting Day 2
- **Current week:** Week 1 — Foundations
- **Streak:** 1 day
- **Hours logged:** ~1
- **Next action:** Day 2 — Day-Ahead vs. Real-Time markets and LMP decomposition. Install Python 3.11+ and create the `energy-trading-30d/` repo before the data-pulling exercise.

---

## Open questions / things to revisit

*(Claude will add anything you stumbled on so we circle back.)*

- **Load vs. generator confusion (Day 1):** initially defined "load" as electricity generated. Corrected — load = demand/consumption. Re-tested at end of Day 1, answered correctly (charging battery = load). Watch for relapse.
- **Offer curve vs. supply stack (Day 1):** initially conflated the two. An *offer curve* is one resource's bid; the *supply stack / merit order* is everyone's curves aggregated. Re-test on Day 3 (merit-order exercise).
- **Marginal-unit partial dispatch (Day 1):** missed that the marginal unit is usually only *partially* dispatched (50 MW out of 100 MW capacity in the toy example). Got concept after correction. Reinforce when we do real ERCOT data on Day 2.
- **Producer-surplus units (Day 1):** wrote "$50" instead of $50/MWh × 100 MW = $5,000. Watch for unit slips on $/MWh × MW × hours.
- **Solar-clearing arithmetic (Day 1 vocab check):** wrote 50×80=$400 (off by 10x). Concept of uniform-price clearing was correct.

---

## Confidence self-rating (update weekly, 1–5)

| Topic | Wk0 | Wk1 | Wk2 | Wk3 | Wk4 |
|---|---|---|---|---|---|
| Power-market structure (ISOs, DA/RT, LMP) | 1 | – | – | – | – |
| Bidding mechanics (offer curves, gate closure, AS) | 1 | – | – | – | – |
| BESS economics (revenue stack, arbitrage, AS) | 1 | – | – | – | – |
| Python data pipelines (pandas, async, AWS) | 1 | – | – | – | – |
| FastAPI + REST service design | 1 | – | – | – | – |
| Time-series forecasting (classical + ML + DL) | 1 | – | – | – | – |
| MILP / optimization for bidding | 1 | – | – | – | – |
| End-to-end autobidder thinking | 1 | – | – | – | – |

---

## Daily log

> Format Claude will use for each day:
> ```
> ### Day N — YYYY-MM-DD — <topic>
> - Hours: X
> - Covered: …
> - Exercise result: …
> - Stuck on / to revisit: …
> - Stretch attempted? Y/N
> - Next-day prep: …
> ```

### Day 0 — 2026-05-05 — Kickoff
- Hours: ~0.5
- Covered: scoped the program (5–8 hrs/day, BESS focus, company-stack projects). Generated `path.md` and `progress.md`.
- Exercise result: n/a
- Stuck on / to revisit: n/a
- Next-day prep: skim Week 1 overview; install Python 3.11+ and create `energy-trading-30d/` repo before Day 2's tooling step.

### Day 1 — 2026-05-05 — What is electricity trading + what is bidding
- Hours: ~1
- Covered: why electricity is a weird commodity (non-storable, instantaneous balance, locational, time-granular, reliability as separate product). The cast: ISO/RTO, generators, load, traders, batteries-as-hybrids. Bidding = price-quantity *curves*, not single numbers. Offer curve, merit order, marginal unit, uniform-price clearing, two-settlement, gate closure. Producer/consumer surplus on a 5-generator merit-order exercise.
- Exercise result: identified marginal unit ($60 generator) and clearing price ($60) on first try. Refinements applied: marginal unit is partially dispatched (50 of 100 MW), and producer surplus needs unit-aware multiplication ($50/MWh × 100 MW = $5,000 per hour for the $10 generator).
- Vocab pulse-check: 4/7 solid (generator, marginal unit, gate closure once explained, congestion as preview), 2 needed correction (load, offer curve), 1 unknown (ISO).
- Re-test pulse-check: 3/3 conceptually correct; one arithmetic slip on solar-farm earnings ($400 → $4,000).
- Stuck on / to revisit: see Open questions section.
- Next-day prep: install Python 3.11+, pandas, matplotlib, requests; create `energy-trading-30d/` repo on GitHub before Day 2's data-pulling exercise.

---

## Weekly checkpoints

### Week 1 — Foundations of Power Markets

- [ ] Day 1: What is electricity trading
- [ ] Day 2: DA vs. RT and LMP decomposition
- [ ] Day 3: Bids, offers, merit-order stack
- [ ] Day 4: Ancillary services and capacity
- [ ] Day 5: Risk, hedging, settlement
- [ ] Day 6–7: Mini project — ERCOT 30-day price-shape notebook
- [ ] **Vocab check:** LMP, SCED, INC-DEC, RegD, FTR, mileage, gate closure, congestion, marginal loss, two-settlement
- [ ] **Output:** GitHub repo with first notebook

### Week 2 — BESS Economics and Bidding Strategy

- [ ] Day 8: Battery as a physical asset (RTE, duration, degradation)
- [ ] Day 9: Energy arbitrage LP (single-day perfect foresight)
- [ ] Day 10: Multi-market revenue stacking + co-optimization
- [ ] Day 11: Price-taker vs. price-maker bidding; look-ahead
- [ ] Day 12: Robust / stochastic bidding under uncertainty
- [ ] Day 13: Tesla Autobidder reverse-engineering — system diagram
- [ ] Day 14: Mini project — perfect-foresight backtester (1 yr, 1 hub)
- [ ] **Output:** Backtester repo with annual-revenue baseline number

### Week 3 — Code and Models (the company stack)

- [ ] Day 15: Pandas + time zones + DST gotchas
- [ ] Day 16: Async ISO crawler (ERCOT, 5 hubs)
- [ ] Day 17: AWS S3 + RDS landing → bronze → silver → gold
- [ ] Day 18: FastAPI service with `/prices`, `/forecast`, `/bids`
- [ ] Day 19: Classical forecasting baselines (persistence, ARIMA)
- [ ] Day 20: XGBoost forecast that beats baselines by ≥10% MAE
- [ ] Day 21: PyTorch LSTM with quantile output, wired into FastAPI
- [ ] **Output:** Crawler → S3 → RDS → FastAPI → ML forecast pipeline

### Week 4 — Autobidder and Polish

- [ ] Day 22: 24-hour MILP for energy + Regulation co-optimization
- [ ] Day 23: Rolling-horizon MPC wrapper around the MILP
- [ ] Day 24: End-to-end backtest comparing 3 policies
- [ ] Day 25: GH Actions CI, structured logging, alert on stale data
- [ ] Day 26: React/Plotly (or Streamlit) dashboard
- [ ] Day 27: Industry context — McKinsey/Wartsila/Modo reads
- [ ] Day 28: Technical mock interview with Claude
- [ ] Day 29: Behavioral + hot-takes prep; applications sent
- [ ] Day 30: Demo Loom + clean README + pinned repo
- [ ] **Output:** Public autobidder repo with README, tests, CI badge, dashboard

---

## Project portfolio (filled in as you ship)

| # | Project | Repo / link | One-line outcome |
|---|---|---|---|
| 0 | Master repo (all 30 days) | https://github.com/billaiagent0215/energy-trading-30d | Initialized; venv at root, requirements.txt pinned |
| 1 | ERCOT 30-day price-shape notebook | _tbd_ | _tbd_ |
| 2 | Perfect-foresight backtester | _tbd_ | _tbd_ |
| 3 | Crawler → S3/RDS → FastAPI → forecast | _tbd_ | _tbd_ |
| 4 | Mini autobidder + dashboard (capstone) | _tbd_ | _tbd_ |

---

## Vocabulary (you should be able to define each in one sentence)

- [ ] ISO / RTO
- [ ] Locational Marginal Price (LMP)
- [ ] Day-ahead market (DAM)
- [ ] Real-time market (RTM)
- [ ] Two-settlement system
- [ ] SCUC / SCED
- [ ] Merit order / supply stack
- [ ] Bid curve / offer curve
- [ ] Gate closure
- [ ] Self-schedule
- [ ] INC / DEC (virtual bid)
- [ ] Ancillary services (Reg Up/Down, Spin, Non-spin)
- [ ] Frequency regulation / mileage / performance score
- [ ] Capacity market
- [ ] Financial Transmission Right (FTR)
- [ ] Round-trip efficiency (RTE)
- [ ] State of charge (SOC)
- [ ] Depth of discharge / cycle life
- [ ] Energy arbitrage
- [ ] Revenue stacking
- [ ] Co-optimization
- [ ] Look-ahead bidding
- [ ] Imbalance / make-whole payments
- [ ] CVaR / robust optimization
- [ ] MILP / receding horizon / MPC

---

## Reflection prompts (Claude will ask weekly)

1. What clicked this week that didn't last week?
2. What concept still feels hand-wavy?
3. Where did your code break? What did you learn from the bug?
4. If a recruiter called tomorrow, which bullet on your résumé could you defend most confidently? Least?

---

*This file is meant to be edited often. Don't be precious about it.*
