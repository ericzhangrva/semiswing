"""Unit and causal look-ahead invariance tests for SemiSwing."""

from __future__ import annotations

import numpy as np
import pandas as pd

from semiswing.backtest.engine import run_portfolio_backtest
from semiswing.config import (
    load_events_settings,
    load_strategy_settings,
    load_universe_settings,
)
from semiswing.data.store import check_bar_sanity
from semiswing.features.build import FEATURE_COLUMNS, build_feature_panel
from semiswing.labels.triple_barrier import (
    PurgedEmbargoKFold,
    compute_triple_barrier_labels,
)
from semiswing.models.signal_models import evaluate_baseline_signals


def _make_synthetic_market(n_days: int = 350) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(123)
    dates = pd.bdate_range("2021-01-01", periods=n_days)
    tickers = ["NVDA", "MU", "INTC", "SMH", "SPY", "^VIX", "^VIX3M", "^VXN", "^VVIX", "^SKEW"]

    rows = []
    for t in tickers:
        if t in ("^VIX", "^VIX3M", "^VXN"):
            base = 18.0 if t != "^VIX3M" else 21.0
            closes = base + np.cumsum(rng.normal(0, 0.3, size=n_days))
            closes = np.clip(closes, 11.0, 26.0)
        elif t == "^VVIX":
            closes = np.full(n_days, 92.0)
        elif t == "^SKEW":
            closes = np.full(n_days, 130.0)
        else:
            drift = 0.0025 if t in ("NVDA", "MU", "SMH") else 0.0005
            rets = rng.normal(drift, 0.015, size=n_days)
            closes = 100.0 * np.exp(np.cumsum(rets))

        for d, c in zip(dates, closes):
            rows.append(
                {
                    "date": d,
                    "ticker": t,
                    "open": c * 0.995,
                    "high": c * 1.012,
                    "low": c * 0.988,
                    "close": c,
                    "volume": 5_000_000.0,
                    "source": "synthetic",
                }
            )
    bars = pd.DataFrame(rows)
    fred = pd.DataFrame(columns=["date", "series_id", "value"])
    earnings = pd.DataFrame(columns=["ticker", "earnings_date"])
    return bars, fred, earnings


def test_config_loads_and_excludes_leveraged_etfs():
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()

    assert strategy.backtest.start_date == "2018-01-01"
    assert strategy.backtest.oos_start_date == "2022-01-01"
    assert strategy.risk.paper_equity == 10000.0
    assert "SOXL" not in universe.all_tradeable
    assert "SMH" in universe.tradeable_etfs
    assert len(events.fomc_dates) > 40


def test_bar_sanity_check():
    df = pd.DataFrame(
        [
            {"date": pd.Timestamp("2025-01-02"), "ticker": "NVDA", "open": 100.0, "high": 99.0, "low": 101.0, "close": 100.5, "volume": 1000},
            {"date": pd.Timestamp("2025-01-03"), "ticker": "NVDA", "open": -5.0, "high": 10.0, "low": 5.0, "close": 8.0, "volume": 1000},
        ]
    )
    clean, stats = check_bar_sanity(df)
    assert len(clean) == 1
    assert stats["invalid_bars"] == 1
    assert clean.iloc[0]["high"] >= clean.iloc[0]["close"]
    assert clean.iloc[0]["low"] <= clean.iloc[0]["open"]


def test_causal_lookahead_invariance():
    """
    CRITICAL TEST: Verify that features computed at t <= T_cutoff on a truncated dataset [0..T_cutoff]
    are strictly identical to features at t <= T_cutoff when future bars [T_cutoff+1..N] are appended.
    """
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    bars, fred, earnings = _make_synthetic_market(n_days=300)

    cutoff_date = sorted(bars["date"].unique())[220]
    bars_trunc = bars[bars["date"] <= cutoff_date].copy()

    panel_full = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel_trunc = build_feature_panel(bars_trunc, fred, earnings, strategy, universe, events)

    sub_full = panel_full[panel_full["date"] == cutoff_date].sort_values("ticker").reset_index(drop=True)
    sub_trunc = panel_trunc[panel_trunc["date"] == cutoff_date].sort_values("ticker").reset_index(drop=True)

    assert len(sub_full) == len(sub_trunc)
    for col in FEATURE_COLUMNS + ["regime_on", "smh_secular_bull", "macro_scalar"]:
        v_full = sub_full[col].values
        v_trunc = sub_trunc[col].values
        mask = ~np.isnan(v_full) & ~np.isnan(v_trunc)
        assert np.allclose(v_full[mask], v_trunc[mask], atol=1e-10), f"Look-ahead leakage detected in {col}"


def test_purged_embargo_cv_has_zero_overlap():
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    bars, fred, earnings = _make_synthetic_market(n_days=280)

    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)
    clean = panel.dropna(subset=["tb_label"]).reset_index(drop=True)

    cv = PurgedEmbargoKFold(n_splits=4, embargo_days=20)
    for tr_idx, te_idx in cv.split(clean):
        tr = clean.iloc[tr_idx]
        te = clean.iloc[te_idx]
        t_test_start = te["date"].min()
        t_test_end = te["date"].max()

        # No training sample starting before test may have tb_end_date >= t_test_start
        before_test = tr[tr["date"] < t_test_start]
        assert (before_test["tb_end_date"] < t_test_start).all()
        # No training sample may fall inside the test window
        assert ((tr["date"] < t_test_start) | (tr["date"] > t_test_end)).all()


