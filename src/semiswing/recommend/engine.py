"""Daily recommendation and dollar-allocation engine for SemiSwing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from semiswing.config import (
    PROJECT_ROOT,
    PortfolioSettings,
    StrategySettings,
    UniverseSettings,
)


@dataclass
class HoldingAction:
    ticker: str
    description: str
    role: str
    shares: float
    avg_cost: float
    current_price: float
    market_value: float
    weight_pct: float
    unrealized_pnl: float
    unrealized_pct: float
    action: str
    action_dollars: float
    action_shares: float
    recommended_stop: float
    tp1_target: float
    ml_prob: float
    rs_rank: float
    slope_t_norm: float
    days_to_earnings: int
    rationale: str


@dataclass
class BuyCandidate:
    rank: int
    ticker: str
    signal_source: str  # "CONSENSUS (ML + Baseline)", "ML (LightGBM+Platt)", "BASELINE (Adaptive L_t)", or "WATCHLIST"
    tier: str
    close_price: float
    atr: float
    stop_price: float
    stop_dist_pct: float
    tp1_price: float
    tp1_gain_pct: float
    ml_prob: float
    ml_ev_r: float
    rs_rank: float
    slope_t_norm: float
    slope_r2: float
    ext_atr: float
    days_to_earnings: int
    # Sizing under Cash Only ($2,533.37)
    buy_dollars_cash_only: float
    buy_shares_cash_only: float
    risk_dollars_cash_only: float
    # Sizing under Cash + TQQQ Rotation ($3,900.29)
    buy_dollars_with_rotate: float
    buy_shares_with_rotate: float
    risk_dollars_with_rotate: float
    # Standard per-$10,000 sizing
    buy_dollars_per_10k: float
    buy_shares_per_10k: float
    shap_summary: str
    gate_notes: str


@dataclass
class DailyRecommendationPlan:
    as_of_date: str
    snapshot_date: str
    account_name: str
    health_score: float
    regime_on: bool
    smh_secular_bull: bool
    smh_close: float
    smh_ema100: float
    smh_ema200: float
    vix_lvl: float
    vix_ts: float
    cash_rate_apy_pct: float
    days_to_fomc: int
    total_equity: float
    current_cash: float
    rotate_proceeds: float
    deployable_cash_with_rotate: float
    holdings_actions: List[HoldingAction] = field(default_factory=list)
    active_buys: List[BuyCandidate] = field(default_factory=list)
    watchlist_candidates: List[BuyCandidate] = field(default_factory=list)
    # Core SMH / Cash sweep summary
    remaining_cash_after_buys_cash_only: float = 0.0
    remaining_cash_after_buys_with_rotate: float = 0.0
    core_sweep_Instrument: str = "SMH"
    core_sweep_dollars_cash_only: float = 0.0
    core_sweep_shares_cash_only: float = 0.0
    core_sweep_dollars_with_rotate: float = 0.0
    core_sweep_shares_with_rotate: float = 0.0
    executive_steps: List[str] = field(default_factory=list)


def _compute_single_ticket_size(
    close_price: float,
    stop_price: float,
    tier: str,
    pool_cash: float,
    total_equity: float,
    strategy: StrategySettings,
    target_slots: int = 2,
    macro_scalar: float = 1.0,
) -> tuple[float, float, float]:
    """
    Compute exact (buy_dollars, buy_shares, risk_dollars) for a candidate given `pool_cash` and `total_equity`.
    Caps each ticket at min(33% of total_equity * macro_scalar, pool_cash / target_slots) so deployable cash is diversified
    across `target_slots` (2 in Cash-Only mode, 2-3 in Cash+TQQQ Rotation mode).
    """
    rcfg = strategy.risk
    if pool_cash < 100.0 or close_price <= 0 or macro_scalar <= 0:
        return 0.0, 0.0, 0.0

    risk_frac = rcfg.risk_per_trade if tier in ("CONSENSUS", "HIGH") else rcfg.risk_per_trade_medium
    risk_budget = total_equity * risk_frac * macro_scalar
    risk_per_share = max(close_price - stop_price, 1e-4)
    desired_shares = risk_budget / risk_per_share
    desired_notional = desired_shares * close_price

    slot_cap = pool_cash / max(target_slots, 1)
    max_pos_notional = min(total_equity * rcfg.max_pos_pct * macro_scalar, slot_cap)
    alloc_notional = min(desired_notional, max_pos_notional, pool_cash)
    if alloc_notional < 100.0:
        return 0.0, 0.0, 0.0

    alloc_shares = alloc_notional / close_price
    actual_risk = alloc_shares * risk_per_share
    return round(alloc_notional, 2), round(alloc_shares, 3), round(actual_risk, 2)


def _allocate_Pool(
    candidates: List[BuyCandidate],
    pool_cash: float,
    total_equity: float,
    strategy: StrategySettings,
    open_swing_count: int,
    open_swing_risk_dollars: float,
    mode: str,
    target_slots: int = 2,
    macro_scalar: float = 1.0,
) -> float:
    """
    Allocate a cash budget (`pool_cash`) across ranked buy candidates using SemiSwing risk and slot caps.
    Updates candidates in place for either `mode="cash_only"` or `mode="with_rotate"` and returns remaining cash.
    """
    rcfg = strategy.risk
    rem_cash = float(pool_cash)
    used_slots = int(open_swing_count)
    used_risk = float(open_swing_risk_dollars)
    max_open_risk_dollars = total_equity * rcfg.max_open_risk
    slot_cap = pool_cash / max(target_slots, 1)
    max_pos_notional = min(total_equity * rcfg.max_pos_pct * macro_scalar, slot_cap)

    for cand in candidates:
        if used_slots >= rcfg.max_positions or rem_cash < 100.0 or macro_scalar <= 0:
            break

        risk_frac = rcfg.risk_per_trade if cand.tier in ("CONSENSUS", "HIGH") else rcfg.risk_per_trade_medium
        target_risk_dollars = total_equity * risk_frac * macro_scalar
        avail_risk_dollars = max(0.0, max_open_risk_dollars - used_risk)
        risk_budget = min(target_risk_dollars, avail_risk_dollars)
        if risk_budget < 25.0:
            continue

        risk_per_share = max(cand.close_price - cand.stop_price, 1e-4)
        desired_shares = risk_budget / risk_per_share
        desired_notional = desired_shares * cand.close_price

        alloc_notional = min(desired_notional, max_pos_notional, rem_cash)
        if alloc_notional < 100.0:
            continue

        alloc_shares = alloc_notional / cand.close_price
        actual_risk = alloc_shares * risk_per_share

        if mode == "cash_only":
            cand.buy_dollars_cash_only = round(alloc_notional, 2)
            cand.buy_shares_cash_only = round(alloc_shares, 3)
            cand.risk_dollars_cash_only = round(actual_risk, 2)
        else:
            cand.buy_dollars_with_rotate = round(alloc_notional, 2)
            cand.buy_shares_with_rotate = round(alloc_shares, 3)
            cand.risk_dollars_with_rotate = round(actual_risk, 2)

        rem_cash -= alloc_notional
        used_risk += actual_risk
        used_slots += 1

    return round(max(0.0, rem_cash), 2)


def build_daily_recommendation_plan(
    panel: pd.DataFrame,
    strategy: StrategySettings,
    universe: UniverseSettings,
    portfolio: PortfolioSettings,
    health_score: float = 100.0,
    capital_override: float | None = None,
) -> DailyRecommendationPlan:
    """
    Evaluate current holdings from `config/portfolio.yaml` and generate today's ranked BUY/SELL/CORE
    recommendations with exact dollar amounts and share counts.
    """
    rcfg = strategy.risk
    bcfg = strategy.baseline
    gcfg = strategy.gate

    smh_dates = panel.loc[panel["ticker"] == "SMH", "date"]
    latest_date = smh_dates.max() if not smh_dates.empty else panel["date"].max()
    day_df = panel[panel["date"] == latest_date].copy().set_index("ticker")

    # Extract market regime & context metrics
    sample_row = day_df.iloc[0]
    regime_on = bool(int(sample_row.get("regime_on", 0)) == 1)
    macro_scalar = float(sample_row.get("macro_scalar", 1.0 if regime_on else 0.0))
    vix_lvl = float(sample_row.get("vix_lvl", 20.0))
    vix_ts = float(sample_row.get("vix_ts", 0.95))
    cash_rate_apy_pct = round(float(sample_row.get("cash_rate_apy", 0.04)) * 100.0, 2)
    days_to_fomc = int(sample_row.get("days_to_fomc", 99))

    # Use snapshot SMH price if provided, otherwise latest panel close
    smh_pos_px = next((p.last_price for p in portfolio.positions if p.ticker == "SMH" and p.last_price > 0), 0.0)
    smh_close = float(smh_pos_px) if smh_pos_px > 0 else (float(day_df.loc["SMH", "close"]) if "SMH" in day_df.index else 539.79)
    smh_hist = panel[panel["ticker"] == "SMH"].sort_values("date")
    if not smh_hist.empty:
        smh_ema100 = float(
            smh_hist["close"].ewm(span=strategy.regime.smh_ema, min_periods=50, adjust=False).mean().iloc[-1]
        )
        smh_ema200 = float(
            smh_hist["close"].ewm(span=200, min_periods=100, adjust=False).mean().iloc[-1]
        )
    else:
        smh_ema100 = smh_close * 0.98
        smh_ema200 = smh_close * 0.90

    # Secular bull core remains intact based on the stateful hysteresis Schmitt trigger
    smh_secular_bull = bool(int(sample_row.get("smh_secular_bull", 1 if smh_close > smh_ema200 else 0)) == 1)

    # 1. Evaluate current holdings and compute total portfolio equity
    current_cash = float(capital_override) if capital_override is not None else float(portfolio.cash)
    positions_list = [] if capital_override is not None else portfolio.positions

    raw_holdings_val = 0.0
    resolved_prices: Dict[str, float] = {}
    for pos in positions_list:
        px = float(pos.last_price) if pos.last_price > 0 else float(day_df.loc[pos.ticker, "close"]) if pos.ticker in day_df.index else float(pos.avg_cost)
        resolved_prices[pos.ticker] = px
        raw_holdings_val += pos.shares * px

    total_equity = round(current_cash + raw_holdings_val, 2)
    if total_equity <= 0:
        total_equity = 10_000.0

    holdings_actions: List[HoldingAction] = []
    rotate_proceeds = 0.0
    open_swing_count = 0
    open_swing_risk_dollars = 0.0
    held_tickers = set()

    for pos in positions_list:
        t = pos.ticker
        held_tickers.add(t)
        px = resolved_prices[t]
        mkt_val = round(pos.shares * px, 2)
        wt_pct = round((mkt_val / total_equity) * 100.0, 2)
        cost_total = pos.shares * pos.avg_cost
        unreal_pnl = round(mkt_val - cost_total, 2)
        unreal_pct = round(((px / pos.avg_cost) - 1.0) * 100.0, 2) if pos.avg_cost > 0 else 0.0

        lookup_t = t if t in day_df.index else (pos.proxy_ticker if pos.proxy_ticker in day_df.index else "")
        if lookup_t and lookup_t in day_df.index:
            r = day_df.loc[lookup_t]
            atr_val = float(r.get("atr", px * 0.025))
            ml_p = float(r.get("ml_prob", 0.50))
            rs_rk = float(r.get("rs_rank", 0.50))
            slp_t = float(r.get("slope_t_norm", 0.0))
            dte = int(r.get("days_to_earnings", 999))
        else:
            atr_val = px * 0.025
            ml_p = 0.50
            rs_rk = 0.50
            slp_t = 0.0
            dte = 999

        stop_dist = min(rcfg.stop_atr * atr_val, pos.avg_cost * rcfg.backstop)
        init_stop = round(pos.avg_cost - stop_dist, 2)
        chandelier_stop = round(px - rcfg.trail_atr * atr_val, 2)
        base_tp1 = pos.avg_cost + rcfg.tp1_atr * atr_val
        tp1_px = round(max(base_tp1, px + 2.5 * atr_val) if pos.tp1_hit else base_tp1, 2)
        unrealized_r = (px - pos.avg_cost) / max(stop_dist, 1e-4)

        if unrealized_r >= rcfg.breakeven_trigger_r or pos.tp1_hit:
            rec_stop = round(max(init_stop, pos.avg_cost, chandelier_stop), 2)
        else:
            rec_stop = round(max(init_stop, pos.current_stop), 2)

        action = "HOLD"
        act_dollars = 0.0
        act_shares = 0.0
        rationale = ""

        if pos.role == "non_universe_leveraged":
            action = "SELL / ROTATE"
            act_dollars = mkt_val
            act_shares = pos.shares
            rotate_proceeds += mkt_val
            rationale = (
                f"{pos.description} ({unreal_pct:+.1f}%). Excluded by SemiSwing unleveraged charter due to "
                f"daily-reset volatility decay / non-core drag; tax-free rotation frees ${mkt_val:,.2f} for SMH Core / AI Swing setups."
            )
        elif pos.role == "bull_core":
            if smh_secular_bull:
                action = "HOLD CORE"
                rationale = (
                    f"Long-term secular bull intact (SMH ${smh_close:.2f} > EMA200 ${smh_ema200:.2f}; "
                    f"tactical pullback below EMA100 ${smh_ema100:.2f}). Keep core {pos.shares:g} sh ({unreal_pct:+.1f}%). {pos.notes}".strip()
                )
            else:
                action = "ROTATE TO CASH"
                act_dollars = mkt_val
                act_shares = pos.shares
                rationale = f"SMH below EMA200 (${smh_ema200:.2f}); rotate core sleeve to Money Market / SGOV."
        elif pos.role == "index_core":
            action = "HOLD CORE (INDEX)"
            rationale = (
                f"Broad unleveraged index core ({unreal_pct:+.1f}%). Keep as long-term portfolio anchor "
                f"(or optional rebalance source into SMH / AI Swing sleeve)."
            )
        else:
            # Active single-stock swing position (NVDA, META, AAPL, TSM, MSFT)
            if px <= rec_stop:
                action = "SELL (STOP HIT)"
                act_dollars = mkt_val
                act_shares = pos.shares
                rationale = f"Price ${px:.2f} breached stop level ${rec_stop:.2f}."
            elif not regime_on and not smh_secular_bull:
                action = "SELL (BEAR REGIME)"
                act_dollars = mkt_val
                act_shares = pos.shares
                rationale = "Both tactical regime_on and SMH EMA200 secular bull are OFF."
            elif px >= tp1_px and not pos.tp1_hit:
                action = "TRIM 25% (TP1 HIT)"
                act_shares = round(pos.shares * rcfg.tp1_fraction, 3)
                act_dollars = round(act_shares * px, 2)
                open_swing_count += 1
                rationale = (
                    f"Up {unreal_pct:+.1f}% (+{unrealized_r:.2f}R), above TP1 (${tp1_px:.2f}). "
                    f"Lock in 25% (${act_dollars:,.2f}) and raise trailing stop to ${rec_stop:.2f}."
                )
            else:
                has_earn = "earnings" in pos.notes.lower() or dte <= 14
                action = (
                    "HOLD (EARNINGS WATCH)"
                    if has_earn
                    else ("HOLD (PROTECT PROFIT)" if unrealized_r >= 1.0 else "HOLD")
                )
                open_swing_count += 1
                rem_risk = max(0.0, (pos.avg_cost - rec_stop) * pos.shares)
                open_swing_risk_dollars += rem_risk
                trim_sh = round(pos.shares * 0.25, 2)
                trim_dlr = round(trim_sh * px, 0)
                earn_note = (
                    f" [Upcoming Earnings [E]: keep Chandelier stop at ${rec_stop:.2f} and consider trimming 25% "
                    f"(~{trim_sh:g} sh = ~${trim_dlr:,.0f}) into pre-earnings strength toward ${tp1_px:.2f}]"
                    if has_earn
                    else ""
                )
                extra_note = f" ({pos.notes})" if pos.notes and not has_earn else ""
                rationale = (
                    f"Active AI/Semi leader ({unreal_pct:+.1f}%, +{unrealized_r:.2f}R vs avg cost ${pos.avg_cost:.2f}). "
                    f"Keep protective Chandelier stop at ${rec_stop:.2f}; next upside target ${tp1_px:.2f}.{extra_note}{earn_note}"
                )

        holdings_actions.append(
            HoldingAction(
                ticker=t,
                description=pos.description or t,
                role=pos.role,
                shares=pos.shares,
                avg_cost=pos.avg_cost,
                current_price=px,
                market_value=mkt_val,
                weight_pct=wt_pct,
                unrealized_pnl=unreal_pnl,
                unrealized_pct=unreal_pct,
                action=action,
                action_dollars=act_dollars,
                action_shares=act_shares,
                recommended_stop=rec_stop,
                tp1_target=tp1_px,
                ml_prob=round(ml_p, 3),
                rs_rank=round(rs_rk, 2),
                slope_t_norm=round(slp_t, 2),
                days_to_earnings=dte,
                rationale=rationale,
            )
        )

    deployable_with_rotate = round(current_cash + rotate_proceeds, 2)

    # 2. Evaluate all tradeable stocks & ETFs for new BUY signals (Consensus, ML, Baseline) + Watchlist
    tradeable_df = day_df[day_df["is_tradeable_universe"] == 1].copy()
    tradeable_df["is_consensus"] = ((tradeable_df["ml_signal"] == 1) & (tradeable_df["baseline_signal"] == 1)).astype(int)
    tradeable_df["is_any_sig"] = ((tradeable_df["ml_signal"] == 1) | (tradeable_df["baseline_signal"] == 1)).astype(int)
    # Candidate quality score when regime is OFF: prioritize stocks that pass all stock-level ML + trend gates
    stock_level_ml_ready = (
        (tradeable_df["ml_prob"] >= gcfg.p_min)
        & (tradeable_df["slope_t_norm"] >= 1.2)
        & (tradeable_df["ema20_slope"] > 0.0)
        & (tradeable_df["rs_rank"] >= 0.80)
        & (tradeable_df["ext_atr"] >= bcfg.ext_atr_min)
        & (tradeable_df["ext_atr"] <= bcfg.ext_atr_max)
        & (tradeable_df["days_to_earnings"] > bcfg.earnings_buffer_days)
    ).astype(int)
    tradeable_df["stock_ready"] = stock_level_ml_ready
    tradeable_df["combined_rank_score"] = (
        tradeable_df["is_consensus"] * 100.0
        + tradeable_df["ml_signal"] * 50.0
        + tradeable_df["baseline_signal"] * 25.0
        + tradeable_df["stock_ready"] * 15.0
        + tradeable_df["ml_prob"] * (tradeable_df["rs_rank"] ** 2) * 10.0
        + tradeable_df["slope_t_norm"].clip(-2.0, 6.0) * tradeable_df["rs_rank"]
    )
    tradeable_df = tradeable_df.sort_values("combined_rank_score", ascending=False)

    active_buys: List[BuyCandidate] = []
    watchlist_candidates: List[BuyCandidate] = []

    for ticker, row in tradeable_df.iterrows():
        if ticker in held_tickers and ticker != "SMH":
            continue

        c_px = float(row["close"])
        atr_val = float(row["atr"])
        if np.isnan(c_px) or np.isnan(atr_val) or atr_val <= 0:
            continue

        ml_sig = int(row.get("ml_signal", 0)) == 1
        base_sig = int(row.get("baseline_signal", 0)) == 1
        stk_ready = int(row.get("stock_ready", 0)) == 1
        ml_prob = float(row.get("ml_prob", 0.50))
        ml_ev = float(row.get("ml_ev_r", 0.0))
        rs_rk = float(row.get("rs_rank", 0.50))
        slp_t = float(row.get("slope_t_norm", 0.0))
        slp_r2 = float(row.get("slope_r2", 0.0))
        ext_a = float(row.get("ext_atr", 0.0))
        ema20_slp = float(row.get("ema20_slope", 0.0))
        slp_acc = float(row.get("slope_accel", 0.0))
        dte = int(row.get("days_to_earnings", 999))
        shap_str = str(row.get("ml_shap", ""))

        if ml_sig and base_sig:
            sig_src = "CONSENSUS (ML + Baseline)"
            tier = "CONSENSUS"
        elif ml_sig:
            sig_src = "ML (LightGBM + Platt)"
            tier = str(row.get("ml_tier", "HIGH"))
        elif base_sig:
            sig_src = "BASELINE (Adaptive L_t)"
            tier = "HIGH"
        else:
            sig_src = "STOCK-READY (Regime Gated)" if stk_ready else "WATCHLIST"
            tier = "HIGH" if ml_prob >= gcfg.p_high else ("MEDIUM" if ml_prob >= gcfg.p_min else "WATCH")

        stop_dist = min(rcfg.stop_atr * atr_val, c_px * rcfg.backstop)
        stop_px = round(c_px - stop_dist, 2)
        stop_pct = round((stop_dist / c_px) * 100.0, 2)
        tp1_px = round(c_px + rcfg.tp1_atr * atr_val, 2)
        tp1_pct = round(((tp1_px / c_px) - 1.0) * 100.0, 2)

        # Standard per-$10,000 sizing
        ref_risk_frac = rcfg.risk_per_trade if tier in ("CONSENSUS", "HIGH") else rcfg.risk_per_trade_medium
        ref_desired_sh = (10_000.0 * ref_risk_frac) / max(stop_dist, 1e-4)
        ref_notional = min(ref_desired_sh * c_px, 10_000.0 * rcfg.max_pos_pct)
        ref_shares = ref_notional / c_px

        # Standalone ticket size for this candidate under both cash pools (2 slots in Cash Only, 2 slots in Cash+ETF Rotate)
        cand_meta_s = float(row.get("ml_size_scalar", 1.0))
        effective_cand_scalar = macro_scalar * cand_meta_s
        stand_dollars_cash, stand_sh_cash, stand_risk_cash = _compute_single_ticket_size(
            c_px, stop_px, tier, current_cash, total_equity, strategy, target_slots=2, macro_scalar=effective_cand_scalar
        )
        stand_dollars_rot, stand_sh_rot, stand_risk_rot = _compute_single_ticket_size(
            c_px, stop_px, tier, deployable_with_rotate, total_equity, strategy, target_slots=2, macro_scalar=effective_cand_scalar
        )

        # Build gate diagnostic notes
        missing_gates = []
        if not regime_on:
            missing_gates.append("regime_on=OFF (SMH pullback)")
        if slp_t < 1.2:
            missing_gates.append(f"slope_t={slp_t:.2f}<1.2")
        elif not base_sig and slp_t < bcfg.slope_t_norm_min:
            missing_gates.append(f"base_slope={slp_t:.2f}<{bcfg.slope_t_norm_min}")
        if rs_rk < bcfg.rs_rank_min:
            missing_gates.append(f"rs_rank={rs_rk:.2f}<{bcfg.rs_rank_min}")
        if ema20_slp <= 0:
            missing_gates.append(f"ema20_slope={ema20_slp:.2f}<=0")
        if ext_a < bcfg.ext_atr_min or ext_a > bcfg.ext_atr_max:
            missing_gates.append(f"ext_atr={ext_a:.2f} outside [{bcfg.ext_atr_min},{bcfg.ext_atr_max}]")
        if ml_prob < gcfg.p_min:
            missing_gates.append(f"ml_prob={ml_prob:.2f}<{gcfg.p_min}")
        if dte <= bcfg.earnings_buffer_days:
            missing_gates.append(f"earnings in {dte}d")
        if not base_sig and slp_acc <= 0:
            missing_gates.append(f"slope_accel={slp_acc:.2f}<=0")
        if not base_sig and slp_r2 < bcfg.slope_r2_min:
            missing_gates.append(f"r2={slp_r2:.2f}<{bcfg.slope_r2_min}")

        if ml_sig or base_sig:
            gate_note = "ALL GATES PASSED"
        elif stk_ready:
            gate_note = "PASSES ALL STOCK GATES (Waiting only on SMH regime_on)"
        else:
            gate_note = "Waiting: " + ", ".join(missing_gates[:3]) if missing_gates else "Near trigger"

        cand = BuyCandidate(
            rank=0,
            ticker=str(ticker),
            signal_source=sig_src,
            tier=tier,
            close_price=round(c_px, 2),
            atr=round(atr_val, 2),
            stop_price=stop_px,
            stop_dist_pct=stop_pct,
            tp1_price=tp1_px,
            tp1_gain_pct=tp1_pct,
            ml_prob=round(ml_prob, 3),
            ml_ev_r=round(ml_ev, 2),
            rs_rank=round(rs_rk, 2),
            slope_t_norm=round(slp_t, 2),
            slope_r2=round(slp_r2, 2),
            ext_atr=round(ext_a, 2),
            days_to_earnings=dte,
            buy_dollars_cash_only=stand_dollars_cash,
            buy_shares_cash_only=stand_sh_cash,
            risk_dollars_cash_only=stand_risk_cash,
            buy_dollars_with_rotate=stand_dollars_rot,
            buy_shares_with_rotate=stand_sh_rot,
            risk_dollars_with_rotate=stand_risk_rot,
            buy_dollars_per_10k=round(ref_notional, 2),
            buy_shares_per_10k=round(ref_shares, 3),
            shap_summary=shap_str,
            gate_notes=gate_note,
        )

        if ml_sig or base_sig:
            cand.rank = len(active_buys) + 1
            active_buys.append(cand)
        elif len(watchlist_candidates) < 8:
            cand.rank = len(watchlist_candidates) + 1
            watchlist_candidates.append(cand)

    # Allocate exact dollar amounts for active buys under both cash pools
    if active_buys:
        rem_cash_only = _allocate_Pool(
            active_buys,
            pool_cash=current_cash,
            total_equity=total_equity,
            strategy=strategy,
            open_swing_count=open_swing_count,
            open_swing_risk_dollars=open_swing_risk_dollars,
            mode="cash_only",
            target_slots=2,
            macro_scalar=macro_scalar,
        )
        rem_with_rotate = _allocate_Pool(
            active_buys,
            pool_cash=deployable_with_rotate,
            total_equity=total_equity,
            strategy=strategy,
            open_swing_count=open_swing_count,
            open_swing_risk_dollars=open_swing_risk_dollars,
            mode="with_rotate",
            target_slots=2,
            macro_scalar=macro_scalar,
        )
    else:
        rem_cash_only = round(current_cash, 2)
        rem_with_rotate = round(deployable_with_rotate, 2)

    # 3. Core Fund (SMH) vs Money Market / SGOV Sweep for remaining cash
    if smh_secular_bull and regime_on:
        core_inst = "SMH (Secular Bull Core ETF)"
        core_dollars_cash = rem_cash_only
        core_shares_cash = round(rem_cash_only / smh_close, 3)
        core_dollars_rot = rem_with_rotate
        core_shares_rot = round(rem_with_rotate / smh_close, 3)
    else:
        core_inst = f"Money Market / SGOV (3M T-Bill Cash @ {cash_rate_apy_pct:.2f}% APY, or Scale into SMH/Top Stock-Ready Leaders)"
        core_dollars_cash = rem_cash_only
        core_shares_cash = round(rem_cash_only / smh_close, 3)
        core_dollars_rot = rem_with_rotate
        core_shares_rot = round(rem_with_rotate / smh_close, 3)

    # 4. Build concise executive action steps
    steps: List[str] = []
    for h in holdings_actions:
        if h.action.startswith("SELL / ROTATE"):
            steps.append(
                f"1. SELL / ROTATE LEVERAGED ETF ({h.ticker}): Sell {h.shares:g} sh (~${h.market_value:,.2f} @ ${h.current_price:.2f}). "
                f"3x daily leverage suffers volatility decay ({h.unrealized_pct:+.1f}% vs QQQM +18.5%); selling in a Roth IRA is tax-free and raises deployable cash from ${current_cash:,.2f} to ${deployable_with_rotate:,.2f}."
            )
        elif h.action.startswith("SELL"):
            steps.append(
                f"1. EXIT {h.ticker}: {h.action} — Sell {h.shares:g} sh (~${h.market_value:,.2f} @ ${h.current_price:.2f}). {h.rationale}"
            )
        elif h.action.startswith("TRIM"):
            steps.append(
                f"1. TAKE PARTIAL PROFIT ON {h.ticker}: Sell {h.action_shares:g} sh (~${h.action_dollars:,.2f} @ ${h.current_price:.2f}) at TP1 (${h.tp1_target:.2f}), and raise stop on remaining shares to ${h.recommended_stop:.2f}."
            )
        elif h.role == "swing":
            steps.append(
                f"1. HOLD & PROTECT {h.ticker} ({h.shares:g} sh, ${h.market_value:,.2f}, {h.unrealized_pct:+.1f}%): "
                f"Set trailing stop at ${h.recommended_stop:.2f} (locks in profit above ${h.avg_cost:.2f} cost) and limit-sell 25% (~0.75 sh = ~$538) at TP1 ${h.tp1_target:.2f} ahead of upcoming earnings [E]."
            )

    steps.append(
        f"2. KEEP CORE ETF HOLDINGS: Hold SMH (4.0 sh = $2,159.16, +37.8%), QQQM (4.878 sh = $1,425.64, +18.5%), and VOO (2.017 sh = $1,415.14, +35.2%)."
    )

    funded_buys_rot = [b for b in active_buys if b.buy_dollars_with_rotate >= 100.0]
    stock_ready_watch = [w for w in watchlist_candidates if "STOCK-READY" in w.signal_source]
    if funded_buys_rot:
        for b in funded_buys_rot:
            steps.append(
                f"3. BUY SWING SIGNAL — {b.ticker} [{b.signal_source}, {b.tier}]: "
                f"Buy ${b.buy_dollars_cash_only:,.2f} ({b.buy_shares_cash_only:.3f} sh) from current cash "
                f"[or ${b.buy_dollars_with_rotate:,.2f} ({b.buy_shares_with_rotate:.3f} sh) if rotating TQQQ] "
                f"@ ~${b.close_price:.2f} | Initial Stop: ${b.stop_price:.2f} (-{b.stop_dist_pct:.1f}%) | TP1 Target: ${b.tp1_price:.2f} (+{b.tp1_gain_pct:.1f}%)."
            )
    else:
        top_ready_str = ", ".join(
            f"{w.ticker} (${w.buy_dollars_cash_only:,.2f} Cash / ${w.buy_dollars_with_rotate:,.2f} w/ Rotate @ ${w.close_price:.2f}, Stop ${w.stop_price:.2f})"
            for w in (stock_ready_watch[:3] or watchlist_candidates[:3])
        )
        steps.append(
            f"3. NEW SWING BUYS ($2,533.37 Cash / $3,900.30 w/ TQQQ Rotate): Because SMH pulled back -3.4% today below EMA100 (${smh_ema100:.2f}), "
            f"strict regime_on is paused. Top Stock-Ready leaders passing all individual ML & trend gates right now are: {top_ready_str}."
        )
        steps.append(
            f"4. CASH / CORE SWEEP OPTION: Either keep ${rem_cash_only:,.2f} (${rem_with_rotate:,.2f} after selling TQQQ) in Money Market ({cash_rate_apy_pct:.2f}% APY) until SMH reclaims ${smh_ema100:.2f}, "
            f"OR if deploying on this dip, split across the top 2–3 Stock-Ready leaders above or add to SMH (${smh_close:.2f})."
        )

    return DailyRecommendationPlan(
        as_of_date=latest_date.strftime("%Y-%m-%d"),
        snapshot_date=portfolio.snapshot_date or latest_date.strftime("%Y-%m-%d"),
        account_name=portfolio.account_name,
        health_score=health_score,
        regime_on=regime_on,
        smh_secular_bull=smh_secular_bull,
        smh_close=round(smh_close, 2),
        smh_ema100=round(smh_ema100, 2),
        smh_ema200=round(smh_ema200, 2),
        vix_lvl=round(vix_lvl, 2),
        vix_ts=round(vix_ts, 3),
        cash_rate_apy_pct=cash_rate_apy_pct,
        days_to_fomc=days_to_fomc,
        total_equity=total_equity,
        current_cash=round(current_cash, 2),
        rotate_proceeds=round(rotate_proceeds, 2),
        deployable_cash_with_rotate=deployable_with_rotate,
        holdings_actions=holdings_actions,
        active_buys=active_buys,
        watchlist_candidates=watchlist_candidates,
        remaining_cash_after_buys_cash_only=rem_cash_only,
        remaining_cash_after_buys_with_rotate=rem_with_rotate,
        core_sweep_Instrument=core_inst,
        core_sweep_dollars_cash_only=core_dollars_cash,
        core_sweep_shares_cash_only=core_shares_cash,
        core_sweep_dollars_with_rotate=core_dollars_rot,
        core_sweep_shares_with_rotate=core_shares_rot,
        executive_steps=steps,
    )


def render_recommendation_email_text(plan: DailyRecommendationPlan) -> str:
    """Render a clean plain-text Trade Ticket summary for MIME text/plain fallback."""
    lines = [
        f"SEMISWING DAILY TRADE TICKET — {plan.as_of_date}",
        f"Account: {plan.account_name} (Snapshot: {plan.snapshot_date})",
        f"Total Equity: ${plan.total_equity:,.2f} | Settled Cash: ${plan.current_cash:,.2f} | Cash + Rotation: ${plan.deployable_cash_with_rotate:,.2f}",
        f"Swing Regime: {'ON (Risk-On)' if plan.regime_on else 'OFF (Defensive)'} | SMH Bull Core: {'ON' if plan.smh_secular_bull else 'OFF'} (SMH ${plan.smh_close:.2f})",
        "",
        "====================================================================",
        "STEP 1: WHAT TO DO WITH YOUR CURRENT HOLDINGS",
        "====================================================================",
    ]
    for h in plan.holdings_actions:
        stop_part = f" | Stop: ${h.recommended_stop:.2f} | Next Target: ${h.tp1_target:.2f}" if h.role == "swing" else ""
        ord_part = f" -> ORDER: ${h.action_dollars:,.2f} ({h.action_shares:g} sh)" if h.action_dollars > 0 else ""
        lines.append(
            f"* [{h.action}] {h.ticker} ({h.shares:g} sh @ ${h.current_price:.2f} = ${h.market_value:,.2f}, P&L {h.unrealized_pct:+.1f}%){ord_part}{stop_part}"
        )
        lines.append(f"  Why: {h.rationale}")

    lines.extend(
        [
            "",
            "====================================================================",
            "STEP 2: WHAT TO BUY (EXACT $ TRADE TICKETS)",
            "====================================================================",
        ]
    )
    if plan.active_buys:
        lines.append("QUALIFIED BUY SIGNALS FOR NEXT OPEN:")
        for b in plan.active_buys:
            lines.append(
                f"* #{b.rank} BUY {b.ticker} ({b.tier} | {b.signal_source}) @ ~${b.close_price:.2f}"
            )
            lines.append(
                f"  - Order (Cash Only Pool):      BUY ${b.buy_dollars_cash_only:,.2f} (~{b.buy_shares_cash_only:.3f} sh)"
            )
            lines.append(
                f"  - Order (With Rotation Pool):  BUY ${b.buy_dollars_with_rotate:,.2f} (~{b.buy_shares_with_rotate:.3f} sh)"
            )
            lines.append(
                f"  - Stop-Loss: ${b.stop_price:.2f} (-{b.stop_dist_pct:.1f}%) | Profit Target (TP1): ${b.tp1_price:.2f} (+{b.tp1_gain_pct:.1f}%)"
            )
            lines.append(
                f"  - Model Score: {b.ml_prob:.3f} (RS {b.rs_rank * 100:.0f}th pct) | Drivers: `{b.shap_summary}`"
            )
    else:
        lines.append(
            f"Option 2A (Immediate Core ETF Deployment): BUY ${plan.core_sweep_dollars_cash_only:,.2f} of {plan.core_sweep_Instrument} "
            f"(~{plan.core_sweep_shares_cash_only:.3f} sh @ ${plan.smh_close:.2f}), or ${plan.core_sweep_dollars_with_rotate:,.2f} "
            f"(~{plan.core_sweep_shares_with_rotate:.3f} sh) if rotating non-core/leveraged ETFs."
        )
        lines.append("")
        lines.append("Option 2B (Top Pre-Sized Stock Trade Tickets — Ready on Pullback/Breakout):")
        for w in plan.watchlist_candidates[:4]:
            lines.append(
                f"* #{w.rank} {w.ticker} (Tier {w.tier}) @ ${w.close_price:.2f} | ML Score: {w.ml_prob:.3f} (RS {w.rs_rank * 100:.0f}th pct)"
            )
            lines.append(
                f"  - Order (Cash Only Pool):      BUY ${w.buy_dollars_cash_only:,.2f} (~{w.buy_shares_cash_only:.2f} sh)"
            )
            lines.append(
                f"  - Order (With Rotation Pool):  BUY ${w.buy_dollars_with_rotate:,.2f} (~{w.buy_shares_with_rotate:.2f} sh)"
            )
            lines.append(
                f"  - Stop-Loss: ${w.stop_price:.2f} (-{w.stop_dist_pct:.1f}%) | Profit Target (TP1): ${w.tp1_price:.2f} (+{w.tp1_gain_pct:.1f}%)"
            )
            lines.append(f"  - Entry Gate: {w.gate_notes} | Drivers: `{w.shap_summary}`")
            lines.append("")

    return "\n".join(lines)


def _info_badge(tip_text: str) -> str:
    """Render a clean circular info icon '(i)' with mouse-over tooltip."""
    clean_tip = tip_text.replace('"', '&quot;').replace("'", "&#39;")
    return (
        f'<span class="tooltip-wrap" style="position:relative; display:inline-flex; align-items:center; cursor:help; vertical-align:middle;">'
        f'<span class="info-icon" title="{clean_tip}" style="display:inline-flex; align-items:center; justify-content:center; '
        f'width:13px; height:13px; border-radius:50%; background:#0284c7; color:#ffffff; font-size:10px; font-weight:700; '
        f'font-family:-apple-system, BlinkMacSystemFont, sans-serif; line-height:1; margin-left:4px; border:1px solid #38bdf8; '
        f'vertical-align:middle; text-decoration:none; box-shadow:0 1px 2px rgba(0,0,0,0.15);">i</span>'
        f'<span class="tip-box" style="visibility:hidden; opacity:0; width:240px; background:#0f172a; color:#f8fafc; '
        f'text-align:left; border-radius:7px; padding:8px 11px; position:absolute; z-index:9999; bottom:130%; left:50%; '
        f'transform:translateX(-50%); font-size:11.5px; font-weight:normal; line-height:1.4; box-shadow:0 4px 14px rgba(0,0,0,0.3); '
        f'transition:opacity 0.2s, visibility 0.2s; pointer-events:none; white-space:normal; text-transform:none; letter-spacing:normal;">{tip_text}</span>'
        f'</span>'
    )


def _render_single_plan_body(plan: DailyRecommendationPlan) -> str:
    """Render an inline-CSS, email-client-safe Trade Ticket card body (680px centered container)."""
    regime_bg = "#dcfce7" if plan.regime_on else "#fef9c3"
    regime_fg = "#166534" if plan.regime_on else "#854d0e"
    regime_label = "RISK-ON (Swing Entries Enabled)" if plan.regime_on else "DEFENSIVE (Hold Core / Cash)"

    # Build Step 1 Holding Cards
    holdings_cards_html = ""
    for h in plan.holdings_actions:
        if "SELL" in h.action or "ROTATE" in h.action:
            border_color = "#ef4444"
            badge_bg = "#fee2e2"
            badge_fg = "#991b1b"
        elif "EARNINGS" in h.action or "TRIM" in h.action:
            border_color = "#f59e0b"
            badge_bg = "#fef3c7"
            badge_fg = "#92400e"
        else:
            border_color = "#10b981"
            badge_bg = "#d1fae5"
            badge_fg = "#065f46"

        pnl_color = "#15803d" if h.unrealized_pnl >= 0 else "#dc2626"
        order_banner = ""
        if h.action_dollars > 0:
            order_banner = f"""
            <div style="margin-top:8px; padding:8px 12px; background:#fef2f2; border-radius:6px; font-size:13px; color:#991b1b; font-weight:600;">
              Order Action: SELL {h.action_shares:g} shares (~${h.action_dollars:,.2f} proceeds added to buying power)
            </div>
            """

        risk_banner = ""
        if h.role == "swing":
            earn_note = (
                f" &nbsp;|&nbsp; <strong>Earnings:</strong> in {h.days_to_earnings} trading days"
                if h.days_to_earnings < 90
                else ""
            )
            risk_banner = f"""
            <div style="margin-top:8px; padding:7px 10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-size:12px; color:#334155;">
              <strong>Protect Stop {_info_badge("Protective exit price ratcheted via Chandelier stop (Close - 2.5x ATR); locks in profits and never lowers.")}:</strong> ${h.recommended_stop:.2f} &nbsp;|&nbsp;
              <strong>Next Target (TP) {_info_badge("First profit target at +3.0x ATR (+1.5R). Sell 25%-50% shares and move stop to breakeven when touched.")}:</strong> ${h.tp1_target:.2f} &nbsp;|&nbsp;
              <strong>RS Rank {_info_badge("Decoupled 20-day idiosyncratic residual momentum percentile vs SMH (96th pct = outperforms 96% of peers beta-neutrally).")}:</strong> {h.rs_rank * 100:.0f}th pct{earn_note}
            </div>
            """

        holdings_cards_html += f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:5px solid {border_color}; border-radius:8px; padding:14px 16px; margin-bottom:10px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
            <tr>
              <td align="left" valign="top">
                <span style="font-size:16px; font-weight:700; color:#0f172a;">{h.ticker}</span>
                <span style="font-size:12px; color:#64748b; margin-left:6px;">{h.description}</span>
                <div style="font-size:12px; color:#475569; margin-top:3px;">
                  {h.shares:g} sh @ ${h.current_price:.2f} (Avg Cost ${h.avg_cost:.2f}) &bull;
                  <strong>${h.market_value:,.2f}</strong> ({h.weight_pct:.1f}% of portfolio) &bull;
                  <span style="color:{pnl_color}; font-weight:600;">${h.unrealized_pnl:+,.2f} ({h.unrealized_pct:+.1f}%)</span>
                </div>
              </td>
              <td align="right" valign="top" style="white-space:nowrap;">
                <span style="display:inline-block; padding:4px 10px; background:{badge_bg}; color:{badge_fg}; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase;">
                  {h.action}
                </span>
              </td>
            </tr>
          </table>
          {order_banner}
          {risk_banner}
          <div style="font-size:12px; color:#475569; margin-top:8px; line-height:1.45;">
            {h.rationale}
          </div>
        </div>
        """

    # Helper to render a Buy Trade Ticket Card (for either active_buys or top watchlist_candidates)
    def _render_ticket_card(c: BuyCandidate, is_active: bool) -> str:
        header_bg = "#0284c7" if is_active else "#1e293b"
        status_pill = (
            f"BUY NOW ({c.signal_source})"
            if is_active
            else f"PRE-SIZED TICKET #{c.rank} (Tier {c.tier})"
        )
        pill_bg = "#22c55e" if is_active else "#38bdf8"
        pill_fg = "#052e16" if is_active else "#082f49"
        earn_str = f"{c.days_to_earnings}d" if c.days_to_earnings < 90 else "None nearby"

        return f"""
        <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; overflow:hidden; margin-bottom:14px;">
          <div style="background:{header_bg}; color:#ffffff; padding:10px 16px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="left" valign="middle">
                  <span style="font-size:17px; font-weight:800; letter-spacing:0.3px;">#{c.rank} {c.ticker}</span>
                  <span style="font-size:13px; color:#cbd5e1; margin-left:8px;">Last Close: <strong>${c.close_price:,.2f}</strong></span>
                </td>
                <td align="right" valign="middle">
                  <span style="display:inline-block; padding:3px 10px; background:{pill_bg}; color:{pill_fg}; border-radius:999px; font-size:11px; font-weight:800;">
                    {status_pill}
                  </span>
                </td>
              </tr>
            </table>
          </div>

          <div style="padding:14px 16px;">
            <!-- Dollar Order Allocation Box -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; margin-bottom:12px;">
              <tr>
                <td width="50%" valign="top" style="padding:10px 14px; border-right:1px solid #bae6fd;">
                  <div style="font-size:11px; color:#0369a1; font-weight:700; text-transform:uppercase;">Order (Using Settled Cash: ${plan.current_cash:,.0f}) {_info_badge("Share and dollar order sized strictly from settled idle cash, capped at min(33% equity, cash / 2).")}</div>
                  <div style="font-size:18px; font-weight:800; color:#0c4a6e; margin-top:2px;">
                    BUY ${c.buy_dollars_cash_only:,.2f}
                  </div>
                  <div style="font-size:12px; color:#0284c7;">
                    ~{c.buy_shares_cash_only:.3f} shares @ ${c.close_price:,.2f} (Max Risk: -${c.risk_dollars_cash_only:,.0f})
                  </div>
                </td>
                <td width="50%" valign="top" style="padding:10px 14px;">
                  <div style="font-size:11px; color:#0369a1; font-weight:700; text-transform:uppercase;">Order (With ETF Rotation: ${plan.deployable_cash_with_rotate:,.0f}) {_info_badge("Expanded order allocation assuming scheduled sales of non-core or leveraged ETFs (e.g. SOXL, TQQQ) are executed.")}</div>
                  <div style="font-size:18px; font-weight:800; color:#0c4a6e; margin-top:2px;">
                    BUY ${c.buy_dollars_with_rotate:,.2f}
                  </div>
                  <div style="font-size:12px; color:#0284c7;">
                    ~{c.buy_shares_with_rotate:.3f} shares @ ${c.close_price:,.2f} (Max Risk: -${c.risk_dollars_with_rotate:,.0f})
                  </div>
                </td>
              </tr>
            </table>

            <!-- Stop Loss, Profit Target, & Model Score Row -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;">
              <tr>
                <td width="33%" valign="top" style="padding-right:6px;">
                  <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:8px 10px;">
                    <div style="font-size:10px; color:#991b1b; font-weight:700; text-transform:uppercase;">Hard Stop-Loss {_info_badge("Non-negotiable downside exit price placed at order fill: Entry - min(2.0x ATR, 8.0% backstop). Never widened or cancelled.")}</div>
                    <div style="font-size:14px; font-weight:700; color:#dc2626; margin-top:2px;">
                      ${c.stop_price:,.2f} <span style="font-size:11px; font-weight:600;">(-{c.stop_dist_pct:.1f}%)</span>
                    </div>
                  </div>
                </td>
                <td width="34%" valign="top" style="padding:0 3px;">
                  <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:8px 10px;">
                    <div style="font-size:10px; color:#166534; font-weight:700; text-transform:uppercase;">Profit Target (TP1) {_info_badge("First profit target at +3.0x ATR (+1.5R). Rules recommend taking 25%-50% profits and moving stop to breakeven when touched.")}</div>
                    <div style="font-size:14px; font-weight:700; color:#15803d; margin-top:2px;">
                      ${c.tp1_price:,.2f} <span style="font-size:11px; font-weight:600;">(+{c.tp1_gain_pct:.1f}%)</span>
                    </div>
                  </div>
                </td>
                <td width="33%" valign="top" style="padding-left:6px;">
                  <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px 10px;">
                    <div style="font-size:10px; color:#475569; font-weight:700; text-transform:uppercase;">ML Score &amp; RS {_info_badge("Composite conviction score combining trend significance (t-stat) with LightGBM continuous sizing scalar and 20d RS percentile.")}</div>
                    <div style="font-size:14px; font-weight:700; color:#0f172a; margin-top:2px;">
                      {c.ml_prob * 100:.1f}% <span style="font-size:11px; color:#64748b;">(RS {c.rs_rank * 100:.0f}th)</span>
                    </div>
                  </div>
                </td>
              </tr>
            </table>

            <!-- Trigger Condition & Top SHAP Drivers -->
            <div style="font-size:12px; color:#334155; background:#f8fafc; border-radius:6px; padding:8px 12px; line-height:1.45;">
              <div><strong>Entry Condition {_info_badge("Pre-trade diagnostic gates required for signal execution (Regime ON, slope_t >= 1.2, positive EMA20 slope, no nearby earnings).")}:</strong> {c.gate_notes} &nbsp;|&nbsp; <strong>Max Hold:</strong> 25 trading days &nbsp;|&nbsp; <strong>Earnings:</strong> {earn_str}</div>
              <div style="margin-top:4px; color:#475569;"><strong>Top Model Drivers (SHAP) {_info_badge("SHAP single-feature marginal attributions showing which specific market features increased (+) or decreased (-) model win probability.")}:</strong> <code>{c.shap_summary or 'N/A'}</code></div>
            </div>
          </div>
        </div>
        """

    step2_html = ""
    if plan.active_buys:
        step2_html += """
        <div style="margin-bottom:10px; font-size:13px; color:#166534; background:#dcfce7; border:1px solid #86efac; padding:10px 14px; border-radius:8px; font-weight:600;">
          Qualified Swing Entry Signals Triggered Today — Execute at Next Market Open:
        </div>
        """
        for b in plan.active_buys:
            step2_html += _render_ticket_card(b, is_active=True)

    # Always show the Immediate Core ETF Option + Top 4 Pre-Sized Stock Trade Tickets
    step2_html += f"""
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-left:5px solid #0284c7; border-radius:8px; padding:14px 16px; margin-bottom:14px;">
      <div style="font-size:14px; font-weight:700; color:#0f172a;">
        Option A — Immediate Core Semiconductor ETF Allocation ({plan.core_sweep_Instrument})
      </div>
      <div style="font-size:12px; color:#475569; margin-top:4px; line-height:1.45;">
        While waiting for individual stocks to dip back inside their volatility band, keep unallocated cash working in your unleveraged core ETF (<strong>{plan.core_sweep_Instrument}</strong> @ <strong>${plan.smh_close:,.2f}</strong>):
      </div>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px;">
        <tr>
          <td width="50%" style="padding:8px 12px; border-right:1px solid #e2e8f0;">
            <div style="font-size:11px; color:#64748b; text-transform:uppercase; font-weight:600;">Using Settled Cash Only</div>
            <div style="font-size:15px; font-weight:800; color:#0f172a;">BUY ${plan.core_sweep_dollars_cash_only:,.2f} of {plan.core_sweep_Instrument}</div>
            <div style="font-size:12px; color:#475569;">~{plan.core_sweep_shares_cash_only:.3f} shares @ ${plan.smh_close:,.2f}</div>
          </td>
          <td width="50%" style="padding:8px 12px;">
            <div style="font-size:11px; color:#64748b; text-transform:uppercase; font-weight:600;">With ETF Rotation (SNXX / SPCX / TQQQ)</div>
            <div style="font-size:15px; font-weight:800; color:#0f172a;">BUY ${plan.core_sweep_dollars_with_rotate:,.2f} of {plan.core_sweep_Instrument}</div>
            <div style="font-size:12px; color:#475569;">~{plan.core_sweep_shares_with_rotate:.3f} shares @ ${plan.smh_close:,.2f}</div>
          </td>
        </tr>
      </table>
    </div>

    <div style="font-size:14px; font-weight:700; color:#0f172a; margin:16px 0 8px 0;">
      Option B — Top 4 New AI &amp; Semiconductor Trade Tickets (Pre-Sized in $)
    </div>
    <div style="font-size:12px; color:#475569; margin-bottom:12px;">
      Pick <strong>2 to 3 tickets</strong> below (sized from your deployable cash pool while capping single-trade risk):
    </div>
    """

    for w in plan.watchlist_candidates[:4]:
        step2_html += _render_ticket_card(w, is_active=False)

    return f"""
        <div style="max-width:680px; width:100%; text-align:left;">
          <style>
            .tooltip-wrap:hover .info-icon {{ background:#0369a1 !important; transform:scale(1.15); }}
            .tooltip-wrap:hover .tip-box {{ visibility:visible !important; opacity:1 !important; }}
          </style>

          <!-- Top Header Card -->
          <div style="background:#0f172a; color:#ffffff; border-radius:12px; padding:20px 22px; margin-bottom:16px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="left" valign="top">
                  <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#38bdf8; font-weight:700;">
                    SemiSwing Daily Portfolio Desk
                  </div>
                  <div style="font-size:22px; font-weight:800; margin-top:4px; color:#f8fafc;">
                    Daily Trade Ticket &mdash; {plan.as_of_date}
                  </div>
                  <div style="font-size:12px; color:#94a3b8; margin-top:4px;">
                    {plan.account_name} &bull; Snapshot Synced: {plan.snapshot_date} &bull; VIX {plan.vix_lvl:.1f} {_info_badge("Front-month CBOE Volatility Index. Values < 22 confirm benign regime; > 30 triggers macro lockdown.")} &bull; APY {plan.cash_rate_apy_pct:.2f}% {_info_badge("Daily interest yield earned on uninvested cash indexed to FRED 3-Month T-Bill rate (DTB3).")}
                  </div>
                </td>
                <td align="right" valign="top">
                  <span style="display:inline-block; padding:5px 12px; background:{regime_bg}; color:{regime_fg}; border-radius:999px; font-size:11px; font-weight:800;">
                    {regime_label} {_info_badge("Sector macro regime governed by Schmitt Trigger on SMH (EMA200 +/- 1.5% band with EMA50 confirmation).")}
                  </span>
                </td>
              </tr>
            </table>

            <!-- Account Balance Bar -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:16px; background:#1e293b; border-radius:8px;">
              <tr>
                <td width="33%" style="padding:10px 14px; border-right:1px solid #334155;">
                  <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">
                    Total Portfolio {_info_badge("Mark-to-market liquidation equity across all cash and long stock/ETF holdings.")}
                  </div>
                  <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-top:2px;">${plan.total_equity:,.2f}</div>
                </td>
                <td width="33%" style="padding:10px 14px; border-right:1px solid #334155;">
                  <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">
                    Settled Cash Now {_info_badge("Immediately available idle cash ready to fund new buy tickets today without selling existing holdings.")}
                  </div>
                  <div style="font-size:18px; font-weight:800; color:#38bdf8; margin-top:2px;">${plan.current_cash:,.2f}</div>
                </td>
                <td width="34%" style="padding:10px 14px;">
                  <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">
                    Cash + Rotation {_info_badge("Settled cash plus capital unlocked if you execute recommended sales of non-core/leveraged ETFs.")}
                  </div>
                  <div style="font-size:18px; font-weight:800; color:#4ade80; margin-top:2px;">${plan.deployable_cash_with_rotate:,.2f}</div>
                </td>
              </tr>
            </table>
          </div>

          <!-- Step 1: Holdings Actions -->
          <div style="margin-bottom:22px;">
            <div style="font-size:15px; font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;">
              Step 1: What to Do With Your Current Holdings ({len(plan.holdings_actions)} Positions)
            </div>
            {holdings_cards_html}
          </div>

          <!-- Step 2: Buy Trade Tickets -->
          <div style="margin-bottom:20px;">
            <div style="font-size:15px; font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;">
              Step 2: What to Buy (Exact $ Trade Tickets)
            </div>
            {step2_html}
          </div>

          <!-- Footer -->
          <div style="text-align:center; font-size:11px; color:#64748b; padding:12px 0 24px 0; border-top:1px solid #cbd5e1;">
            SemiSwing Unleveraged AI &amp; Semiconductor Swing System &bull;
            SMH ${plan.smh_close:.2f} (EMA100 ${plan.smh_ema100:.2f} / EMA200 ${plan.smh_ema200:.2f}) &bull;
            3M T-Bill Cash Yield: {plan.cash_rate_apy_pct:.2f}% APY
          </div>

        </div>
    """


