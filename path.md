# Energy Trading — 30-Day Mastery Path (BESS + Autobidder Track)

> **Target role:** Energy trading / quant / data-eng internship at a BESS-focused autobidder company.
> **Stack you must match:** Python · FastAPI · async services · REST/JSON · PyTorch · scikit-learn · time-series forecasting · AWS RDS · S3 · crawlers · ETL · Docker · GitHub Actions · QA automation · React/TypeScript/Plotly (light).
> **Pace:** 5–8 hrs/day · 30 days · complete beginner → interview-ready.
> **North star:** By Day 30 you can (1) explain how a battery makes money in a wholesale power market, (2) crawl + clean an ISO data feed, (3) train a price-forecast model, (4) write a MILP/heuristic bidder that closes the loop from signal → executed bid, and (5) talk about all of it like an engineer who has shipped it.

---

## How this learning loop works

Every session follows the same rhythm:

1. **You** open the conversation and say "let's continue" (or "Day N").
2. **Claude** reads `path.md` (this file) and `progress.md` to see where you are.
3. **Claude teaches** that day's lesson — concepts first, then a hands-on exercise, then a quick check.
4. **You** do the exercise; Claude reviews, answers questions, pushes back where you're shaky.
5. **Claude** updates `progress.md` with what was covered, what stuck, and what to revisit.

If a day feels too heavy, we split it. If it feels easy, we add a stretch goal. The plan is a scaffold, not a cage.

---

## The four-week arc

