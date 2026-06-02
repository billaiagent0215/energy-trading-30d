"""
Reusable timezone + DST utilities for cross-ISO energy data work.

Import pattern:
    from timezone_utils import ensure_utc, to_market_local, MARKET_TZ

Design principles:
    1. All internal storage is UTC. Conversion happens at I/O edges only.
    2. DST handling is explicit — never silently shift.
    3. ISO conventions are encoded as constants, not magic strings.
"""

import pandas as pd


# ----- Market → timezone lookup ----------------------------------------------

MARKET_TZ = {
    "caiso":  "America/Los_Angeles",
    "ercot":  "America/Chicago",
    "pjm":    "America/New_York",
    "miso":   "America/New_York",
    "isone":  "America/New_York",
    "nyiso":  "America/New_York",
    "spp":    "America/Chicago",
}

# Hour convention: "HB" = Hour Beginning, "HE" = Hour Ending
MARKET_HOUR_CONVENTION = {
    "caiso":  "HB",
    "ercot":  "HE",
    "pjm":    "HE",
    "miso":   "HE",
    "isone":  "HE",
    "nyiso":  "HB",
    "spp":    "HE",
}


# ----- Function 1: ensure_utc -------------------------------------------------

def ensure_utc(df, col="interval_start"):
    """
    Guarantee df[col] is a tz-aware UTC datetime column.

    Handles three input cases:
      - already tz-aware UTC: no-op
      - tz-aware in another zone: convert to UTC
      - naive: assume UTC and localize

    Returns a copy of df with the column overwritten.

    TODO: implement this function.
    Hints:
      - Use pd.to_datetime(df[col]) to ensure it's datetime type.
      - Check df[col].dt.tz: None means naive, otherwise tz-aware.
      - For naive timestamps, use .dt.tz_localize("UTC").
      - For tz-aware in another zone, use .dt.tz_convert("UTC").
    """
    df = df.copy()
    df[col] = pd.to_datetime(df[col])    # ensure datetime type
    if df[col].dt.tz is None:
        df[col] = df[col].dt.tz_localize("UTC")
    else:
        df[col] = df[col].dt.tz_convert("UTC")
    return df


# ----- Function 2: to_market_local --------------------------------------------

def to_market_local(df, col, market):
    """
    Convert a UTC datetime column to the market's operating timezone.

    Args:
        df: DataFrame
        col: column name containing tz-aware UTC timestamps
        market: one of MARKET_TZ keys

    Returns a copy of df with df[col] converted to local time.

    TODO: implement this function.
    Hints:
      - First call ensure_utc() to be safe.
      - Look up MARKET_TZ[market] (raise KeyError if not found).
      - Use .dt.tz_convert(tz).
    """
    df = df.copy()
    df = ensure_utc(df, col)
    tz = MARKET_TZ[market]
    df[col] = df[col].dt.tz_convert(tz)
    return df

# ----- Function 3: safe_localize ----------------------------------------------

def safe_localize(ts_series, tz):
    """
    Safely localize naive timestamps. DST-nonexistent or DST-ambiguous
    timestamps become NaT instead of raising or silently shifting.

    Args:
        ts_series: pandas Series of naive timestamps
        tz: target IANA timezone string

    Returns a tz-aware Series. NaT for problematic timestamps.

    TODO: implement this function.
    Hints:
      - Use ts_series.dt.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").
      - Both keyword arguments are critical — don't omit either.
    """
    return ts_series.dt.tz_localize(tz, ambiguous="NaT", nonexistent="NaT")



# ----- Function 4: asof_join_forecasts ---------------------------------------

