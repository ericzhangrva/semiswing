"""DuckDB + Parquet storage and data-health reconciliation engine."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import duckdb
import numpy as np
import pandas as pd

from semiswing.config import PROJECT_ROOT, StrategySettings, UniverseSettings
from semiswing.data.providers.sources import (
    fetch_earnings_dates,
    fetch_fred_series,
    fetch_stooq_daily,
    fetch_yfinance_daily,
)

DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "semiswing.duckdb"


def get_connection(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    p = db_path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(p))


def check_bar_sanity(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Verify bar sanity rules: positive prices, high >= max(open, close), low <= min(open, close)."""
    if df.empty:
        return df, {"health_score": 0.0, "invalid_bars": 0, "extreme_jumps": 0}

    out = df.copy()
    valid_price = (out["close"] > 0) & (out["open"] > 0) & (out["high"] > 0) & (out["low"] > 0)
    # Repair tiny floating-point rounding discrepancies in adjusted OHLC
    max_oc = np.maximum(out["open"], out["close"])
    min_oc = np.minimum(out["open"], out["close"])
    out["high"] = np.maximum(out["high"], max_oc)
    out["low"] = np.minimum(out["low"], min_oc)

    invalid_count = int((~valid_price).sum())
    out = out[valid_price].copy()

    out["ret_1d"] = out.groupby("ticker")["close"].pct_change()
    extreme_jumps = int((out["ret_1d"].abs() > 0.35).sum())
    out = out.drop(columns=["ret_1d"])

    total_rows = max(len(df), 1)
    penalty = min(40.0, (invalid_count / total_rows) * 1000.0)
    health_score = max(0.0, 100.0 - penalty)
    return out, {
        "health_score": round(health_score, 1),
        "invalid_bars": invalid_count,
        "extreme_jumps": extreme_jumps,
    }


def reconcile_eod_sample(
    yf_df: pd.DataFrame, sample_tickers: List[str], tolerance: float = 0.005, lookback_days: int = 30
) -> Dict[str, float]:
    """Compare recent EOD closes between yfinance and Stooq on a sample of tickers."""
    if yf_df.empty:
        return {"reconciled_tickers": 0, "agreement_rate": 0.0, "median_diff_pct": 1.0}

    cutoff = yf_df["date"].max() - pd.Timedelta(days=lookback_days * 2)
    diffs = []
    checked = 0
    for t in sample_tickers:
        stq = fetch_stooq_daily(t, start_date=cutoff.strftime("%Y-%m-%d"))
        if stq.empty:
            continue
        yf_sub = yf_df[(yf_df["ticker"] == t) & (yf_df["date"] >= cutoff)][["date", "close"]].rename(
            columns={"close": "close_yf"}
        )
        merged = pd.merge(yf_sub, stq[["date", "close"]], on="date", how="inner").tail(lookback_days)
        if merged.empty:
            continue
        checked += 1
        rel_diff = (merged["close_yf"] - merged["close"]).abs() / merged["close"]
        diffs.extend(rel_diff.tolist())

    if not diffs:
        return {"reconciled_tickers": 0, "agreement_rate": 1.0, "median_diff_pct": 0.0}

    arr = np.array(diffs)
    agreement = float((arr <= tolerance).mean())
    median_diff = float(np.median(arr))
    return {
        "reconciled_tickers": checked,
        "agreement_rate": round(agreement, 4),
        "median_diff_pct": round(median_diff * 100.0, 4),
    }