| Week | Theme | Output by end of week |
|---|---|---|
| 1 | Power-market & trading fundamentals | You can explain LMP, DA vs RT, unit commitment, and what a "bid" actually is. |
| 2 | BESS economics & bidding strategy | You can value-stack a battery across energy arbitrage + ancillary services and explain ERCOT/CAISO/PJM differences. |
| 3 | Data + ML stack (the company's tools) | You have a working pipeline: ISO crawler → S3/RDS → FastAPI → price-forecast model. |
| 4 | Autobidder build + interview polish | You ship a mini-autobidder (forecast → optimize → bid → settle) and can talk about it crisply. |

---

# WEEK 1 — Foundations of Power Markets and Trading

**Goal:** by Friday, the words "day-ahead clear", "LMP", "ancillary", "settlement", "merit order" sound obvious to you.

## Day 1 — What is electricity trading, really?
- **Concepts:** Why electricity is a weird commodity (non-storable historically, instantaneous balance, transmission constraints). Vertically integrated utility vs. deregulated market. Wholesale vs. retail. The role of the ISO/RTO.
- **The seven US ISOs:** PJM, MISO, ERCOT, CAISO, SPP, NYISO, ISO-NE — what region, what's distinctive about each.
- **Key terms to nail today:** generator, load, scheduler, ISO, balancing authority, congestion, marginal unit.
- **Exercise:** Draw (on paper) the supply/demand curve of an electricity market. Mark where the marginal generator sets the price. Send Claude a photo or describe it.
- **Stretch:** Read the EIA's "How electricity is delivered to consumers" overview. Summarize in 5 bullets.

## Day 2 — Day-Ahead vs. Real-Time markets, and Locational Marginal Pricing (LMP)
- **Concepts:** The two-settlement system. Why DA exists (financial commitment) and why RT exists (physical balance). Virtual / INC-DEC trading.
- **LMP decomposition:** `LMP = System Energy Price + Congestion Cost + Marginal Loss Cost`. Why a node 50 miles away can be $200/MWh different.
- **The clearing process:** participants submit bids/offers → ISO runs Security-Constrained Unit Commitment (SCUC, day-ahead) and Security-Constrained Economic Dispatch (SCED, real-time) → uniform-price auction clears.
- **Exercise:** Pull yesterday's hourly DA LMPs for ERCOT hub HB_HOUSTON and the corresponding RT 5-min prices. Plot both. Where did they diverge? Why do you think?
- **Tooling intro:** install Python 3.11+, pandas, matplotlib, requests. Set up a scratch repo `energy-trading-30d/`.

## Day 3 — Bids, offers, and the merit-order stack
- **Concepts:** **What a bid actually looks like.** A generator submits an offer curve: "I'll produce 0–50 MW at $20, 50–100 MW at $35, 100–150 MW at $80." Loads submit demand bids. The ISO stacks them and clears at the marginal price.
- **Bid types:** energy bid (price-quantity pairs), self-schedule, virtual/INC-DEC, ancillary-service bid. Min/max output, ramp rates, min-up/min-down constraints.
- **Gate closure** and bid-modification rules. Why you can't change your mind 3 minutes before the hour.
- **Exercise:** Given a toy stack of 5 generators and a load forecast of 4,200 MW, find the clearing price and dispatch by hand. Then write a 30-line Python function that does it.
- **Stretch:** Read [Yes Energy — How Power Trading Works (DA Virtual Trades)](https://www.yesenergy.com/blog/how-power-trading-works) and write down 3 strategies a virtual trader uses.

## Day 4 — Ancillary services and capacity markets
- **Concepts:** Why ancillary exists (reliability, not energy). The product set: Regulation Up/Down, Spinning Reserve, Non-Spinning Reserve, Frequency Response, Black Start.
- **Pay-for-performance** (PJM RegD) vs. capacity-only payments. Mileage. Performance score.
- **Capacity markets** (PJM RPM, ISO-NE FCM, MISO PRA): paying generators to *exist* so the lights stay on in 3 years.
- **Exercise:** Build a one-page comparison table: ERCOT vs. CAISO vs. PJM — what AS products exist, how they're paid, and which one currently pays the most for a 4-hour battery.
- **Reading:** [Modo — ERCOT Ancillary Services beginner's guide](https://modoenergy.com/research/ercot-ancillary-services-explainer) and [Modo — PJM Regulation payments explainer](https://modoenergy.com/research/en/pjm-regulation-payments-explainer-ancillary-services-how-to-guide-battery-energy-storage-revenues).

## Day 5 — Risk, hedging, settlement
- **Concepts:** P&L = MWh × (sale price − purchase price) − costs. Mark-to-market vs. settled cashflow. Imbalance penalties.
- **Hedging instruments:** futures (CME), forwards/PPAs, FTRs (Financial Transmission Rights), virtual bids.
- **The trader's dashboard:** position, exposure, VaR, expected revenue, realized vs. expected.
- **Exercise:** Given a battery dispatch schedule and DA + RT prices, compute the day's revenue and the imbalance cost. Decompose into "DA arbitrage" and "RT correction".
- **Weekly checkpoint with Claude:** vocabulary quiz (LMP, SCED, INC-DEC, RegD, FTR, mileage, gate closure, congestion, marginal loss, two-settlement). You should explain each in one sentence without looking.

## Day 6–7 — Catch-up + project sprint
- Re-read anything fuzzy.
- **Mini project (Sat–Sun, ~6 hrs total):** Build a Jupyter notebook that pulls 30 days of ERCOT DA prices for one hub, plots the daily price shape, and computes the average peak-vs-off-peak spread. This is your first piece of "real" trader analysis. Push it to GitHub.

---

# WEEK 2 — BESS Economics and Bidding Strategy

**Goal:** by Friday, you can sketch a battery's revenue stack on a napkin and explain *why* an autobidder beats a human at this.

## Day 8 — Why batteries? The physical asset
- **Concepts:** Lithium-ion chemistry basics (LFP vs. NMC), C-rate, round-trip efficiency (~85–92%), depth of discharge, augmentation, cycle life vs. calendar life. **Duration** matters: a 1MW/4MWh battery is a different product from a 1MW/2MWh one.
- **Degradation cost:** every cycle costs you $X of NPV. This becomes a *constraint* in your optimizer.
- **Exercise:** Given a 100 MW / 400 MWh battery with 90% RTE, $250/kWh capex, and 6,000-cycle warranty, compute the per-MWh "cycling cost" you'd add to your optimizer.

## Day 9 — Energy arbitrage: the simplest trade
- **Concepts:** Charge cheap, discharge expensive. Sounds easy — isn't, because (a) you have a finite tank, (b) tomorrow's prices are uncertain, (c) the tank dictates a state-of-charge trajectory.
- **Single-day perfect-foresight LP:** the textbook formulation. Decision variables: `charge_t`, `discharge_t`, `SOC_t`. Constraints: SOC bounds, power bounds, RTE. Objective: maximize `sum(price_t × discharge_t − price_t × charge_t)`.
- **Exercise:** Code this LP in Python with `pulp` or `cvxpy`. Run it on yesterday's DA prices. Plot the SOC curve. Notice it always charges at the lowest 4 hours and discharges at the highest 4 hours? That's the arbitrage signal.

## Day 10 — Multi-market revenue stacking
- **Concepts:** Real money is in *stacking* DA arbitrage + RT arbitrage + ancillary services. You bid your power capacity into multiple markets simultaneously, subject to physical co-optimization (you can't sell the same MW twice).
- **Co-optimization:** how the ISO clears energy + AS jointly. How *you* should bid into them jointly.
- **Case study read:** [Modo — ERCOT & CAISO BESS revenue stack June 2025](https://modoenergy.com/research/en/ercot-caiso-june-2025-revenue-stack-batteries-bess-energy-arbitrage-nodal-price-locational-marginal-price-transmission-congestion-price-spreads). Note how the stack mix shifted as AS markets saturated.
- **Exercise:** Extend yesterday's LP to also bid 20% of capacity into Regulation. Add an opportunity-cost term.

## Day 11 — Bidding strategy: price-taker vs. price-maker
- **Concepts:** Self-schedule (always run) vs. economic bid (only run if price clears). Bid curve construction. Risk-aware bidding: the bid you submit *commits* you; if RT diverges, you pay imbalance.
- **Look-ahead bidding:** the trick that separates pros from amateurs — you bid hour 14 with awareness of expected hours 15–24 prices, so you don't drain the battery too early.
- **Reading:** [Look-Ahead Bidding Strategy for Energy Storage](https://www.researchgate.net/publication/312670741_Look-Ahead_Bidding_Strategy_for_Energy_Storage).
- **Exercise:** Implement a simple rolling-horizon LP: every hour, re-solve a 24-hour optimization using updated forecasts. Compare to single-shot.

## Day 12 — Forecasting uncertainty and robust bidding
- **Concepts:** Point forecasts lie. You need a *distribution* of prices. Quantile regression, scenario generation, robust optimization, CVaR (Conditional Value at Risk).
- **Why this matters for bidding:** a robust bid hedges against forecast error so a single bad forecast doesn't blow up the day.
- **Reading:** [Robust BESS bidding in DA + RT](https://www.sciencedirect.com/science/article/abs/pii/S2352152X22025099).
- **Exercise:** Generate 100 price-path scenarios (bootstrap from history). Solve a stochastic LP that maximizes expected revenue subject to a 5% CVaR constraint. Compare to the deterministic solution.

## Day 13 — The Tesla Autobidder mental model
- **Concepts:** Read the [Tesla Autobidder job posting](https://talents.vaia.com/companies/tesla-motors-inc/staff-quantitative-energy-trading-meteorologist-autobidder-33533481/) and reverse-engineer the architecture. They mention: continuous price forecasting, market-trend analysis, re-optimization, "physical dispatch and market trading strategies". $420M+ in trading profit.
- **The closed loop:** weather → load forecast → price forecast → bid optimization → submit bids to ISO → execute physical dispatch → settle → measure → retrain. This is what your company means by "Tesla-Autopilot-style automated trading."
- **Exercise:** Draw the system diagram for an autobidder. Label every component, every data feed, every decision frequency. Send Claude.

## Day 14 — Week 2 project sprint
- **Mini project (~6–8 hrs):** Build a "perfect-foresight back-tester" in Python. Input: a year of hourly DA prices for an ERCOT hub. Battery: 100 MW / 400 MWh. Output: total revenue, daily revenue distribution, capacity factor. This is your **baseline** — every model you build later must beat or match this.

---

# WEEK 3 — Code and Models: Build the Company's Stack

**Goal:** by Friday, you have a working data pipeline and a price-forecast model that beats naive baselines.

## Day 15 — Python for energy data: pandas, datetime, time zones
- **Concepts:** Hourly time series, DST gotchas (spring forward = 23 hours), UTC vs. local prevailing. Resampling, rolling windows, lag features.
- **Exercise:** Take a year of 5-min ERCOT RT prices, resample to hourly, compute (a) hourly mean, (b) intra-hour volatility, (c) daily peak hour. Handle DST correctly.

## Day 16 — Web crawling and ISO public APIs
- **Concepts:** ISO data sources: ERCOT MIS, CAISO OASIS, PJM Data Miner, MISO Market Reports, EIA-930. Rate limits, auth, pagination, retries with backoff.
- **Tools:** `requests`, `httpx` (async), `tenacity` for retries, `aiohttp` for parallel pulls.
- **Exercise:** Write an async crawler that pulls 30 days of ERCOT DA hourly LMPs for 5 hubs in parallel. Save raw JSON to `./raw/`, parsed CSV to `./clean/`.

## Day 17 — AWS S3 + RDS for storage
- **Concepts:** S3 = cheap object store for raw + parquet historical. RDS Postgres = OLTP for "current state" (positions, latest forecasts, bid log). The split: **landing → bronze (raw S3) → silver (cleaned parquet S3) → gold (RDS for serving)**.
- **Tools:** `boto3`, `psycopg2`/`asyncpg`, `sqlalchemy`, `pyarrow`.
- **Exercise:** Set up a free-tier AWS account. Create an S3 bucket and a tiny RDS Postgres. Push yesterday's crawled data to S3. Load the cleaned hourly summary into a `prices` Postgres table.
- **Important:** Do this with IAM roles and least-privilege; don't paste keys.

## Day 18 — FastAPI: serve the data
- **Concepts:** Why FastAPI: async, Pydantic models = free input/output validation, auto OpenAPI docs. The pattern in trading shops: every model and every dataset is a service behind a REST endpoint, so the bidder, the dashboard, and the back-test all read from the same source of truth.
- **Exercise:** Build a FastAPI service with three endpoints:
  - `GET /prices/{iso}/{hub}?start=...&end=...` returns hourly LMPs.
  - `GET /forecast/{iso}/{hub}?horizon=24` returns the latest 24-hour forecast (mock for now).
  - `POST /bids` accepts a bid payload and stores it in RDS.
- **Stretch:** Containerize with Docker. Add health/ready endpoints. Write 5 pytest tests.

## Day 19 — Time-series forecasting: classical baselines
- **Concepts:** Always start with baselines: persistence ("tomorrow = today"), seasonal-naive ("this hour next week = this hour last week"), AR/ARIMA, Prophet. Metrics: MAE, RMSE, MAPE, sMAPE. Why MAPE breaks near zero prices.
- **Train/val/test:** for time series, *never* shuffle. Walk-forward CV.
- **Exercise:** Predict next-day hourly DA prices using seasonal-naive and ARIMA. Score with MAE on a 30-day holdout.

## Day 20 — ML forecasting: gradient boosting and features
- **Concepts:** XGBoost / LightGBM remain the workhorse for short-term price forecasts. Engineering: lags (1h, 24h, 168h), calendar (hour, day-of-week, holiday), weather (temperature, wind, solar), gas price, load forecast.
- **Exercise:** Build an XGBoost model that predicts hour-ahead RT price. Beat seasonal-naive by ≥10% on MAE.
- **Reading:** [Hybrid Stacking for Short-Term Price Forecasting](https://www.techrxiv.org/users/802208/articles/1235479/master/file/data/A_Hybrid_Stacking_Method_for_Short_Term_Price_Forecasting_in_Electricity_Trading_Market-techrxiv/A_Hybrid_Stacking_Method_for_Short_Term_Price_Forecasting_in_Electricity_Trading_Market-techrxiv.pdf).

## Day 21 — Deep learning: PyTorch LSTM for prices
- **Concepts:** When DL helps (long sequences, multivariate, lots of data) and when it doesn't (small data, noisy regimes). LSTM/GRU vs. Transformer vs. Temporal Fusion Transformer. Quantile loss for distributional forecasts.
- **Exercise:** Train a small PyTorch LSTM on hourly prices + load + temperature. Output a *quantile* forecast (P10, P50, P90), not just a point.
- **Project sprint (Sun):** Wire the forecast model behind your FastAPI `/forecast` endpoint. Now your stack is: crawler → S3 → cleaning → RDS → FastAPI → ML model → REST forecast.

---

# WEEK 4 — Autobidder, Capstone, and Interview Polish

**Goal:** by Day 30, you ship an autobidder demo and can talk about it for 20 minutes without notes.

## Day 22 — MILP for bid optimization
- **Concepts:** Why MILP (binaries for on/off, integer for discrete bid blocks). Formulation: variables, constraints (SOC dynamics, power bounds, RTE, AS coupling), objective (revenue − cycling cost − imbalance penalty).
- **Tools:** `pulp` (free), `pyomo` (more flexible), commercial solvers (Gurobi, CPLEX) — academic/free tiers exist.
- **Reading:** [nAG — Optimizing BESS with MILP](https://nag.com/insights/optimize-battery-energy-storage-milp/).
- **Exercise:** Write a 24-hour MILP for a 100MW/400MWh battery co-optimizing energy + Regulation. Solve with pulp.

## Day 23 — Rolling/receding-horizon control
- **Concepts:** You don't solve once a day; you re-solve every 5–15 minutes as new info arrives. Receding-horizon / Model Predictive Control. Why this is the right framing for a real-time autobidder.
- **Exercise:** Wrap yesterday's MILP in a loop: at each hour, take the latest forecast (from your FastAPI endpoint), re-solve the next 24 hours, commit only the *next* hour's actions, advance.

## Day 24 — Putting it together: end-to-end autobidder backtest
- **Capstone build (full day):** Pipeline: historical price + load + weather → forecast model → rolling-horizon MILP → simulated bid execution → simulated settlement → P&L log.
- Compare three policies:
  1. **Naive:** charge at fixed hours 02–06, discharge 17–21.
  2. **DA-only LP** with point forecasts.
  3. **Rolling MILP** with quantile forecasts and CVaR.
- Score each on annual revenue and worst-week revenue.

## Day 25 — Production-ish polish
- **Concepts:** Logging (structured JSON), monitoring, alerting on stale data, idempotent retries, schema migrations, secret management.
- **CI/CD:** GitHub Actions to run pytest + ruff + mypy on every PR. Build & push Docker image on tag.
- **Exercise:** Add a GH Actions workflow. Add 1 alert: "if no new prices arrived in the last 30 min, log ERROR."

## Day 26 — Light frontend for the dashboard
- **Concepts:** What a trader's screen looks like: SOC over time, forecast vs. actual, today's bid vs. cleared, P&L. Why your company uses React/TypeScript/Plotly — lightweight, browser-native interactivity.
- **Exercise:** Build a single-page React (or Streamlit if you're tight on time) dashboard reading from your FastAPI. Three panels: live price chart (Plotly), SOC trajectory, today's bid table.

## Day 27 — Industry context: who's who, where the market is going
- **Read & summarize (1 page each):**
  - [McKinsey — Winning strategies for BESS](https://www.mckinsey.com/industries/industrials/our-insights/powering-the-future-strategies-for-battery-energy-storage-developers).
  - [Wartsila — 2026 energy storage outlook](https://www.wartsila.com/insights/article/2026-energy-storage-outlook-and-opportunities).
  - [Modo — US BESS Q3 2025 roundup](https://modoenergy.com/research/en/ercot-pjm-caiso-nyiso-us-bess-research-roundup-q3-2025).
- **The competitive landscape:** Tesla Autobidder, Fluence Mosaic, Gridmatic, Habitat Energy, Tyba, Modo (data), Ascend Analytics. Understand who does what.

## Day 28 — Interview prep: technical
- **Topics to be ready for:**
  - Walk through your autobidder repo. Explain every architecture choice.
  - "How would you bid a 100MW/200MWh battery in ERCOT next week?" (talk through DA + RT + AS allocation).
  - "Your forecast says price will be $300 at 6pm. What's your bid?" (bid curve, not single price).
  - "Your model is 20% off on a hot day. What do you do?" (online retraining, regime detection, fallback policies).
  - SQL: write a query for "hours where RT price > 2× DA price for this hub last 30 days".
  - Python: implement a streaming z-score detector.
- **Mock interview with Claude.**

## Day 29 — Interview prep: behavioral + market view
- **Stories to have ready (STAR format):** the autobidder build, a hard bug, a tradeoff you made.
- **Hot-take questions:** "Where will BESS revenues come from in 2030?" "Is virtual trading dead in PJM?" "What's the main risk in autobidding?" Have a sharp opinion backed by numbers.
- **Send out applications.**

## Day 30 — Demo day
- Record a 5-minute Loom walking through your repo. Push a clean README. Pin the repo on your GitHub.
- **Final checkpoint with Claude:** what landed, what to keep practicing, what to revisit in week 5+.

---

## What to keep doing after Day 30

- One paper a week from arXiv (energy + ML).
- Watch ERCOT real-time scarcity events when they happen — your gut for price behavior comes from screen-time, not books.
- Re-run your backtest monthly with new data; confirm nothing has rotted.
- Contribute one PR to a public energy-data tool (e.g., `gridstatus`, `ercot-api`).

---

## Curated reading list (don't try to read it all up front)

- **Books / long-form**
  - "Energy Trading and Risk Management" — Iris Marie Mack
  - Stoft, *Power System Economics* — for the theory
- **Industry research (free, current)**
  - Modo Energy research blog — best in class for BESS market data
  - Wood Mackenzie / Wartsila annual storage outlooks
  - Ascend Analytics blog
- **Code**
  - [`gridstatus`](https://github.com/gridstatus/gridstatus) — Python ISO data lib
  - [`pybroker`](https://github.com/edtechre/pybroker) — algo trading framework
  - [Stefan Jansen — ML for Trading](https://github.com/stefan-jansen/machine-learning-for-trading) — reference for finance+ML patterns
- **Papers** — see links inline above.
- **Interview**
  - [10 Questions for an Energy Market Job Interview](https://medium.com/the-megawatts/10-questions-you-must-prepare-for-an-energy-market-job-interview-df8ec5796436)

---

*Plan generated 2026-05-05. Adjust as you go — the loop is the thing, not the schedule.*