def asof_join_forecasts(actuals, forecasts, ts_col="timestamp",
                        tolerance="6h"):
    """
    Pair each actual observation with the most recent forecast that was
    AVAILABLE BEFORE that observation. Prevents look-ahead bias.

    Args:
        actuals: DataFrame with ts_col (tz-aware) and an 'actual' column
        forecasts: DataFrame with ts_col (tz-aware) and a 'forecast' column
        ts_col: timestamp column name (default 'timestamp')
        tolerance: max age of forecast acceptable (default '6h')

    Returns merged DataFrame. Rows where no forecast was available within
    the tolerance have NaN in the forecast column.

    TODO: implement this function.
    Hints:
      - Sort both inputs by ts_col first (asof requires sorted).
      - Use pd.merge_asof(actuals, forecasts, on=ts_col,
                          direction='backward',
                          tolerance=pd.Timedelta(tolerance)).
    """
    actuals_sorted = actuals.sort_values(ts_col)
    forecasts_sorted = forecasts.sort_values(ts_col)
    return pd.merge_asof(
        actuals_sorted, forecasts_sorted,
        on=ts_col,
        direction="backward",
        tolerance=pd.Timedelta(tolerance),
    )


# ----- Quick smoke test -------------------------------------------------------

if __name__ == "__main__":
    print("Testing timezone_utils...\n")

    # Test 1: ensure_utc with already-UTC data
    df1 = pd.DataFrame({
        "interval_start": pd.date_range("2026-05-01", periods=3, freq="h", tz="UTC"),
        "value": [1, 2, 3]
    })
    print("Test 1 input (UTC):", df1["interval_start"].dt.tz)
    df1_out = ensure_utc(df1)
    print("Test 1 output:     ", df1_out["interval_start"].dt.tz)
    assert str(df1_out["interval_start"].dt.tz) == "UTC", "Should remain UTC"

    # Test 2: ensure_utc with naive data
    df2 = pd.DataFrame({
        "interval_start": pd.date_range("2026-05-01", periods=3, freq="h"),
        "value": [1, 2, 3]
    })
    print("\nTest 2 input (naive):", df2["interval_start"].dt.tz)
    df2_out = ensure_utc(df2)
    print("Test 2 output:       ", df2_out["interval_start"].dt.tz)
    assert str(df2_out["interval_start"].dt.tz) == "UTC", "Should become UTC"

    # Test 3: to_market_local
    df3_out = to_market_local(df1, "interval_start", "caiso")
    print("\nTest 3 CAISO local time:")
    print(df3_out)
    assert "Los_Angeles" in str(df3_out["interval_start"].dt.tz)

    # Test 4: safe_localize with DST spring-forward
    bad_ts = pd.Series(pd.to_datetime([
        "2026-03-08 01:00:00",
        "2026-03-08 02:30:00",   # nonexistent — should become NaT
        "2026-03-08 03:00:00",
    ]))
    localized = safe_localize(bad_ts, "America/Los_Angeles")
    print("\nTest 4 DST spring-forward:")
    print(localized)
    assert pd.isna(localized.iloc[1]), "02:30 on 2026-03-08 should be NaT"

    # Test 5: safe_localize with DST fall-back ambiguity
    ambig_ts = pd.Series(pd.to_datetime([
        "2025-11-02 00:00:00",
        "2025-11-02 01:30:00",   # ambiguous — should become NaT
        "2025-11-02 03:00:00",
    ]))
    localized = safe_localize(ambig_ts, "America/Los_Angeles")
    print("\nTest 5 DST fall-back:")
    print(localized)
    assert pd.isna(localized.iloc[1]), "01:30 on 2025-11-02 should be NaT"

    # Test 6: asof_join_forecasts
    actuals = pd.DataFrame({
        "timestamp": pd.date_range("2026-05-01", periods=5, freq="h", tz="UTC"),
        "actual": [10, 12, 15, 18, 14]
    })
    forecasts = pd.DataFrame({
        "timestamp": pd.date_range("2026-05-01", periods=3, freq="2h", tz="UTC"),
        "forecast": [11, 16, 13]
    })
    joined = asof_join_forecasts(actuals, forecasts, ts_col="timestamp")
    print("\nTest 6 asof join:")
    print(joined)
    assert "forecast" in joined.columns

    print("\n✓ All tests passed!")