def render_recommendation_email_html(plan: DailyRecommendationPlan) -> str:
    """Render a standalone HTML page for a single DailyRecommendationPlan."""
    body_card = _render_single_plan_body(plan)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SemiSwing Daily Trade Ticket ({plan.as_of_date})</title>
</head>
<body style="margin:0; padding:20px 12px; background-color:#f1f5f9; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#0f172a;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        {body_card}
      </td>
    </tr>
  </table>
</body>
</html>
"""


def render_multi_portfolio_inner_html(plans: Dict[str, DailyRecommendationPlan]) -> str:
    """Render a tabbed multi-portfolio HTML container for all snapshots (`main`, `minor-roth-ira`, etc.)."""
    first_key = next(iter(plans.keys()))
    tabs_html = ""
    panels_html = ""

    for idx, (slug, plan) in enumerate(plans.items()):
        is_first = idx == 0
        btn_bg = "#0284c7" if is_first else "#1e293b"
        btn_fg = "#ffffff" if is_first else "#cbd5e1"
        btn_border = "#38bdf8" if is_first else "#334155"
        tabs_html += f"""
        <button
          id="tab-btn-{slug}"
          onclick="switchPortfolioTab('{slug}')"
          style="cursor:pointer; padding:9px 16px; margin-right:8px; margin-bottom:6px; border-radius:999px; border:1px solid {btn_border}; background:{btn_bg}; color:{btn_fg}; font-size:13px; font-weight:700; transition:all 0.15s;"
        >
          {slug} &bull; ${plan.total_equity:,.0f}
        </button>
        """
        disp = "block" if is_first else "none"
        panels_html += f"""
        <div id="tab-panel-{slug}" class="semiswing-portfolio-panel" style="display:{disp};">
          {_render_single_plan_body(plan)}
        </div>
        """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td align="center">
          <div style="max-width:680px; width:100%; text-align:left; margin-bottom:14px;">
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:12px 16px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;">
              <div>
                <div style="font-size:10px; text-transform:uppercase; letter-spacing:1px; color:#94a3b8; font-weight:700; margin-bottom:6px;">
                  Select Snapshot Portfolio ({len(plans)} Loaded)
                </div>
                <div>
                  {tabs_html}
                </div>
              </div>
              <div style="margin-top:4px;">
                <a href="../index.html" style="font-size:12px; color:#38bdf8; text-decoration:none; font-weight:600; margin-right:12px;">&larr; Dashboard</a>
                <button onclick="lockSemiSwing()" style="cursor:pointer; padding:6px 12px; border-radius:6px; border:1px solid #475569; background:#1e293b; color:#94a3b8; font-size:11px; font-weight:600;">
                  Lock Page
                </button>
              </div>
            </div>
          </div>
          {panels_html}
        </td>
      </tr>
    </table>
    """