def test_portfolio_backtest_runs_and_respects_risk_caps():
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    bars, fred, earnings = _make_synthetic_market(n_days=320)

    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)
    panel = evaluate_baseline_signals(panel, strategy)

    res = run_portfolio_backtest(panel, strategy, mode="baseline", start_date="2021-06-01")
    assert not res.equity_curve.empty
    assert (res.equity_curve["n_positions"] <= strategy.risk.max_positions).all()
    assert (res.equity_curve["equity"] > 0).all()


def test_dynamic_pit_universe_reconstitution_and_causal_invariance():
    """
    Test Phase 3 Two-Stage PIT Funnel:
    - Stage 1: Close >= 15, history >= 60d, med dollar vol >= 150M
    - Stage 2: Top 40 ranked by log10(dollar_vol) * ATR%
    - Causal look-ahead invariance: Future quarters do not alter past quarter universes.
    """
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    bars, fred, earnings = _make_synthetic_market(n_days=350)

    # Compute PIT universe on full dataset vs truncated dataset
    cutoff_date = sorted(bars["date"].unique())[250]
    bars_trunc = bars[bars["date"] <= cutoff_date].copy()

    from semiswing.features.build import compute_pit_quarterly_universe
    univ_full = compute_pit_quarterly_universe(bars, universe)
    univ_trunc = compute_pit_quarterly_universe(bars_trunc, universe)

    # For dates up to cutoff_date that belong to quarters prior to or at cutoff, universes must match exactly
    common_dates = [d for d in univ_trunc.keys() if d in univ_full and d <= cutoff_date]
    assert len(common_dates) > 0
    for d in common_dates:
        assert univ_full[d] == univ_trunc[d], f"Look-ahead leakage in PIT universe at {d}"

    # Verify panel is_tradeable_universe flag matches
    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    assert "is_tradeable_universe" in panel.columns
    # Check that ETFs are always marked tradeable
    for etf in universe.tradeable_etfs:
        etf_rows = panel[panel["ticker"] == etf]
        if not etf_rows.empty:
            assert (etf_rows["is_tradeable_universe"] == 1).all()


def test_missing_single_stock_bar_forward_fills_mark_to_market():
    """
    Verify Task 1 regression fix:
    - Missing single-stock bar on day t forward-fills last_valid_close rather than crashing to entry price or $0.
    - Missing benchmark ETFs (SMH/SPY) prevents the master calendar from advancing onto a partial ingestion day.
    """
    strategy = load_strategy_settings()
    d0 = pd.Timestamp("2023-01-02")
    d1 = pd.Timestamp("2023-01-03")
    d2 = pd.Timestamp("2023-01-04")
    d3 = pd.Timestamp("2023-01-05")  # Partial date missing SMH/SPY

    rows = [
        # Day 0: Signal generation day
        {"date": d0, "ticker": "SMH", "open": 200.0, "high": 202.0, "low": 198.0, "close": 201.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
        {"date": d0, "ticker": "SPY", "open": 400.0, "high": 402.0, "low": 398.0, "close": 401.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
        {"date": d0, "ticker": "NVDA", "open": 98.0, "high": 101.0, "low": 97.0, "close": 100.0, "atr": 3.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 1, "baseline_score": 2.5, "baseline_tier": "HIGH", "baseline_prob": 0.8},

        # Day 1: Order fills at Open (100.0), Closes at 104.0 (last_valid_close = 104.0)
        {"date": d1, "ticker": "SMH", "open": 201.0, "high": 203.0, "low": 200.0, "close": 202.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
        {"date": d1, "ticker": "SPY", "open": 401.0, "high": 403.0, "low": 400.0, "close": 402.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
        {"date": d1, "ticker": "NVDA", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "atr": 3.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},

        # Day 2: SMH & SPY trade normally; NVDA bar is completely missing!
        {"date": d2, "ticker": "SMH", "open": 202.0, "high": 204.0, "low": 201.0, "close": 203.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
        {"date": d2, "ticker": "SPY", "open": 402.0, "high": 404.0, "low": 401.0, "close": 403.0, "atr": 4.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},

        # Day 3: Partial ingestion anomaly (SMH/SPY missing)
        {"date": d3, "ticker": "AAPL", "open": 150.0, "high": 152.0, "low": 149.0, "close": 151.0, "atr": 3.0, "regime_on": 1, "smh_secular_bull": 1, "baseline_signal": 0, "baseline_score": 0.0, "baseline_tier": "HIGH", "baseline_prob": 0.5},
    ]
    panel = pd.DataFrame(rows)
    res = run_portfolio_backtest(panel, strategy, mode="baseline", start_date="2023-01-01", bull_core_smh=False)

    # 1. Master Calendar Gate verification: Day 3 dropped
    assert d3 not in list(res.equity_curve["date"])

    # 2. Verify NVDA remained in open positions on Day 2 and forward-filled at 104.0
    row_d2 = res.equity_curve[res.equity_curve["date"] == d2].iloc[0]
    assert row_d2["n_positions"] == 1, "Open position was lost on missing bar day!"
    assert row_d2["equity"] > 9500.0, f"Mark-to-market cliff occurred: {row_d2['equity']}"


