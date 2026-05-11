### Exam for Day 4
## Description: Imagine you're advising a developer who has $50M to deploy a single 100 MW / 400 MWh battery and is choosing between PJM, ERCOT, and CAISO. You're going to build a one-page comparison table answering:

# Q1: Energy market structure — Hub locations, DA gate time, RT granularity.
Hub locations
PJM:Spread across 13 states
ERCOT:Texas
CAISO:California

DA gate time
PJM:10:30 AM(EPT)
ERCOT:10:00 AM(CPT)
CAISO:10:00 AM(PPT)

RT granularity
PJM:5 minutes
ERCOT:5 minutes
CAISO:5 minutes/15 minutes

# Q2: Ancillary product set offered — Which of {RegUp, RegDown, RegD-fast, Spin, Non-Spin} does the ISO have? Are RegUp and RegDown separate or co-optimized?
PJM:RegUp, RegDown, Spin, Non-Spin
ERCOT:RegUp, RegDown, Spin, Non-Spin
CAISO:RegUp, RegDown, Spin, Non-Spin

# Q3: Capacity market — Does it exist? Forward years? Approximate $/MW-year for batteries?
PJM:Yes, ~$120,100 / MW-year
ERCOT:No
CAISO:Yes, ~$84,000 to $120,000+ / MW-year

# Q4: 2025–2026 BESS revenue mix — What fraction of total BESS revenue came from energy arbitrage vs. AS vs. capacity? Use the Modo numbers above.
PJM:86% from regulation payments
ERCOT:87% from AS
CAISO:roughly 80% from DA

# Q5: The strategic punchline — In one sentence, why would a developer choose this ISO?
PJM, they have capacity market which is great for investing and AS price is not saturated yet

# Q6: Why is PJM RegD payment higher per MW than PJM Spin payment, even though Spin requires more sustained discharge?
Beacuse regulation up requires generator to supply the power much faster compare to spin.

# Q7: ERCOT doesn't have a capacity market. So how does ERCOT incentivize someone to build a new gas plant? (Hint: the energy market does double duty.)
ERCOT doesn't have capacity market. It incentivize capital to invest in new power plant by allowing the price to spike in high-demand hours. Naturally attact new generators.

# Q8: A battery operator in PJM has a 100 MW / 400 MWh battery. They can't simultaneously bid all 100 MW into Regulation and discharge at full power for energy arbitrage. Why? What does the optimizer have to do?
Because some energy must be stored to discharge while the grid is not stable due to Regup contract. If all the capacity are used in energy arbitrage, there would have nothing left for emergency situations.

# Clean table
| Dimension | PJM | ERCOT | CAISO |
|---|---|---|---|
| Hubs | Western Hub, AEP-Dayton, NI, Eastern | HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST | TH_NP15, TH_SP15, TH_ZP26 |
| DA gate | 10:30 ET | 10:00 CT | 10:00 PT |
| RT granularity | 5-min | 5-min | 5-min + 15-min FMM |
| Co-optimization | Yes | Migrating | Yes |
| Reg products | RegA + **RegD (fast)** | RegUp + RegDown + **ECRS** + **FFR** | RegUp + RegDown |
| Capacity mechanism | RPM (3-yr forward auction) | None — energy-only + ORDC | RA (bilateral contracts, annual) |
| Capacity $/MW-yr (4-hr battery) | ~$60–70k after ELCC | $0 | ~$80–120k (RA) |
| 2025–26 revenue mix | ~80% Reg, balance energy + capacity | ~50% AS / ~40% energy arbitrage / ~10% other | ~55% energy / ~20% AS / ~20% RA |
| 2025–26 BESS revenue level | ~$24/kW-month (highest in US) | ~$3–4/kW-month | ~$3.5/kW-month |
| Strategic punchline | Highest current revenue + bankable capacity; AS saturation risk on horizon | Energy-only volatility play; need sharp arbitrage skill; saturated AS | Mature market, declining margins; RA stability is the durable revenue |