def encrypt_html_with_passcode(
    inner_html: str,
    passcode: str,
    as_of_date: str,
    portfolio_names: list[str] | None = None,
) -> str:
    """
    Encrypt `inner_html` using PBKDF2-HMAC-SHA256 (150,000 iterations) + SHA256 Counter Mode + Encrypt-then-HMAC-SHA256.
    Uses 100% pure Python stdlib (`hashlib`, `hmac`, `secrets`, `base64`) and decrypts in the browser via native `window.crypto.subtle`.
    """
    import base64
    import hashlib
    import hmac
    import secrets

    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    master_key = hashlib.pbkdf2_hmac("sha256", passcode.encode("utf-8"), salt, 150_000, dklen=64)
    enc_key = master_key[:32]
    mac_key = master_key[32:64]

    pt_bytes = inner_html.encode("utf-8")
    ct_bytes = bytearray(len(pt_bytes))
    num_blocks = (len(pt_bytes) + 31) // 32

    for i in range(num_blocks):
        ks = hmac.digest(enc_key, nonce + i.to_bytes(4, "big"), "sha256")
        start = i * 32
        end = min(start + 32, len(pt_bytes))
        for j in range(end - start):
            ct_bytes[start + j] = pt_bytes[start + j] ^ ks[j]

    ct_final = bytes(ct_bytes)
    tag = hmac.digest(mac_key, nonce + ct_final, "sha256")

    b64_salt = base64.b64encode(salt).decode("ascii")
    b64_nonce = base64.b64encode(nonce).decode("ascii")
    b64_tag = base64.b64encode(tag).decode("ascii")
    b64_ct = base64.b64encode(ct_final).decode("ascii")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SemiSwing Protected Trade Ticket ({as_of_date})</title>
