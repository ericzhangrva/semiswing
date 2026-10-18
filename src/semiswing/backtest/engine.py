"""Event-driven daily portfolio backtest engine and performance metrics (§6 & §9 of instruction.md)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import norm

from semiswing.config import StrategySettings


@dataclass
class Position:
    ticker: str
    entry_date: pd.Timestamp
    entry_price: float
    shares: float
    initial_shares: float
    atr_at_entry: float
    initial_stop: float
    current_stop: float
    tp1_price: float
    tp1_hit: bool = False
    highest_close: float = 0.0
    days_held: int = 0
    risk_per_share: float = 0.0
    tier: str = "HIGH"
    entry_prob: float = 0.65
    low_prob_streak: int = 0
    realized_pnl: float = 0.0
    entry_notional: float = 0.0
    entry_risk_dollars: float = 0.0
    shap_summary: str = ""


@dataclass
class BacktestResult:
    name: str
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics_overall: Dict[str, float] = field(default_factory=dict)
    metrics_2022_bear: Dict[str, float] = field(default_factory=dict)
    metrics_ai_era: Dict[str, float] = field(default_factory=dict)
    yearly_table: pd.DataFrame = field(default_factory=pd.DataFrame)


CORE_PRE2022_SEMI_TICKERS: tuple[str, ...] = (
    "NVDA",
    "AVGO",
    "AMD",
    "TSM",
    "ASML",
    "MU",
    "KLAC",
    "LRCX",
    "AMAT",
    "MRVL",
    "QCOM",
    "TXN",
    "ON",
    "MCHP",
    "INTC",
    "SNPS",
    "CDNS",
    "MPWR",
    "ADI",
    "NXPI",
    "TER",
    "WDC",
    "STX",
    "ANET",
    "COHR",
)


def _deflated_sharpe_prob(sharpe_ann: float, n_obs: int, skew: float, kurt: float, n_trials: int = 12) -> float:
    """Compute probabilistic/deflated Sharpe ratio against a benchmark of `n_trials` strategy variants."""
    if n_obs < 30 or np.isnan(sharpe_ann) or sharpe_ann <= 0.0:
        return 0.0
    sr_daily = sharpe_ann / np.sqrt(252.0)
    # Expected maximum Sharpe under null across n_trials
    euler_gamma = 0.5772156649
    z1 = norm.ppf(1.0 - 1.0 / max(n_trials, 2))
    z2 = norm.ppf(1.0 - 1.0 / (max(n_trials, 2) * np.e))
    sr0_daily = np.sqrt(1.0 / n_obs) * ((1.0 - euler_gamma) * z1 + euler_gamma * z2) if n_trials > 1 else 0.0

    denom_sq = 1.0 - skew * sr_daily + ((kurt - 1.0) / 4.0) * (sr_daily**2)
    denom = np.sqrt(max(denom_sq, 1e-8) / max(n_obs - 1, 1))
    z = (sr_daily - sr0_daily) / denom
    return float(norm.cdf(z))


def compute_period_metrics(
    eq_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
    n_trials: int = 12,
) -> Dict[str, float]:
    """Compute portfolio & trade statistics over a specified date window using excess returns over 3M T-Bills."""
    sub_eq = eq_df.copy()
    if start_date:
        sub_eq = sub_eq[sub_eq["date"] >= pd.to_datetime(start_date)]
    if end_date:
        sub_eq = sub_eq[sub_eq["date"] <= pd.to_datetime(end_date)]

    if len(sub_eq) < 2:
        return {
            "total_return_pct": 0.0,
            "cagr_pct": 0.0,
            "sharpe": 0.0,
            "deflated_sharpe_prob": 0.0,
            "sortino": 0.0,
            "max_dd_pct": 0.0,
            "cash_days_pct": 100.0,
            "trades": 0,
            "win_rate_pct": 0.0,
            "profit_factor": 0.0,
            "avg_r": 0.0,
        }

    rets = sub_eq["equity"].pct_change().dropna()
    if "rf_daily" in sub_eq.columns:
        rf_daily = sub_eq["rf_daily"].iloc[1:].fillna(0.0)
        excess_rets = rets - rf_daily
    else:
        excess_rets = rets

    start_val = float(sub_eq["equity"].iloc[0])
    end_val = float(sub_eq["equity"].iloc[-1])
    tot_ret = (end_val / start_val) - 1.0
    n_years = max(len(sub_eq) / 252.0, 1e-4)
    cagr = (end_val / start_val) ** (1.0 / n_years) - 1.0 if end_val > 0 else -1.0

    # Excess return volatility, Sharpe, and Sortino over 3M T-Bill rate
    std_ex = float(excess_rets.std())
    mean_ex = float(excess_rets.mean())
    sharpe = (mean_ex / std_ex) * np.sqrt(252.0) if std_ex > 1e-7 else 0.0

    downside = excess_rets[excess_rets < 0]
    down_std = float(np.sqrt(np.mean(downside**2))) if len(downside) > 0 else 0.0
    sortino = (mean_ex / down_std) * np.sqrt(252.0) if down_std > 1e-7 else 0.0

    skew = float(excess_rets.skew()) if len(excess_rets) > 10 and std_ex > 1e-7 else 0.0
    kurt = float(excess_rets.kurtosis() + 3.0) if len(excess_rets) > 10 and std_ex > 1e-7 else 3.0
    dsr_prob = _deflated_sharpe_prob(sharpe, len(excess_rets), skew, kurt, n_trials=n_trials)

    peaks = sub_eq["equity"].cummax()
    dd = (sub_eq["equity"] / peaks) - 1.0
    max_dd = float(dd.min())
    cash_days_pct = float((sub_eq["n_positions"] == 0).mean() * 100.0)

    sub_tr = trades_df.copy()
    if not sub_tr.empty:
        if start_date:
            sub_tr = sub_tr[sub_tr["entry_date"] >= pd.to_datetime(start_date)]
        if end_date:
            sub_tr = sub_tr[sub_tr["entry_date"] <= pd.to_datetime(end_date)]

    n_trades = len(sub_tr)
    if n_trades > 0:
        wins = sub_tr[sub_tr["net_pnl"] > 0]["net_pnl"].sum()
        losses = abs(sub_tr[sub_tr["net_pnl"] < 0]["net_pnl"].sum())
        win_rate = float((sub_tr["net_pnl"] > 0).mean() * 100.0)
        pf = float(wins / losses) if losses > 1e-6 else (10.0 if wins > 0 else 0.0)
        avg_r = float(sub_tr["r_multiple"].mean())
    else:
        win_rate = 0.0
        pf = 0.0
        avg_r = 0.0

    return {
        "total_return_pct": round(tot_ret * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "sharpe": round(sharpe, 2),
        "deflated_sharpe_prob": round(dsr_prob, 3),
        "sortino": round(sortino, 2),
        "max_dd_pct": round(abs(max_dd) * 100.0, 2),
        "cash_days_pct": round(cash_days_pct, 1),
        "trades": int(n_trades),
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": round(pf, 2),
        "avg_r": round(avg_r, 2),
    }


def run_portfolio_backtest(
    panel: pd.DataFrame,
    strategy: StrategySettings,
    mode: str = "baseline",
    start_date: str | None = None,
    bull_core_smh: bool = False,
    allowed_tickers: set[str] | tuple[str, ...] | None = None,
) -> BacktestResult:
    """
    Simulate the SemiSwing portfolio on daily bars starting from `start_date` (default: oos_start_date).
    mode in {"baseline", "baseline_fixed20", "ml"}.
    - Unused cash accrues daily 3-Month Treasury Bill interest (`cash_rate_apy / 252`).
    - When `bull_core_smh=True`, unallocated capital during `smh_secular_bull == 1` is swept into `SMH`
      (and into T-Bill cash whenever `smh_secular_bull == 0`).
    - When `allowed_tickers` is provided, swing entries are restricted to that ticker subset (used to
      compare pre-2022 pure SMH/SOXX semiconductor constituents vs. the expanded 50-stock AI universe).
    """
    rcfg = strategy.risk
    b_start = pd.to_datetime(start_date or strategy.backtest.oos_start_date)
    cost_rate = (strategy.backtest.commission_bps + strategy.backtest.slippage_bps) / 10000.0
    allowed_set = set(allowed_tickers) if allowed_tickers is not None else None

    sig_col = "ml_signal" if mode == "ml" else "baseline_signal"
    score_col = "ml_score" if mode == "ml" else "baseline_score"
    tier_col = "ml_tier" if mode == "ml" else "baseline_tier"
    prob_col = "ml_prob" if mode == "ml" else "baseline_prob"

    df = panel[panel["date"] >= b_start].sort_values(["date", "ticker"]).copy()
    dates = np.sort(df["date"].unique())

    cash = float(rcfg.paper_equity)
    open_positions: Dict[str, Position] = {}
    cooldown_until: Dict[str, int] = {}
    streak_stops = 0
    pause_until_idx = -1
    prev_regime_on = 0
    prev_secular_bull = 0
    pending_candidates: List[dict] = []

    eq_rows = []
    closed_trades = []
    smh_prev_close: float = np.nan

    # Group panel by date for fast event-driven loop
    by_date = {d: grp.set_index("ticker") for d, grp in df.groupby("date", sort=False)}

    for d_idx, dt in enumerate(dates):
        day_slice = by_date[dt]
        regime_today = int(day_slice["regime_on"].iloc[0]) if len(day_slice) > 0 else 0
        secular_bull_today = (
            int(day_slice["smh_secular_bull"].iloc[0])
            if ("smh_secular_bull" in day_slice.columns and len(day_slice) > 0)
            else regime_today
        )
        cash_rate_apy = (
            float(day_slice["cash_rate_apy"].iloc[0])
            if ("cash_rate_apy" in day_slice.columns and len(day_slice) > 0)
            else 0.035
        )
        if np.isnan(cash_rate_apy):
            cash_rate_apy = 0.035
        smh_daily_ret = (
            float(day_slice["smh_daily_ret"].iloc[0])
            if ("smh_daily_ret" in day_slice.columns and len(day_slice) > 0)
            else 0.0
        )
        if np.isnan(smh_daily_ret):
            smh_daily_ret = 0.0

        # 0. Accrue return on unallocated cash from previous close to today's close:
        #    - Mode 1 (bull_core_smh=False): always accrues daily 3-Month T-Bill interest (DTB3 / 252)
        #    - Mode 2 (bull_core_smh=True): accrues SMH return when prev_secular_bull == 1, or T-Bill interest otherwise
        if cash > 0:
            if bull_core_smh and prev_secular_bull == 1 and d_idx > 0:
                cash *= 1.0 + smh_daily_ret
            else:
                cash *= 1.0 + (cash_rate_apy / 252.0)

        # 1. MORNING (09:30 ET OPEN):
        # (a) Check overnight gaps below stop on existing positions
        gap_exits: List[tuple[str, float, str]] = []
        for ticker, pos in list(open_positions.items()):
            if ticker not in day_slice.index:
                continue
            row = day_slice.loc[ticker]
            o_px = float(row["open"])
            if o_px <= pos.current_stop:
                gap_exits.append((ticker, o_px, "STOP_GAP"))

        for ticker, raw_exit_px, reason in gap_exits:
            pos = open_positions.pop(ticker)
            exit_px = raw_exit_px * (1.0 - cost_rate)
            proceeds = pos.shares * exit_px
            remaining_basis = pos.shares * pos.entry_price
            cash += proceeds
            total_net_pnl = pos.realized_pnl + (proceeds - remaining_basis)
            r_mult = total_net_pnl / max(pos.entry_risk_dollars, 1.0)
            closed_trades.append(
                {
                    "ticker": ticker,
                    "tier": pos.tier,
                    "entry_date": pos.entry_date,
                    "exit_date": dt,
                    "days_held": pos.days_held + 1,
                    "entry_price": round(pos.entry_price, 2),
                    "exit_price": round(exit_px, 2),
                    "initial_stop": round(pos.initial_stop, 2),
                    "tp1_hit": pos.tp1_hit,
                    "net_pnl": round(total_net_pnl, 2),
                    "return_pct": round((total_net_pnl / max(pos.entry_notional, 1.0)) * 100.0, 2),
                    "r_multiple": round(r_mult, 2),
                    "exit_reason": reason,
                    "entry_prob": round(pos.entry_prob, 3),
                    "shap_summary": pos.shap_summary,
                }
            )
            if total_net_pnl < 0:
                cooldown_until[ticker] = d_idx + rcfg.cooldown_days
                streak_stops += 1
                if streak_stops >= rcfg.streak_stop_limit:
                    pause_until_idx = d_idx + rcfg.cooldown_days
                    streak_stops = 0

        # (b) Execute pending candidate orders at Market Open (Next-Day Open Fill)
        # Check morning pre-market sector gap-down circuit breaker (09:15-09:30 ET)
        smh_open = float(day_slice.loc["SMH", "open"]) if "SMH" in day_slice.index else np.nan
        if not np.isnan(smh_prev_close) and smh_prev_close > 0 and not np.isnan(smh_open):
            smh_gap_down = (smh_open / smh_prev_close) - 1.0
            if smh_gap_down < -strategy.regime.premarket_gap_down_max:
                pending_candidates.clear()

        if d_idx > pause_until_idx and pending_candidates and len(open_positions) < rcfg.max_positions:
            open_pos_val = sum(
                pos.shares * (float(day_slice.loc[t, "open"]) if t in day_slice.index else pos.entry_price)
                for t, pos in open_positions.items()
            )
            open_equity = cash + open_pos_val
            open_risk_dollars = sum(
                max(0.0, (pos.entry_price - pos.current_stop) * pos.shares)
                for pos in open_positions.values()
            )

            pending_candidates.sort(key=lambda x: x["score"], reverse=True)
            for cand in pending_candidates:
                if len(open_positions) >= rcfg.max_positions:
                    break
                ticker = cand["ticker"]
                if ticker in open_positions:
                    continue
                if cooldown_until.get(ticker, -1) > d_idx:
                    continue
                if ticker not in day_slice.index:
                    continue

                row = day_slice.loc[ticker]
                o_px = float(row["open"])
                c_prev = cand["close"]
                atr_sig = cand["atr"]
                if np.isnan(o_px) or o_px <= 0 or np.isnan(atr_sig) or atr_sig <= 0:
                    continue

                # Gap-up protection filter: do not chase if stock opened > 1.0 ATR above signal close or > 4% gap
                if o_px > (c_prev + 1.0 * atr_sig) or (c_prev > 0 and (o_px / c_prev) > 1.04):
                    continue

                macro_s = float(cand.get("macro_scalar", 1.0))
                if macro_s <= 0.0:
                    continue

                tier = cand["tier"]
                risk_frac = rcfg.risk_per_trade if tier == "HIGH" else rcfg.risk_per_trade_medium
                max_open_r = rcfg.max_open_risk
                pos_cap_pct = rcfg.max_pos_pct

                risk_budget = open_equity * risk_frac * macro_s
                if (open_risk_dollars + risk_budget) > (open_equity * max_open_r):
                    continue

                entry_px = o_px * (1.0 + cost_rate)
                stop_dist = rcfg.stop_atr * atr_sig
                backstop_dist = entry_px * rcfg.backstop
                effective_stop_dist = min(stop_dist, backstop_dist)
                stop_px = entry_px - effective_stop_dist
                tp1_px = entry_px + rcfg.tp1_atr * atr_sig

                desired_shares = risk_budget / max(effective_stop_dist, 1e-4)
                max_notional = min(open_equity * pos_cap_pct * macro_s, cash * 0.99)
                shares = min(desired_shares, max_notional / entry_px)
                notional = shares * entry_px

                if notional < 100.0 or shares <= 0:
                    continue

                cash -= notional
                actual_risk_dollars = shares * effective_stop_dist
                open_risk_dollars += actual_risk_dollars

                open_positions[ticker] = Position(
                    ticker=ticker,
                    entry_date=dt,
                    entry_price=entry_px,
                    shares=shares,
                    initial_shares=shares,
                    atr_at_entry=atr_sig,
                    initial_stop=stop_px,
                    current_stop=stop_px,
                    tp1_price=tp1_px,
                    tp1_hit=False,
                    highest_close=entry_px,
                    days_held=0,
                    risk_per_share=effective_stop_dist,
                    tier=tier,
                    entry_prob=cand["prob"],
                    entry_notional=notional,
                    entry_risk_dollars=actual_risk_dollars,
                    shap_summary=cand["shap_summary"],
                )

        # 2. INTRADAY & EOD: Process price action for all currently open positions
        to_close: List[tuple[str, float, str]] = []

        for ticker, pos in list(open_positions.items()):
            if ticker not in day_slice.index:
                continue
            row = day_slice.loc[ticker]
            o_px = float(row["open"])
            h_px = float(row["high"])
            l_px = float(row["low"])
            c_px = float(row["close"])
            atr_now = float(row["atr"]) if not np.isnan(row["atr"]) else pos.atr_at_entry
            pos.days_held += 1

            # (a) Check hard stop hit intraday
            if l_px <= pos.initial_stop:
                to_close.append((ticker, pos.initial_stop, "STOP"))
                continue

            # (b) Check Stage-1 Take Profit on partial shares
            if not pos.tp1_hit and h_px >= pos.tp1_price:
                fill_px = max(pos.tp1_price, o_px) * (1.0 - cost_rate)
                sell_sh = pos.shares * rcfg.tp1_fraction
                proceeds = sell_sh * fill_px
                cost_basis = sell_sh * pos.entry_price
                cash += proceeds
                pos.realized_pnl += proceeds - cost_basis
                pos.shares -= sell_sh
                pos.tp1_hit = True
                pos.current_stop = max(pos.current_stop, pos.entry_price)

            # (c) Check EOD trailing stop on close
            if c_px <= pos.current_stop:
                to_close.append((ticker, c_px, "TRAIL_STOP_EOD"))
                continue

            # Update highest close and trailing stop for next bar
            pos.highest_close = max(pos.highest_close, c_px)
            unrealized_r = (c_px - pos.entry_price) / max(pos.risk_per_share, 1e-6)

            if unrealized_r >= rcfg.breakeven_trigger_r:
                pos.current_stop = max(pos.current_stop, pos.entry_price)
            if pos.tp1_hit or unrealized_r >= 1.5:
                chandelier = pos.highest_close - rcfg.trail_atr * atr_now
                pos.current_stop = max(pos.current_stop, chandelier)

            # Check EOD exit rules:
            if prev_secular_bull == 0 and prev_regime_on == 0:
                to_close.append((ticker, c_px, "REGIME_OFF"))
                continue

            if int(row["days_to_earnings"]) <= 1 and unrealized_r < 0.25 and not pos.tp1_hit:
                to_close.append((ticker, c_px, "EARNINGS_EXIT"))
                continue

            if pos.days_held == rcfg.early_time_stop_day and unrealized_r < rcfg.early_time_stop_min_r:
                to_close.append((ticker, c_px, "TIME_STOP_12D"))
                continue
            if pos.days_held >= rcfg.time_stop and not pos.tp1_hit and unrealized_r < 0.50:
                to_close.append((ticker, c_px, "TIME_STOP_25D"))
                continue

        # Execute full position exits
        for ticker, raw_exit_px, reason in to_close:
            pos = open_positions.pop(ticker)
            exit_px = raw_exit_px * (1.0 - cost_rate)
            proceeds = pos.shares * exit_px
            remaining_basis = pos.shares * pos.entry_price
            cash += proceeds
            total_net_pnl = pos.realized_pnl + (proceeds - remaining_basis)
            r_mult = total_net_pnl / max(pos.entry_risk_dollars, 1.0)

            closed_trades.append(
                {
                    "ticker": ticker,
                    "tier": pos.tier,
                    "entry_date": pos.entry_date,
                    "exit_date": dt,
                    "days_held": pos.days_held,
                    "entry_price": round(pos.entry_price, 2),
                    "exit_price": round(exit_px, 2),
                    "initial_stop": round(pos.initial_stop, 2),
                    "tp1_hit": pos.tp1_hit,
                    "net_pnl": round(total_net_pnl, 2),
                    "return_pct": round((total_net_pnl / max(pos.entry_notional, 1.0)) * 100.0, 2),
                    "r_multiple": round(r_mult, 2),
                    "exit_reason": reason,
                    "entry_prob": round(pos.entry_prob, 3),
                    "shap_summary": pos.shap_summary,
                }
            )

            if reason in ("STOP", "STOP_GAP") and total_net_pnl < 0:
                cooldown_until[ticker] = d_idx + rcfg.cooldown_days
                streak_stops += 1
                if streak_stops >= rcfg.streak_stop_limit:
                    pause_until_idx = d_idx + rcfg.cooldown_days
                    streak_stops = 0
            elif total_net_pnl > 0:
                streak_stops = 0

        # 3. EOD: Generate candidate signals for Next-Day Open execution
        pending_candidates = []
        if d_idx > pause_until_idx and len(open_positions) < rcfg.max_positions:
            candidates = day_slice[day_slice[sig_col] == 1].copy()
            if allowed_set is not None and not candidates.empty:
                candidates = candidates[candidates.index.isin(allowed_set)]
            if not candidates.empty:
                candidates = candidates.sort_values(score_col, ascending=False)
                for ticker, row in candidates.iterrows():
                    c_px = float(row["close"])
                    atr_val = float(row["atr"])
                    if np.isnan(c_px) or np.isnan(atr_val) or atr_val <= 0:
                        continue
                    macro_val = float(row["macro_scalar"]) if "macro_scalar" in row else 1.0
                    pending_candidates.append(
                        {
                            "ticker": ticker,
                            "close": c_px,
                            "atr": atr_val,
                            "tier": str(row[tier_col]),
                            "prob": float(row[prob_col]),
                            "score": float(row[score_col]),
                            "macro_scalar": macro_val,
                            "shap_summary": str(row.get("ml_shap", "")),
                        }
                    )

        # End-of-day mark-to-market
        eod_pos_val = sum(
            pos.shares * (float(day_slice.loc[t, "close"]) if t in day_slice.index else pos.entry_price)
            for t, pos in open_positions.items()
        )
        eod_equity = cash + eod_pos_val
        eq_rows.append(
            {
                "date": dt,
                "equity": eod_equity,
                "cash": cash,
                "n_positions": len(open_positions),
                "regime_on": regime_today,
                "rf_daily": cash_rate_apy / 252.0,
            }
        )
        prev_regime_on = regime_today
        prev_secular_bull = secular_bull_today
        if "SMH" in day_slice.index:
            smh_c = float(day_slice.loc["SMH", "close"])
            if not np.isnan(smh_c) and smh_c > 0:
                smh_prev_close = smh_c

    eq_df = pd.DataFrame(eq_rows)
    trades_df = pd.DataFrame(closed_trades)

    res = BacktestResult(name=mode, equity_curve=eq_df, trades=trades_df)
    res.metrics_overall = compute_period_metrics(eq_df, trades_df)
    res.metrics_2022_bear = compute_period_metrics(eq_df, trades_df, "2022-01-01", "2022-12-31")
    res.metrics_ai_era = compute_period_metrics(eq_df, trades_df, strategy.backtest.ai_era_start, None)

    # Yearly breakdown
    if not eq_df.empty:
        years = sorted(eq_df["date"].dt.year.unique())
        y_rows = []
        for yr in years:
            m = compute_period_metrics(eq_df, trades_df, f"{yr}-01-01", f"{yr}-12-31")
            y_rows.append({"year": yr, **m})
        res.yearly_table = pd.DataFrame(y_rows)

    return res
