"""Data providers for daily OHLCV, macro series, and earnings dates."""

from __future__ import annotations

import io
import os
from datetime import datetime
from typing import Dict, List

import httpx
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_yfinance_daily(tickers: List[str], start_date: str = "2017-01-01") -> pd.DataFrame:
    """Download adjusted and unadjusted daily OHLCV from yfinance in batch."""
    if not tickers:
        return pd.DataFrame()

    raw = yf.download(
        tickers=tickers,
        start=start_date,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
        threads=True,
    )
    if raw.empty:
        return pd.DataFrame()

    rows = []
    if len(tickers) == 1:
        t = tickers[0]
        df_t = raw.copy()
        df_t = df_t.dropna(how="all")
        df_t["ticker"] = t
        df_t["date"] = pd.to_datetime(df_t.index).tz_localize(None)
        rows.append(df_t)
    else:
        for t in tickers:
            if t not in raw.columns.get_level_values(0):
                continue
            df_t = raw[t].copy().dropna(how="all")
            if df_t.empty:
                continue
            df_t["ticker"] = t
            df_t["date"] = pd.to_datetime(df_t.index).tz_localize(None)
            rows.append(df_t)

    if not rows:
        return pd.DataFrame()

    out = pd.concat(rows, ignore_index=True)
    out = out.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    keep_cols = ["date", "ticker", "open", "high", "low", "close", "volume"]
    for c in keep_cols:
        if c not in out.columns:
            out[c] = np.nan
    out = out[keep_cols].dropna(subset=["close"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    out["source"] = "yfinance"
    return out


def fetch_stooq_daily(ticker: str, start_date: str = "2017-01-01") -> pd.DataFrame:
    """Fetch daily EOD bars from Stooq CSV endpoint for cross-source reconciliation."""
    if ticker.startswith("^"):
        return pd.DataFrame()
    stooq_sym = f"{ticker.lower()}.us"
    url = f"https://stooq.com/q/d/l/?s={stooq_sym}&i=d"
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200 or "No data" in resp.text or len(resp.text.strip()) < 30:
                return pd.DataFrame()
            df = pd.read_csv(io.StringIO(resp.text))
    except Exception:
        return pd.DataFrame()

    if "Date" not in df.columns or "Close" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    df = df[df["date"] >= pd.to_datetime(start_date)].copy()
    if df.empty:
        return pd.DataFrame()

    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df["ticker"] = ticker
    df["source"] = "stooq"
    for c in ["open", "high", "low", "close", "volume"]:
        if c not in df.columns:
            df[c] = np.nan
    return df[["date", "ticker", "open", "high", "low", "close", "volume", "source"]].sort_values("date").reset_index(drop=True)


def fetch_fred_series(series_ids: List[str], start_date: str = "2017-01-01") -> pd.DataFrame:
    """Fetch official FRED macro series via public fredgraph.csv (or API if key provided)."""
    rows = []
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for sid in series_ids:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start_date}"
            try:
                resp = client.get(url)
                if resp.status_code != 200:
                    continue
                df = pd.read_csv(io.StringIO(resp.text))
                date_col = "DATE" if "DATE" in df.columns else df.columns[0]
                val_col = sid if sid in df.columns else df.columns[1]
                df["date"] = pd.to_datetime(df[date_col], errors="coerce").dt.tz_localize(None)
                df["value"] = pd.to_numeric(df[val_col], errors="coerce")
                df = df.dropna(subset=["date", "value"]).copy()
                df["series_id"] = sid
                rows.append(df[["date", "series_id", "value"]])
            except Exception:
                continue

    if not rows:
        return pd.DataFrame(columns=["date", "series_id", "value"])
    return pd.concat(rows, ignore_index=True).sort_values(["series_id", "date"]).reset_index(drop=True)


def fetch_earnings_dates(tickers: List[str]) -> pd.DataFrame:
    """Fetch historical and upcoming earnings dates for single-stock tickers via yfinance."""
    rows = []
    for t in tickers:
        if t.startswith("^"):
            continue
        try:
            tk = yf.Ticker(t)
            ed = tk.get_earnings_dates(limit=40)
            if ed is not None and not ed.empty:
                dates = pd.to_datetime(ed.index).tz_localize(None).normalize().unique()
                for d in dates:
                    rows.append({"ticker": t, "earnings_date": d})
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(columns=["ticker", "earnings_date"])
    return pd.DataFrame(rows).drop_duplicates().sort_values(["ticker", "earnings_date"]).reset_index(drop=True)