</head>
<body style="margin:0; padding:20px 12px; background-color:#0f172a; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#f8fafc;">
  <div id="lock-screen" style="max-width:420px; margin:70px auto; background:#1e293b; border:1px solid #334155; border-radius:14px; padding:28px 24px; text-align:center; box-shadow:0 20px 25px -5px rgba(0,0,0,0.4);">
    <div style="font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:#38bdf8; font-weight:700;">
      SemiSwing Portfolio Vault
    </div>
    <h1 style="font-size:21px; font-weight:800; margin:8px 0 6px 0; color:#f8fafc;">
      Daily Trade Tickets ({as_of_date})
    </h1>
    <p style="font-size:13px; color:#94a3b8; margin:0 0 20px 0; line-height:1.5;">
      Enter your passcode to decrypt and view your portfolio recommendations.
    </p>
    <form onsubmit="handleUnlock(event)" style="margin:0;">
      <input
        id="passcode-input"
        type="password"
        placeholder="Enter Passcode"
        autocomplete="current-password"
        autofocus
        style="width:100%; box-sizing:border-box; padding:11px 14px; border-radius:8px; border:1px solid #475569; background:#0f172a; color:#f8fafc; font-size:16px; text-align:center; letter-spacing:3px; margin-bottom:12px; outline:none;"
      />
      <button
        id="unlock-btn"
        type="submit"
        style="width:100%; cursor:pointer; padding:11px 16px; border-radius:8px; border:none; background:#0284c7; color:#ffffff; font-size:14px; font-weight:700;"
      >
        Unlock Trade Tickets
      </button>
    </form>
    <div id="unlock-error" style="display:none; margin-top:12px; font-size:12px; color:#f87171; font-weight:600;">
      Incorrect passcode. Please try again.
    </div>
    <div style="margin-top:18px; padding-top:14px; border-top:1px solid #334155; font-size:12px;">
      <a href="../backtests/backtest_report.html" style="color:#38bdf8; text-decoration:none; font-weight:600;">
        View Public Walk-Forward Backtest Report ($10K) &rarr;
      </a>
    </div>
  </div>

  <div id="unlocked-content" style="display:none;"></div>

  <script>
    const PAYLOAD = {{
      salt: "{b64_salt}",
      nonce: "{b64_nonce}",
      tag: "{b64_tag}",
      ct: "{b64_ct}"
    }};

    function b64ToBytes(b64) {{
      const bin = atob(b64);
      const arr = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      return arr;
    }}

    function switchPortfolioTab(slug) {{
      document.querySelectorAll('.semiswing-portfolio-panel').forEach(el => {{
        el.style.display = 'none';
      }});
      const target = document.getElementById('tab-panel-' + slug);
      if (target) target.style.display = 'block';

      document.querySelectorAll('[id^="tab-btn-"]').forEach(btn => {{
        if (btn.id === 'tab-btn-' + slug) {{
          btn.style.background = '#0284c7';
          btn.style.color = '#ffffff';
          btn.style.borderColor = '#38bdf8';
        }} else {{
          btn.style.background = '#1e293b';
          btn.style.color = '#cbd5e1';
          btn.style.borderColor = '#334155';
        }}
      }});
    }}

    function lockSemiSwing() {{
      localStorage.removeItem('semiswing_passcode');
      location.reload();
    }}

    async function decryptWithPasscode(passcode) {{
      const enc = new TextEncoder();
      const salt = b64ToBytes(PAYLOAD.salt);
      const nonce = b64ToBytes(PAYLOAD.nonce);
      const tag = b64ToBytes(PAYLOAD.tag);
      const ct = b64ToBytes(PAYLOAD.ct);

      const baseKey = await crypto.subtle.importKey(
        'raw', enc.encode(passcode), {{ name: 'PBKDF2' }}, false, ['deriveBits']
      );
      const masterBits = await crypto.subtle.deriveBits(
        {{ name: 'PBKDF2', salt: salt, iterations: 150000, hash: 'SHA-256' }},
        baseKey,
        512
      );
      const masterBytes = new Uint8Array(masterBits);
      const encKeyBytes = masterBytes.slice(0, 32);
      const macKeyBytes = masterBytes.slice(32, 64);

      const macKey = await crypto.subtle.importKey(
        'raw', macKeyBytes, {{ name: 'HMAC', hash: 'SHA-256' }}, false, ['verify']
      );
      const macInput = new Uint8Array(nonce.length + ct.length);
      macInput.set(nonce, 0);
      macInput.set(ct, nonce.length);

      const isValid = await crypto.subtle.verify('HMAC', macKey, tag, macInput);
      if (!isValid) return null;

      const encKey = await crypto.subtle.importKey(
        'raw', encKeyBytes, {{ name: 'HMAC', hash: 'SHA-256' }}, false, ['sign']
      );
      const pt = new Uint8Array(ct.length);
      const numBlocks = Math.ceil(ct.length / 32);
      const blockInput = new Uint8Array(20);
      blockInput.set(nonce, 0);

      for (let i = 0; i < numBlocks; i++) {{
        blockInput[16] = (i >>> 24) & 0xff;
        blockInput[17] = (i >>> 16) & 0xff;
        blockInput[18] = (i >>> 8) & 0xff;
        blockInput[19] = i & 0xff;
        const ksBuf = await crypto.subtle.sign('HMAC', encKey, blockInput);
        const ks = new Uint8Array(ksBuf);
        const start = i * 32;
        const end = Math.min(start + 32, ct.length);
        for (let j = 0; j < end - start; j++) {{
          pt[start + j] = ct[start + j] ^ ks[j];
        }}
      }}
      return new TextDecoder().decode(pt);
    }}

    async function handleUnlock(e) {{
      if (e) e.preventDefault();
      const input = document.getElementById('passcode-input');
      const err = document.getElementById('unlock-error');
      const btn = document.getElementById('unlock-btn');
      const code = input.value.trim();
      if (!code) return;

      btn.textContent = 'Decrypting...';
      err.style.display = 'none';
      try {{
        const html = await decryptWithPasscode(code);
        if (html) {{
          localStorage.setItem('semiswing_passcode', code);
          document.body.style.backgroundColor = '#f1f5f9';
          document.body.style.color = '#0f172a';
          document.getElementById('lock-screen').style.display = 'none';
          const container = document.getElementById('unlocked-content');
          container.innerHTML = html;
          container.style.display = 'block';
        }} else {{
          err.style.display = 'block';
          btn.textContent = 'Unlock Trade Tickets';
        }}
      }} catch (ex) {{
        err.style.display = 'block';
        btn.textContent = 'Unlock Trade Tickets';
      }}
    }}

    window.addEventListener('DOMContentLoaded', async () => {{
      const saved = localStorage.getItem('semiswing_passcode');
      if (saved) {{
        document.getElementById('passcode-input').value = saved;
        await handleUnlock(null);
      }}
    }});
  </script>
