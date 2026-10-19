"""Institutional Validation Gate and CI Regression Test Suite (§9 of instruction.md).

Tier 1 Deterministic CI Invariance & Gate Integrity:
- Zero DuckDB dependency (runs in milliseconds in fresh GitHub Actions environments).
- Validates that committed audit manifest matches current source code SHA256 digest (preventing stale artifact merging).
- Verifies mathematical hurdle logic on synthetic edge cases.
- Enforces that committed audit manifest passes all 8 institutional gates for both Cash Swing and SMH Bull Core modes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from semiswing.backtest.engine import BacktestResult
from semiswing.backtest.report import (
    CASH_SWING_HURDLES,
    SMH_CORE_HURDLES,
    STRATEGY_SOURCE_FILES,
    _build_institutional_gates,
    compute_strategy_source_sha256,
)
from semiswing.config import PROJECT_ROOT


def _make_dummy_result(
    ai_sharpe: float = 1.80,
    ai_dsr: float = 0.965,
    ai_pf: float = 4.80,
    ai_dd: float = 34.0,
    oos_sharpe: float = 1.35,
    oos_pf: float = 4.50,
    oos_dd: float = 36.0,
    bear_ret: float = -20.0,
    bear_dd: float = 22.0,
    bear_cash: float = 88.0,
) -> BacktestResult:
    res = BacktestResult(name="TestMode", equity_curve=None, trades=None)
    res.metrics_ai_era = {
        "sharpe": ai_sharpe,
        "deflated_sharpe_prob": ai_dsr,
        "profit_factor": ai_pf,
        "max_dd_pct": ai_dd,
        "trades": 70,
        "win_rate_pct": 60.0,
        "total_return_pct": 1200.0,
        "cagr_pct": 100.0,
    }
    res.metrics_overall = {
        "sharpe": oos_sharpe,
        "deflated_sharpe_prob": 0.90,
        "profit_factor": oos_pf,
        "max_dd_pct": oos_dd,
        "trades": 85,
        "win_rate_pct": 58.0,
        "total_return_pct": 800.0,
        "cagr_pct": 60.0,
    }
    res.metrics_2022_bear = {
        "total_return_pct": bear_ret,
        "max_dd_pct": bear_dd,
        "cash_days_pct": bear_cash,
        "trades": 15,
        "win_rate_pct": 0.0,
        "profit_factor": 0.0,
    }
    return res


def test_strategy_source_files_exist():
    """Verify all files designated in STRATEGY_SOURCE_FILES exist on disk."""
    for rel_path in STRATEGY_SOURCE_FILES:
        fp = PROJECT_ROOT / rel_path
        assert fp.exists(), f"Designated strategy source file missing: {rel_path}"


def test_source_code_manifest_freshness():
    """
    CI TIER 1 GUARD: Verify that the committed audit manifest SHA256 digest
    matches the exact current SHA256 of all strategy and configuration source code.
    If source code was modified without regenerating the backtest audit report, fail immediately.
    """
    manifest_path = PROJECT_ROOT / "reports" / "backtests" / "audit_manifest.json"
    assert manifest_path.exists(), (
        "Missing reports/backtests/audit_manifest.json. "
        "Run '.venv/bin/semiswing backtest' to generate the initial institutional audit manifest."
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    committed_hash = manifest.get("source_sha256", "")
    current_hash = compute_strategy_source_sha256(PROJECT_ROOT)

    assert committed_hash == current_hash, (
        f"STALE BACKTEST AUDIT DETECTED!\n"
        f"Committed manifest hash: {committed_hash}\n"
        f"Current source code hash: {current_hash}\n"
        f"Strategy source code has changed without regenerating the walk-forward backtest report.\n"
        f"Please run '.venv/bin/semiswing backtest' locally to update reports/backtests/audit_manifest.json."
    )


def test_validation_gate_logic_synthetic():
    """Unit test the mathematical gate evaluation logic on synthetic metric dictionaries."""
    cal_stats_pass = {"brier_skill_score": 0.035, "brier_calibrated": 0.240}
    ml_win = _make_dummy_result(ai_sharpe=1.85, ai_dsr=0.970, ai_dd=33.5)
    base_win = _make_dummy_result(ai_sharpe=1.75, ai_dsr=0.950, ai_dd=35.5)
    smh_bench = _make_dummy_result(ai_sharpe=1.34, ai_dd=35.74, oos_dd=45.14, bear_ret=-34.97, bear_dd=45.14)

    # 1. Winning baseline and ML should pass 100% of Core gates
    df, gates, all_pass = _build_institutional_gates(
        ml_win, base_win, smh_bench, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats_pass
    )
    assert all_pass is True
    for g in gates:
        assert g["Status"] == "PASS"

    # 2. Drawdown violation triggers FAIL on Gate 4a
    ml_high_dd = _make_dummy_result(ai_dd=38.5)
    _, gates_dd, pass_dd = _build_institutional_gates(
        ml_high_dd, base_win, smh_bench, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats_pass
    )
    assert pass_dd is False
    g4a = [g for g in gates_dd if "Gate 4a" in g["Gate"]][0]
    assert g4a["Status"] == "FAIL"

    # 3. Low Sharpe triggers FAIL on Gate 1
    ml_low_sr = _make_dummy_result(ai_sharpe=1.45)
    _, gates_sr, pass_sr = _build_institutional_gates(
        ml_low_sr, base_win, smh_bench, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats_pass
    )
    assert pass_sr is False
    g1 = [g for g in gates_sr if "Gate 1" in g["Gate"]][0]
    assert g1["Status"] == "FAIL"

    # 4. Low Brier Skill Score triggers FAIL on Gate 7
    cal_stats_fail = {"brier_skill_score": 0.005, "brier_calibrated": 0.248}
    _, gates_bss, pass_bss = _build_institutional_gates(
        ml_win, base_win, smh_bench, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats_fail
    )
    assert pass_bss is False
    g7 = [g for g in gates_bss if "Gate 7" in g["Gate"]][0]
    assert g7["Status"] == "FAIL"

    # 5. 2022 Bear Market violation triggers FAIL on Gate 6
    ml_bad_bear = _make_dummy_result(bear_ret=-45.0, bear_dd=48.0, bear_cash=50.0)
    _, gates_bear, pass_bear = _build_institutional_gates(
        ml_bad_bear, base_win, smh_bench, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats_pass
    )
    assert pass_bear is False
    g6 = [g for g in gates_bear if "Gate 6" in g["Gate"]][0]
    assert g6["Status"] == "FAIL"


def test_committed_manifest_passes_all_institutional_gates():
    """
    CI TIER 1 GUARD: Verify that the committed audit manifest achieves 100% PASS
    across all institutional gates for both Cash Swing and SMH Bull Core modes.
    """
    manifest_path = PROJECT_ROOT / "reports" / "backtests" / "audit_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest.get("all_gates_pass") is True, "Institutional Audit Manifest contains failing gates!"
    assert manifest.get("smh_core_gates_pass") is True, "SMH Bull Core Mode failed institutional gates!"
    assert manifest.get("cash_swing_gates_pass") is True, "Cash Swing Mode failed institutional gates!"

    for gate in manifest.get("gates_smh_core", []):
        assert gate["Status"] == "PASS", f"SMH Bull Core Gate Failed: {gate['Gate']} (Value: {gate['Value']})"

    for gate in manifest.get("gates_cash_swing", []):
        assert gate["Status"] == "PASS", f"Cash Swing Gate Failed: {gate['Gate']} (Value: {gate['Value']})"
