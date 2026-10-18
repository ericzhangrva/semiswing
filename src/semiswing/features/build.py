"""Causal feature builder for SemiSwing (§4 of instruction.md)."""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from semiswing.config import EventsSettings, StrategySettings, UniverseSettings


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Compute causal Wilder/EMA Average True Range (ATR)."""
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()


def _rolling_ols_log_price(log_p: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fast causal rolling OLS of log(C) ~ alpha + beta * t over a fixed window L.
    Uses lag-1 Newey-West HAC standard error correction for residual autocorrelation.
    Returns (beta, t_stat_norm, r2) arrays of same length as log_p.
    """
    n = len(log_p)
    beta = np.full(n, np.nan, dtype=np.float64)
    t_norm = np.full(n, np.nan, dtype=np.float64)
    r2 = np.full(n, np.nan, dtype=np.float64)
    if n < window or window < 5:
        return beta, t_norm, r2

    t_idx = np.arange(window, dtype=np.float64)
    t_mean = (window - 1) / 2.0
    t_centered = t_idx - t_mean
    s_tt = float(np.sum(t_centered**2))

    # Build sliding windows of shape (n - window + 1, window)
    windows = np.lib.stride_tricks.sliding_window_view(log_p, window)
    y_mean = np.mean(windows, axis=1, keepdims=True)
    y_centered = windows - y_mean

    b = np.sum(y_centered * t_centered, axis=1) / s_tt
    resid = y_centered - b[:, None] * t_centered[None, :]

    ss_tot = np.sum(y_centered**2, axis=1)
    ss_res = np.sum(resid**2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2_val = np.where(ss_tot > 1e-12, 1.0 - ss_res / ss_tot, 0.0)
        r2_val = np.clip(r2_val, 0.0, 1.0)

        # Newey-West lag-1 HAC variance of score u_i = t_centered_i * resid_i
        u = resid * t_centered[None, :]
        gamma_0 = np.sum(u**2, axis=1)
        gamma_1 = np.sum(u[:, 1:] * u[:, :-1], axis=1)
        nw_var_u = np.maximum(gamma_0 + 2.0 * (1.0 - 0.5) * gamma_1, 1e-16)
        dof_scale = window / max(window - 2, 1)
        se_b = np.sqrt(dof_scale * nw_var_u) / s_tt
        raw_t = np.where(se_b > 1e-12, b / se_b, 0.0)
        # Normalize t-stat to 20-day equivalent scale: t * sqrt(20 / L)
        norm_t = raw_t * np.sqrt(20.0 / float(window))

    beta[window - 1 :] = b
    t_norm[window - 1 :] = norm_t
    r2[window - 1 :] = r2_val
    return beta, t_norm, r2


def _adaptive_ols_log_price(log_p: np.ndarray, l_arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute causal OLS slope, sample-size-normalized Newey-West t-stat, and R^2
    using the adaptive window L_t at each bar t.
    Precomputes candidate windows L in [10..60] and indexes causally.
    """
    n = len(log_p)
    beta_out = np.full(n, np.nan, dtype=np.float64)
    t_norm_out = np.full(n, np.nan, dtype=np.float64)
    r2_out = np.full(n, np.nan, dtype=np.float64)

    valid_ls = sorted(set(int(x) for x in l_arr[~np.isnan(l_arr)] if 5 <= x <= 60))
    if not valid_ls:
        return beta_out, t_norm_out, r2_out

    cache_b = {}
    cache_t = {}
    cache_r2 = {}
    for w in valid_ls:
        cache_b[w], cache_t[w], cache_r2[w] = _rolling_ols_log_price(log_p, w)

    for i in range(n):
        w = l_arr[i]
        if np.isnan(w):
            continue
        wi = int(w)
        if wi in cache_b:
            beta_out[i] = cache_b[wi][i]
            t_norm_out[i] = cache_t[wi][i]
            r2_out[i] = cache_r2[wi][i]
    return beta_out, t_norm_out, r2_out


def build_context_and_regime(
    bars: pd.DataFrame,
    fred: pd.DataFrame,
    strategy: StrategySettings,
    events: EventsSettings,
) -> pd.DataFrame:
    """Build daily market context, macro, volatility, and regime_on table indexed by date."""
    piv = bars.pivot(index="date", columns="ticker", values="close").sort_index()
    dates = piv.index

    ctx = pd.DataFrame(index=dates)
    # Context prices with causal forward fill
    for col in ["SMH", "SPY", "QQQ", "^VIX", "^VIX3M", "^VXN", "^VVIX", "^SKEW"]:
        if col in piv.columns:
            ctx[col] = piv[col].ffill()
        else:
            ctx[col] = np.nan

    # Merge FRED series causally (forward-fill up to 5 business days, lagged by 1 day for publication lag)
    if not fred.empty:
        fred_piv = fred.pivot(index="date", columns="series_id", values="value").sort_index()
        fred_piv = fred_piv.shift(1).reindex(dates).ffill(limit=5)
        for sid in ["DTB3", "DGS10", "DTWEXBGS", "VIXCLS", "VXVCLS", "BAMLH0A0HYM2"]:
            if sid in fred_piv.columns:
                ctx[sid] = fred_piv[sid]
            else:
                ctx[sid] = np.nan
    else:
        for sid in ["DTB3", "DGS10", "DTWEXBGS", "VIXCLS", "VXVCLS", "BAMLH0A0HYM2"]:
            ctx[sid] = np.nan

    # Annualized risk-free cash yield (decimal, e.g. 0.05 for 5.0% APY) from 3-Month T-Bill (DTB3)
    ctx["cash_rate_apy"] = (ctx["DTB3"].ffill().combine_first(ctx["DGS10"].ffill() * 0.85).fillna(3.5)) / 100.0

    # Fallbacks between yfinance and FRED for VIX and VIX3M
    vix = ctx["^VIX"].combine_first(ctx["VIXCLS"]).ffill().fillna(20.0)
    vix3m = ctx["^VIX3M"].combine_first(ctx["VXVCLS"]).ffill()
    vxn = ctx["^VXN"].combine_first(vix).ffill()
    vvix = ctx["^VVIX"].fillna(95.0).ffill()
    skew = ctx["^SKEW"].fillna(130.0).ffill()

    ctx["vix_lvl"] = vix
    ctx["vix_ts"] = (vix / vix3m).fillna(1.05)  # Fail-closed default: missing term structure locks down
    ctx["vvix"] = vvix

    # VXN 5-day squeeze velocity z-score against 252d rolling distribution
    dvxn_5 = vxn.diff(5)
    ctx["vxn_squeeze_vel"] = (
        (dvxn_5 - dvxn_5.rolling(252, min_periods=60).mean())
        / dvxn_5.rolling(252, min_periods=60).std().replace(0, np.nan)
    ).fillna(0.0)

    # SKEW 20d z-score
    ctx["skew_idx"] = (
        (skew - skew.rolling(60, min_periods=20).mean())
        / skew.rolling(60, min_periods=20).std().replace(0, np.nan)
    ).fillna(0.0)

    # Macro 20d changes
    ctx["tnx_chg20"] = (ctx["DGS10"].ffill().diff(20) * 100.0).fillna(0.0)
    ctx["dxy_chg20"] = (ctx["DTWEXBGS"].ffill().pct_change(20) * 100.0).fillna(0.0)
    ctx["hy_spread_chg20"] = (ctx["BAMLH0A0HYM2"].ffill().diff(20) * 100.0).fillna(0.0)

    # SMH regime indicators
    smh = ctx["SMH"]
    spy = ctx["SPY"]
    ctx["smh_ret_1d"] = np.log(smh / smh.shift(1))
    ctx["smh_daily_ret"] = smh.pct_change().fillna(0.0)
    ctx["sector_rs"] = (smh.pct_change(20) - spy.pct_change(20)).fillna(0.0)

    rcfg = strategy.regime
    smh_ema200 = smh.ewm(span=rcfg.smh_ema_slow, min_periods=50, adjust=False).mean()
    smh_ema50 = smh.ewm(span=rcfg.smh_ema_fast, min_periods=30, adjust=False).mean()

    upper_band = smh_ema200 * (1.0 + rcfg.hysteresis_band_pct)
    lower_band = smh_ema200 * (1.0 - rcfg.hysteresis_band_pct)

    n_bars = len(ctx)
    r_state = np.zeros(n_bars, dtype=int)
    m_scalar = np.zeros(n_bars, dtype=np.float64)

    current_r = 0
    for i in range(n_bars):
        price = smh.iloc[i]
        u = upper_band.iloc[i]
        l = lower_band.iloc[i]
        e50 = smh_ema50.iloc[i]
        e200 = smh_ema200.iloc[i]
        v = vix.iloc[i]
        ts = ctx["vix_ts"].iloc[i]

        # 1. Evaluate Stateful Hysteresis (Schmitt Trigger)
        if np.isnan(price) or np.isnan(u) or np.isnan(l):
            current_r = 0
        elif price > u and price > e50:
            current_r = 1
        elif price < l:
            current_r = 0
        # Else: price in [l, u] -> retains previous current_r

        r_state[i] = current_r

        # 2. Evaluate Continuous Macro Multiplier M_t
        if current_r == 0 or ts >= rcfg.vix_ts_max or v >= rcfg.vix_kill_switch:
            m_scalar[i] = 0.0
        elif e50 < e200 or v >= rcfg.vix_max_entry:
            m_scalar[i] = 0.5
        else:
            m_scalar[i] = 1.0

    ctx["smh_secular_bull"] = r_state
    ctx["regime_on"] = (m_scalar > 0.0).astype(int)
    ctx["macro_scalar"] = m_scalar

    # FOMC calendar features (causal check against scheduled calendar)
    fomc_dt = np.sort(pd.to_datetime(events.fomc_dates).values)
    date_vals = dates.values
    idx_next = np.searchsorted(fomc_dt, date_vals, side="left")
    days_to_fomc = np.full(len(dates), 99, dtype=int)
    for i, pos in enumerate(idx_next):
        if pos < len(fomc_dt):
            # Convert calendar day difference to approximate trading days
            cal_days = int((fomc_dt[pos] - date_vals[i]) / np.timedelta64(1, "D"))
            days_to_fomc[i] = max(0, int(round(cal_days * 5 / 7)))
    ctx["days_to_fomc"] = days_to_fomc
    ctx["fomc_in_5d"] = (ctx["days_to_fomc"] <= 5).astype(int)
    ctx["fomc_next_day"] = (ctx["days_to_fomc"] <= 1).astype(int)

    return ctx.reset_index()


def _compute_ticker_features(
    df_t: pd.DataFrame,
    ctx: pd.DataFrame,
    earnings_t: pd.DataFrame,
    strategy: StrategySettings,
    is_etf: bool,
) -> pd.DataFrame:
    """Compute all single-ticker causal features on closed daily bars."""
    df = df_t.sort_values("date").copy().reset_index(drop=True)
    df = pd.merge(df, ctx, on="date", how="left")

    close = df["close"]
    log_c = np.log(close.values.astype(np.float64))
    log_ret = pd.Series(np.r_[np.nan, np.diff(log_c)], index=df.index)
    df["log_ret_1d"] = log_ret

    # ATR(14) and ATR%
    df["atr"] = compute_atr(df, period=14)
    df["atr_pct"] = (df["atr"] / close).replace(0, np.nan)

    # 20d dollar volume
    df["dollar_vol_20d"] = (close * df["volume"]).rolling(20, min_periods=10).mean()

    # Realized volatilities (annualized)
    sigma_10 = log_ret.rolling(10, min_periods=8).std()
    sigma_20 = log_ret.rolling(20, min_periods=15).std()
    sigma_60 = log_ret.rolling(60, min_periods=30).std()
    sigma_250 = log_ret.rolling(250, min_periods=60).std()

    df["rv10"] = sigma_10 * np.sqrt(252.0)
    df["rv20"] = sigma_20 * np.sqrt(252.0)
    df["rv60"] = sigma_60 * np.sqrt(252.0)
    df["vol_compress"] = (df["rv10"] / df["rv60"].replace(0, np.nan)).fillna(1.0)

    # Vol-scaled dynamic window L_t in [min, max]
    ratio = (sigma_250 / sigma_20.replace(0, np.nan)).fillna(1.0)
    l_raw = np.round(strategy.window.base * ratio)
    l_t = np.clip(l_raw, strategy.window.min, strategy.window.max)
    df["L_t"] = l_t

    # Fixed multi-scale OLS slopes (10d, 20d, 40d)
    for w in strategy.window.fixed:
        b_w, t_w, r2_w = _rolling_ols_log_price(log_c, w)
        df[f"beta_{w}d"] = b_w
        df[f"slope_t_norm_{w}d"] = t_w
        df[f"slope_r2_{w}d"] = r2_w
        df[f"slope_sharpe_{w}d"] = (b_w * 252.0) / df["rv20"].replace(0, np.nan)

    # Adaptive window L_t OLS slope, normalized t-stat, and R^2
    b_adap, t_adap, r2_adap = _adaptive_ols_log_price(log_c, l_t.values)
    df["slope_beta"] = b_adap
    df["slope_t_norm"] = t_adap
    df["slope_r2"] = r2_adap
    df["slope_sharpe"] = (b_adap * 252.0) / df["rv20"].replace(0, np.nan)

    # Volatility-normalized trend acceleration: (beta_10d - beta_40d) / sigma_20
    df["slope_accel"] = (df["beta_10d"] - df["beta_40d"]) / sigma_20.replace(0, np.nan)

    # EMA slopes in ATR units and extension from EMA20
    ema20 = close.ewm(span=20, min_periods=15, adjust=False).mean()
    ema50 = close.ewm(span=50, min_periods=30, adjust=False).mean()
    df["ema20"] = ema20
    df["ema50"] = ema50
    df["ema20_slope"] = (ema20 / ema20.shift(5) - 1.0) / df["atr_pct"]
    df["ema50_slope"] = (ema50 / ema50.shift(10) - 1.0) / df["atr_pct"]
    df["ext_atr"] = (close - ema20) / df["atr"].replace(0, np.nan)

    # Residual momentum vs SMH (rolling 120d beta)
    smh_ret = df["smh_ret_1d"]
    cov_120 = log_ret.rolling(120, min_periods=40).cov(smh_ret)
    var_120 = smh_ret.rolling(120, min_periods=40).var().replace(0, np.nan)
    beta_smh = (cov_120 / var_120).clip(0.2, 3.0).fillna(1.0)
    resid_1d = log_ret - beta_smh * smh_ret
    df["resid_mom_20"] = resid_1d.rolling(20, min_periods=15).sum()
    df["resid_mom_60"] = resid_1d.rolling(60, min_periods=30).sum()

    # Days to next earnings (set to 999 for ETFs or when no earnings within 90 days)
    if is_etf or earnings_t.empty:
        df["days_to_earnings"] = 999
    else:
        ed_vals = np.sort(earnings_t["earnings_date"].values)
        d_vals = df["date"].values
        pos = np.searchsorted(ed_vals, d_vals, side="left")
        dte = np.full(len(df), 999, dtype=int)
        for i, p in enumerate(pos):
            if p < len(ed_vals):
                cal_d = int((ed_vals[p] - d_vals[i]) / np.timedelta64(1, "D"))
                dte[i] = max(0, int(round(cal_d * 5 / 7)))
        df["days_to_earnings"] = dte

    df["is_etf"] = int(is_etf)
    return df


FEATURE_COLUMNS: List[str] = [
    "slope_t_norm",
    "slope_r2",
    "slope_sharpe",
    "slope_accel",
    "slope_t_norm_10d",
    "slope_t_norm_20d",
    "slope_t_norm_40d",
    "slope_r2_20d",
    "ema20_slope",
    "ema50_slope",
    "ext_atr",
    "resid_mom_20",
    "resid_mom_60",
    "rs_rank",
    "sector_rs",
    "vol_compress",
    "vix_ts",
    "vxn_squeeze_vel",
    "skew_idx",
]


def compute_pit_quarterly_universe(
    bars: pd.DataFrame,
    universe: UniverseSettings,
) -> dict[pd.Timestamp, set[str]]:
    """
    Compute strictly point-in-time (PIT) quarterly tradeable universe mapping: date -> set of tradeable stock tickers.

    Two-Stage PIT Funnel (evaluated at t_k - 1 before each quarter start t_k in {Jan 1, Apr 1, Jul 1, Oct 1}):
    1. Stage 1 — Survivorship-Free Industry + Liquidity Gate:
       - Active US-listed semiconductor & tech equities in all_panel_stocks
       - History >= pit_min_history_days (>= 60 trading days since listing/IPO)
       - Close_{t-1} >= pit_min_price ($15.00)
       - Median Daily Dollar Volume over trailing pit_volume_window (60d) >= pit_min_dollar_vol_60d ($150M)
       - ATR%_{20d, t-1} > 0
    2. Stage 2 — Swing Tradability Ranking:
       SwingRankScore_{i, t-1} = log10(MedDollarVol_{60d}) * ATR%_{20d, t-1}
       Select Top N (default 40) ranked by SwingRankScore descending.

    Quarterly Invariance & Position Grace Rule:
    - Selected tickers receive is_tradeable_universe = 1 for all trading days in quarter k.
    - Stocks outside the Top 40 have is_tradeable_universe = 0 (blocking new entry signals),
      while open positions held from previous quarters continue to be managed by stops/targets until exit.
    """
    df_bars = bars.copy()
    df_bars["date"] = pd.to_datetime(df_bars["date"])

    etfs_and_ctx = set(universe.tradeable_etfs) | set(universe.context_tickers)
    stocks_bars = df_bars[~df_bars["ticker"].isin(etfs_and_ctx)].copy()

    def _prep_stock(df_t: pd.DataFrame) -> pd.DataFrame:
        df_t = df_t.sort_values("date").copy()
        c = df_t["close"]
        h = df_t["high"]
        l = df_t["low"]
        v = df_t["volume"]
        pc = c.shift(1)
        tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
        df_t["atr20"] = tr.ewm(
            alpha=1.0 / universe.pit_atr_window,
            min_periods=universe.pit_atr_window,
            adjust=False,
        ).mean()
        df_t["atr_pct_20"] = (df_t["atr20"] / c).replace(0, np.nan)
        df_t["dollar_vol"] = c * v
        df_t["bars_count"] = np.arange(1, len(df_t) + 1)
        return df_t

    stocks_prepared = pd.concat([_prep_stock(g) for _, g in stocks_bars.groupby("ticker")], ignore_index=True)

    all_dates = sorted(df_bars["date"].unique())
    dates_df = pd.DataFrame({"date": all_dates})
    dates_df["year"] = dates_df["date"].dt.year
    dates_df["quarter"] = dates_df["date"].dt.quarter
    quarter_starts = dates_df.groupby(["year", "quarter"])["date"].min().tolist()

    date_to_universe: dict[pd.Timestamp, set[str]] = {}
    earliest_universe: set[str] | None = None

    vol_win = universe.pit_volume_window
    min_price = universe.pit_min_price
    min_hist = universe.pit_min_history_days
    min_dvol = universe.pit_min_dollar_vol_60d
    top_n = universe.pit_top_n

    for i, q_start in enumerate(quarter_starts):
        hist_dates = [d for d in all_dates if d < q_start]
        if not hist_dates:
            continue
        t_minus_1 = hist_dates[-1]
        window_dates = hist_dates[-vol_win:]
        if len(window_dates) < 20:
            continue

        w_df = stocks_prepared[stocks_prepared["date"].isin(window_dates)]
        t1_df = stocks_prepared[stocks_prepared["date"] == t_minus_1].set_index("ticker")

        med_dvol = w_df.groupby("ticker")["dollar_vol"].median()

        cands = []
        for ticker in t1_df.index:
            c_val = float(t1_df.loc[ticker, "close"])
            atr_pct = float(t1_df.loc[ticker, "atr_pct_20"])
            b_cnt = int(t1_df.loc[ticker, "bars_count"])
            d_med = float(med_dvol.get(ticker, 0.0))

            if (
                c_val >= min_price
                and b_cnt >= min_hist
                and d_med >= min_dvol
                and not np.isnan(atr_pct)
                and atr_pct > 0
            ):
                score = np.log10(d_med) * atr_pct
                cands.append({"ticker": ticker, "score": score})

        if cands:
            c_df = pd.DataFrame(cands).sort_values("score", ascending=False)
            selected = set(c_df.head(top_n)["ticker"].tolist())
        else:
            selected = set()

        if earliest_universe is None and selected:
            earliest_universe = selected

        next_q_start = quarter_starts[i + 1] if i + 1 < len(quarter_starts) else None
        q_dates = [d for d in all_dates if d >= q_start and (next_q_start is None or d < next_q_start)]
        for d in q_dates:
            date_to_universe[d] = selected

    for d in all_dates:
        if d not in date_to_universe:
            date_to_universe[d] = earliest_universe or set()

    return date_to_universe


def build_feature_panel(
    bars: pd.DataFrame,
    fred: pd.DataFrame,
    earnings: pd.DataFrame,
    strategy: StrategySettings,
    universe: UniverseSettings,
    events: EventsSettings,
) -> pd.DataFrame:
    """Build full causal feature panel across all tradeable and training-only tickers."""
    ctx = build_context_and_regime(bars, fred, strategy, events)
    target_tickers = universe.all_panel_stocks + universe.tradeable_etfs
    etf_set = set(universe.tradeable_etfs)
    tradeable_set = set(universe.all_tradeable)

    frames = []
    for t in target_tickers:
        df_t = bars[bars["ticker"] == t]
        if df_t.empty or len(df_t) < 65:
            continue
        ed_t = earnings[earnings["ticker"] == t] if not earnings.empty else pd.DataFrame()
        feat_t = _compute_ticker_features(df_t, ctx, ed_t, strategy, is_etf=(t in etf_set))
        feat_t["is_tradeable_universe"] = int(t in tradeable_set)
        frames.append(feat_t)

    if not frames:
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True).sort_values(["date", "ticker"]).reset_index(drop=True)

    # Dynamic Point-in-Time Universe Reconstitution (Phase 3 Two-Stage Funnel)
    if universe.dynamic_pit_reconstitution:
        date_to_univ = compute_pit_quarterly_universe(bars, universe)
        panel_dts = pd.to_datetime(panel["date"])
        panel["is_tradeable_universe"] = [
            1 if t in etf_set or t in date_to_univ.get(d, set()) else 0
            for d, t in zip(panel_dts, panel["ticker"])
        ]

    # Cross-sectional percentile rank of resid_mom_20 on each date across single stocks
    stock_mask = panel["is_etf"] == 0
    panel["rs_rank"] = 0.5
    panel.loc[stock_mask, "rs_rank"] = (
        panel.loc[stock_mask].groupby("date")["resid_mom_20"].rank(pct=True, na_option="keep")
    ).fillna(0.5)
    # For SMH/SOXX ETFs, rank is set above 0.5 when sector_rs > 0
    panel.loc[~stock_mask, "rs_rank"] = np.where(panel.loc[~stock_mask, "sector_rs"] > 0, 0.70, 0.30)

    return panel