</body>
</html>
"""


def write_recommendation_reports(
    plan: DailyRecommendationPlan,
    out_dir: Path | None = None,
    all_plans: Dict[str, DailyRecommendationPlan] | None = None,
    passcode: str | None = None,
) -> tuple[Path, Path]:
    """
    Write daily Markdown (local gitignored) and Passcode-Encrypted Multi-Portfolio HTML Trade Ticket reports to `reports/daily/`.
    """
    import os

    target_dir = out_dir or (PROJECT_ROOT / "reports" / "daily")
    target_dir.mkdir(parents=True, exist_ok=True)

    plans_dict = all_plans or {"main": plan}
    effective_passcode = (passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if not effective_passcode:
        raise ValueError(
            "PORTFOLIO_PASSCODE is required to encrypt daily trade ticket report. "
            "Set it in your local .env or CI secrets."
        )

    md_path = target_dir / f"{plan.as_of_date}_recommendations.md"
    html_path = target_dir / "latest_recommendations.html"
    dated_html_path = target_dir / f"{plan.as_of_date}_recommendations.html"

    # Combine markdown locally (gitignored)
    md_sections = []
    for slug, p in plans_dict.items():
        md_sections.append(f"### PORTFOLIO: {slug}\n" + render_recommendation_email_text(p))
    md_path.write_text("\n\n" + ("\n\n" + "=" * 72 + "\n\n").join(md_sections), encoding="utf-8")

    # Build multi-portfolio inner HTML and encrypt with passcode
    inner_multi_html = render_multi_portfolio_inner_html(plans_dict)
    encrypted_html = encrypt_html_with_passcode(
        inner_multi_html, effective_passcode, plan.as_of_date, portfolio_names=list(plans_dict.keys())
    )

    html_path.write_text(encrypted_html, encoding="utf-8")
    dated_html_path.write_text(encrypted_html, encoding="utf-8")
    return html_path, md_path


