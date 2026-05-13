# CAISO NP15 — 30-day price shape (April–May 2026)

Pulled 30 days of CAISO Day-Ahead hourly LMPs at `TH_NP15_GEN-APND`.

## Headline

The peak (17–21) vs. off-peak (10–14) spread averaged **$20.12/MWh** over the window;
monthly average LMP was **$15.30/MWh**, with hour 14 occasionally going negative —
the classic California "duck curve" with solar over-generation pushing midday prices
below zero.

A 100 MW / 400 MWh battery cycling once per day at 90% round-trip efficiency would
earn roughly **$26.4/kW-year** (~$2.64M/year) under perfect-foresight arbitrage alone.

CAISO BESS fleet earns ~$42/kW-year today (Modo, 2025), implying:
- ~63% of total BESS revenue comes from energy arbitrage
- ~37% comes from ancillary services and RA capacity payments

**Seasonal caveat:** May is a shoulder month — solar abundance and mild evening
load compress spreads. Summer (Jul–Sep) typically runs 2–3× higher; a full-year
arbitrage estimate is likely $35–50/kW-year.

## Files
- `price_shape.ipynb` — full notebook
- `data/caiso_np15_da_30d.parquet` — cached price pull (regenerate by running the notebook)
- `hour_profile.png` — average hour-of-day curve (the duck shape, with the hour-14 negative)
- `daily_variation.png` — 30 daily shapes overlaid on the 30-day average
- `daily_mean.png` — average daily LMP across the month (which days were broadly expensive)

## Re-run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook price_shape.ipynb
```