def ingest_all(
    strategy: StrategySettings,
    universe: UniverseSettings,
    start_date: str = "2017-01-01",
    db_path: Path | None = None,
) -> Dict[str, object]:
    """Ingest prices, FRED macro series, and earnings dates into DuckDB + Parquet."""
    # Fetch 1 extra warmup year prior to start_date so 250d rolling features are warm on start_date
    warmup_start = (pd.to_datetime(start_date) - pd.Timedelta(days=400)).strftime("%Y-%m-%d")

    all_tickers = universe.all_equity_and_context
    yf_df = fetch_yfinance_daily(all_tickers, start_date=warmup_start)
    clean_df, sanity_stats = check_bar_sanity(yf_df)

    # Cross-check recent EOD prices against Stooq on core tradeable leaders
    recon_stats = reconcile_eod_sample(
        clean_df,
        sample_tickers=universe.tradeable_stocks[:5] + universe.tradeable_etfs,
        tolerance=strategy.data.eod_tolerance,
    )

    fred_df = fetch_fred_series(list(universe.fred_series.keys()), start_date=warmup_start)
    earnings_df = fetch_earnings_dates(universe.all_panel_stocks)

    # Combine health score
    recon_penalty = max(0.0, (1.0 - recon_stats["agreement_rate"]) * 30.0)
    overall_health = round(max(0.0, sanity_stats["health_score"] - recon_penalty), 1)

    conn = get_connection(db_path)
    try:
        conn.register("clean_df_view", clean_df)
        conn.execute("CREATE OR REPLACE TABLE daily_bars AS SELECT * FROM clean_df_view")

        conn.register("fred_df_view", fred_df)
        conn.execute("CREATE OR REPLACE TABLE fred_series AS SELECT * FROM fred_df_view")

        conn.register("earnings_df_view", earnings_df)
        conn.execute("CREATE OR REPLACE TABLE earnings_dates AS SELECT * FROM earnings_df_view")

        health_row = pd.DataFrame(
            [
                {
                    "run_ts": pd.Timestamp.now(),
                    "health_score": overall_health,
                    "invalid_bars": sanity_stats["invalid_bars"],
                    "extreme_jumps": sanity_stats["extreme_jumps"],
                    "reconciled_tickers": recon_stats["reconciled_tickers"],
                    "agreement_rate": recon_stats["agreement_rate"],
                    "median_diff_pct": recon_stats["median_diff_pct"],
                }
            ]
        )
        conn.register("health_row_view", health_row)
        conn.execute("CREATE OR REPLACE TABLE data_health AS SELECT * FROM health_row_view")
    finally:
        conn.close()

    # Also save Parquet snapshots for fast inspection
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_parquet(DATA_DIR / "daily_bars.parquet", index=False)
    fred_df.to_parquet(DATA_DIR / "fred_series.parquet", index=False)
    earnings_df.to_parquet(DATA_DIR / "earnings_dates.parquet", index=False)

    return {
        "rows_bars": len(clean_df),
        "tickers_ingested": clean_df["ticker"].nunique(),
        "date_min": str(clean_df["date"].min().date()) if not clean_df.empty else None,
        "date_max": str(clean_df["date"].max().date()) if not clean_df.empty else None,
        "rows_fred": len(fred_df),
        "rows_earnings": len(earnings_df),
        "health_score": overall_health,
        **recon_stats,
    }


def load_stored_data(db_path: Path | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float]:
    """Load daily_bars, fred_series, earnings_dates, and latest data_health score from DuckDB."""
    conn = get_connection(db_path)
    try:
        bars = conn.execute("SELECT * FROM daily_bars ORDER BY ticker, date").df()
        fred = conn.execute("SELECT * FROM fred_series ORDER BY series_id, date").df()
        earnings = conn.execute("SELECT * FROM earnings_dates ORDER BY ticker, earnings_date").df()
        health_df = conn.execute("SELECT health_score FROM data_health ORDER BY run_ts DESC LIMIT 1").df()
        health = float(health_df["health_score"].iloc[0]) if not health_df.empty else 100.0
    finally:
        conn.close()
    bars["date"] = pd.to_datetime(bars["date"]).dt.tz_localize(None)
    if not fred.empty:
        fred["date"] = pd.to_datetime(fred["date"]).dt.tz_localize(None)
    if not earnings.empty:
        earnings["earnings_date"] = pd.to_datetime(earnings["earnings_date"]).dt.tz_localize(None)
    return bars, fred, earnings, health
