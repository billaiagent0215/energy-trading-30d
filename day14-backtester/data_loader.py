"""
Layer 1+2: ingestion + storage.

Pulls 12 months of CAISO TH_NP15_GEN-APND day-ahead hourly LMPs,
caches per-month parquet files for resumability, and exposes a
single function load_year() that returns a clean tz-aware DataFrame.

Run this once: python data_loader.py
"""

from pathlib import Path
from datetime import datetime, timedelta
import time

import pandas as pd
import gridstatus


# ---------- Configuration ----------
HUB = "TH_NP15_GEN-APND"
START = datetime(2025, 5, 1)
END = datetime(2026, 5, 1)                  # exclusive — gives 12 full months
CACHE_DIR = Path(__file__).parent / "data"
CACHE_DIR.mkdir(exist_ok=True)


def _month_starts(start: datetime, end: datetime):
    """Yield (month_start, next_month_start) tuples covering [start, end)."""
    cur = start
    while cur < end:
        if cur.month == 12:
            nxt = datetime(cur.year + 1, 1, 1)
        else:
            nxt = datetime(cur.year, cur.month + 1, 1)
        yield cur, min(nxt, end)
        cur = nxt


def _pull_one_month(iso, month_start: datetime, month_end: datetime,
                    max_retries: int = 3) -> pd.DataFrame:
    """Pull a single month of DA hourly LMPs at HUB. Retries on failure."""
    for attempt in range(max_retries):
        try:
            df = iso.get_lmp(
                date=month_start,
                end=month_end,
                market="DAY_AHEAD_HOURLY",
                locations=[HUB],
            )
            # Normalize column names
            df = df.rename(columns={"Interval Start": "interval_start",
                                    "LMP": "lmp"})
            return df[["interval_start", "lmp"]].sort_values("interval_start")
        except Exception as e:
            wait = 2 ** attempt
            print(f"   attempt {attempt+1} failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Failed to pull {month_start:%Y-%m} after {max_retries} retries")


def pull_and_cache():
    """Pull all months that aren't already cached. Idempotent."""
    iso = gridstatus.CAISO()
    for m_start, m_end in _month_starts(START, END):
        cache_file = CACHE_DIR / f"caiso_np15_da_{m_start:%Y-%m}.parquet"
        if cache_file.exists():
            print(f"✓ cached: {cache_file.name}")
            continue
        print(f"→ pulling: {m_start:%Y-%m}")
        df = _pull_one_month(iso, m_start, m_end)
        df.to_parquet(cache_file, index=False)
        print(f"   wrote {len(df)} rows to {cache_file.name}")


def load_year() -> pd.DataFrame:
    """Load all cached months, concatenated, deduplicated, sorted."""
    frames = []
    for m_start, _ in _month_starts(START, END):
        cache_file = CACHE_DIR / f"caiso_np15_da_{m_start:%Y-%m}.parquet"
        if cache_file.exists():
            frames.append(pd.read_parquet(cache_file))
    if not frames:
        raise RuntimeError("No cached data found. Run pull_and_cache() first.")
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset="interval_start").sort_values("interval_start")
    df["interval_start"] = pd.to_datetime(df["interval_start"], utc=True)
    return df.reset_index(drop=True)


if __name__ == "__main__":
    pull_and_cache()
    df = load_year()
    print(f"\nLoaded {len(df)} hourly observations")
    print(f"Date range: {df['interval_start'].min()} → {df['interval_start'].max()}")
    print(f"Mean LMP:   ${df['lmp'].mean():.2f}/MWh")
    print(f"Min LMP:    ${df['lmp'].min():.2f}/MWh")
    print(f"Max LMP:    ${df['lmp'].max():.2f}/MWh")
    print(f"Std LMP:    ${df['lmp'].std():.2f}/MWh")
