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
    for col in FEATURE_COLUMNS:
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
