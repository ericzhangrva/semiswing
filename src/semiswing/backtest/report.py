"""HTML and Markdown backtest report and interactive benchmark chart generator (§9 of instruction.md)."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from semiswing.backtest.engine import BacktestResult, compute_period_metrics
from semiswing.config import PROJECT_ROOT, StrategySettings

STRATEGY_SOURCE_FILES = [
    "src/semiswing/config.py",
    "src/semiswing/features/build.py",
    "src/semiswing/labels/triple_barrier.py",
    "src/semiswing/models/signal_models.py",
    "src/semiswing/backtest/engine.py",
]


def compute_strategy_source_sha256(root_dir: Path | None = None) -> str:
    """Compute deterministic SHA256 digest over canonical strategy logic and configuration files."""
    if root_dir is None:
        root_dir = PROJECT_ROOT
    h = hashlib.sha256()
    for rel_path in STRATEGY_SOURCE_FILES:
        fp = root_dir / rel_path
        if fp.exists():
            content = fp.read_bytes().replace(b"\r\n", b"\n")
            h.update(rel_path.encode("utf-8"))
            h.update(content)
    return h.hexdigest()


def load_trial_count_k(reports_dir: Path | None = None) -> int:
    """Read cumulative trial counter K from experiments_log.json for Deflated Sharpe Ratio calculation."""
    if reports_dir is None:
        reports_dir = PROJECT_ROOT / "reports" / "backtests"
    log_file = reports_dir / "experiments_log.json"
    if log_file.exists():
        try:
            data = json.loads(log_file.read_text(encoding="utf-8"))
            return int(data.get("total_trials", 14))
        except Exception:
            return 14
    return 14


def compute_benchmark_result(
    panel: pd.DataFrame,
    strategy: StrategySettings,
    ticker: str = "SMH",
    label: str | None = None,
) -> BacktestResult:
    """Compute a Buy & Hold benchmark curve for any index/ETF ticker over the OOS period."""
    oos_start = pd.to_datetime(strategy.backtest.oos_start_date)
    sub = panel[(panel["ticker"] == ticker) & (panel["date"] >= oos_start)].sort_values("date").copy()
    disp_name = label or f"{ticker} Buy & Hold"
    if sub.empty:
        empty_eq = pd.DataFrame(columns=["date", "equity", "cash", "n_positions", "regime_on"])
        return BacktestResult(name=disp_name, equity_curve=empty_eq, trades=pd.DataFrame())

    init_eq = float(strategy.risk.paper_equity)
    first_px = float(sub["close"].iloc[0])
    rf_vals = sub["cash_rate_apy"].fillna(0.035).values / 252.0 if "cash_rate_apy" in sub.columns else 0.0
    eq_df = pd.DataFrame(
        {
            "date": sub["date"].values,
            "equity": init_eq * (sub["close"].values / first_px),
            "cash": 0.0,
            "n_positions": 1,
            "regime_on": sub["regime_on"].values,
            "rf_daily": rf_vals,
        }
    )
    empty_trades = pd.DataFrame()
    res = BacktestResult(name=disp_name, equity_curve=eq_df, trades=empty_trades)
    res.metrics_overall = compute_period_metrics(eq_df, empty_trades)
    res.metrics_2022_bear = compute_period_metrics(eq_df, empty_trades, "2022-01-01", "2022-12-31")
    res.metrics_ai_era = compute_period_metrics(eq_df, empty_trades, strategy.backtest.ai_era_start, None)

    years = sorted(eq_df["date"].dt.year.unique())
    y_rows = []
    for yr in years:
        m = compute_period_metrics(eq_df, empty_trades, f"{yr}-01-01", f"{yr}-12-31")
        y_rows.append({"year": yr, **m})
    res.yearly_table = pd.DataFrame(y_rows)
    return res


def compute_cash_tbill_benchmark(panel: pd.DataFrame, strategy: StrategySettings) -> BacktestResult:
    """Compute a 100% 3-Month Treasury Bill (DTB3) risk-free savings curve over the OOS period."""
    oos_start = pd.to_datetime(strategy.backtest.oos_start_date)
    sub = (
        panel[panel["date"] >= oos_start][["date", "cash_rate_apy", "regime_on"]]
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .copy()
    )
    disp_name = "3M T-Bill Cash (DTB3)"
    if sub.empty:
        empty_eq = pd.DataFrame(columns=["date", "equity", "cash", "n_positions", "regime_on"])
        return BacktestResult(name=disp_name, equity_curve=empty_eq, trades=pd.DataFrame())

    init_eq = float(strategy.risk.paper_equity)
    daily_rates = sub["cash_rate_apy"].fillna(0.035).values / 252.0
    eq_vals = init_eq * np.cumprod(1.0 + daily_rates)
    eq_df = pd.DataFrame(
        {
            "date": sub["date"].values,
            "equity": eq_vals,
            "cash": eq_vals,
            "n_positions": 0,
            "regime_on": sub["regime_on"].values,
            "rf_daily": daily_rates,
        }
    )
    empty_trades = pd.DataFrame()
    res = BacktestResult(name=disp_name, equity_curve=eq_df, trades=empty_trades)
    res.metrics_overall = compute_period_metrics(eq_df, empty_trades)
    res.metrics_2022_bear = compute_period_metrics(eq_df, empty_trades, "2022-01-01", "2022-12-31")
    res.metrics_ai_era = compute_period_metrics(eq_df, empty_trades, strategy.backtest.ai_era_start, None)

    years = sorted(eq_df["date"].dt.year.unique())
    y_rows = []
    for yr in years:
        m = compute_period_metrics(eq_df, empty_trades, f"{yr}-01-01", f"{yr}-12-31")
        y_rows.append({"year": yr, **m})
    res.yearly_table = pd.DataFrame(y_rows)
    return res


def _style_map() -> Dict[str, Dict[str, object]]:
    """Consistent color, line width, and dash styles for strategies vs benchmark indexes."""
    return {
        "Baseline (SMH Bull Core + Swing)": {"color": "#059669", "lw": 2.6, "ls": "-", "dash": "solid", "zorder": 10, "default_on": True},
        "ML (SMH Bull Core + Swing)": {"color": "#2563eb", "lw": 2.6, "ls": "-", "dash": "solid", "zorder": 10, "default_on": True},
        "Pure Pre-2022 Semi (SMH Bull Core + Swing)": {"color": "#0d9488", "lw": 2.1, "ls": "-.", "dash": "dashdot", "zorder": 9, "default_on": True},
        "Baseline (Adaptive L_t)": {"color": "#10b981", "lw": 2.2, "ls": "--", "dash": "dash", "zorder": 9, "default_on": True},
        "ML (LightGBM + Platt)": {"color": "#3b82f6", "lw": 2.3, "ls": "-", "dash": "solid", "zorder": 9, "default_on": True},
        "Pure Pre-2022 Semi (Cash Swing)": {"color": "#14b8a6", "lw": 1.9, "ls": ":", "dash": "dot", "zorder": 8, "default_on": False},
        "Baseline (Fixed 20d)": {"color": "#94a3b8", "lw": 1.4, "ls": ":", "dash": "dot", "zorder": 4, "default_on": False},
        "SMH Buy & Hold": {"color": "#dc2626", "lw": 2.2, "ls": "-.", "dash": "dashdot", "zorder": 8, "default_on": True},
        "SOXX Buy & Hold": {"color": "#f97316", "lw": 1.7, "ls": ":", "dash": "dot", "zorder": 6, "default_on": False},
        "VGT Buy & Hold": {"color": "#7c3aed", "lw": 1.9, "ls": "-.", "dash": "dashdot", "zorder": 7, "default_on": True},
        "QQQ Buy & Hold": {"color": "#d97706", "lw": 2.0, "ls": "--", "dash": "dash", "zorder": 7, "default_on": True},
        "AIQ Buy & Hold": {"color": "#ec4899", "lw": 1.6, "ls": ":", "dash": "dot", "zorder": 5, "default_on": False},
        "IGV Buy & Hold": {"color": "#06b6d4", "lw": 1.6, "ls": ":", "dash": "dot", "zorder": 5, "default_on": False},
        "S&P 500 (SPY) Buy & Hold": {"color": "#334155", "lw": 2.0, "ls": "--", "dash": "dash", "zorder": 6, "default_on": True},
        "3M T-Bill Cash (DTB3)": {"color": "#64748b", "lw": 1.5, "ls": ":", "dash": "dot", "zorder": 3, "default_on": True},
    }


def generate_benchmark_charts(
    results: Dict[str, BacktestResult],
    charts_dir: Path,
    ai_era_start: str = "2023-01-01",
) -> Dict[str, Path]:
    """Generate high-resolution static PNG comparison charts for Markdown and artifact embedding."""
    charts_dir.mkdir(parents=True, exist_ok=True)
    styles = _style_map()
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "axes.edgecolor": "#cbd5e1",
            "axes.grid": True,
            "grid.alpha": 0.3,
            "grid.color": "#94a3b8",
        }
    )

    chart_paths: Dict[str, Path] = {}

    # 1. Full OOS Equity Curve (2022-2026): Growth of $10,000
    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=160)
    for name, res in results.items():
        if res.equity_curve.empty or name == "Baseline (Fixed 20d)":
            continue
        st = styles.get(name, {"color": "#334155", "lw": 1.5, "ls": "-", "zorder": 5})
        eq = res.equity_curve
        final_ret = res.metrics_overall.get("total_return_pct", 0.0)
        sr = res.metrics_overall.get("sharpe", 0.0)
        lbl = f"{name} ({final_ret:+.1f}% | SR {sr:.2f})"
        ax.plot(
            eq["date"],
            eq["equity"],
            label=lbl,
            color=st["color"],
            linewidth=st["lw"],
            linestyle=st["ls"],
            zorder=st["zorder"],
        )

    ax.axvspan(pd.to_datetime("2022-01-01"), pd.to_datetime("2022-12-31"), color="#fee2e2", alpha=0.35, label="2022 Bear Market")
    ax.set_title("Full Out-of-Sample Growth of $10,000 (2022–2026: Includes 2022 Bear Crash)", fontsize=13.5, fontweight="bold", pad=12)
    ax.set_ylabel("Portfolio Value ($ USD)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.92, ncol=2)
    fig.tight_layout()
    p1 = charts_dir / "equity_2022_2026.png"
    fig.savefig(p1)
    plt.close(fig)
    chart_paths["equity_2022_2026"] = p1

    # 2. Modern AI Cycle (2023-2026): Rebased on Jan 1, 2023
    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=160)
    ai_dt = pd.to_datetime(ai_era_start)
    for name, res in results.items():
        if res.equity_curve.empty or name == "Baseline (Fixed 20d)":
            continue
        sub = res.equity_curve[res.equity_curve["date"] >= ai_dt].copy()
        if sub.empty:
            continue
        st = styles.get(name, {"color": "#334155", "lw": 1.5, "ls": "-", "zorder": 5})
        rebased = 10000.0 * (sub["equity"].values / float(sub["equity"].iloc[0]))
        final_ret = res.metrics_ai_era.get("total_return_pct", 0.0)
        sr = res.metrics_ai_era.get("sharpe", 0.0)
        lbl = f"{name} ({final_ret:+.1f}% | SR {sr:.2f})"
        ax.plot(
            sub["date"],
            rebased,
            label=lbl,
            color=st["color"],
            linewidth=st["lw"],
            linestyle=st["ls"],
            zorder=st["zorder"],
        )

    ax.set_title("Modern AI Cycle Growth of $10,000 (2023–2026: Rebased Jan 1, 2023)", fontsize=13.5, fontweight="bold", pad=12)
    ax.set_ylabel("Portfolio Value ($ USD)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.92, ncol=2)
    fig.tight_layout()
    p2 = charts_dir / "equity_2023_2026_ai_era.png"
    fig.savefig(p2)
    plt.close(fig)
    chart_paths["equity_2023_2026_ai_era"] = p2

    # 3. Underwater Drawdown Comparison (2022-2026)
    fig, ax = plt.subplots(figsize=(13, 5.8), dpi=160)
    dd_keys = [
        "ML (LightGBM + Platt)",
        "Baseline (Adaptive L_t)",
        "ML (SMH Bull Core + Swing)",
        "Baseline (SMH Bull Core + Swing)",
        "Pure Pre-2022 Semi (SMH Bull Core + Swing)",
        "SMH Buy & Hold",
        "VGT Buy & Hold",
        "QQQ Buy & Hold",
        "S&P 500 (SPY) Buy & Hold",
    ]
    for name in dd_keys:
        if name not in results or results[name].equity_curve.empty:
            continue
        res = results[name]
        st = styles.get(name, {"color": "#334155", "lw": 1.5, "ls": "-", "zorder": 5})
        eq = res.equity_curve
        peaks = eq["equity"].cummax()
        dd_pct = ((eq["equity"] / peaks) - 1.0) * 100.0
        max_dd = res.metrics_overall.get("max_dd_pct", 0.0)
        ax.plot(
            eq["date"],
            dd_pct,
            label=f"{name} (Max DD: -{max_dd:.1f}%)",
            color=st["color"],
            linewidth=st["lw"],
            linestyle=st["ls"],
            zorder=st["zorder"],
        )

    ax.axhline(-20.0, color="#ef4444", linestyle=":", linewidth=1.2, label="-20% Drawdown Gate")
    ax.set_title("Underwater Drawdown Comparison (2022–2026)", fontsize=13.5, fontweight="bold", pad=12)
    ax.set_ylabel("Drawdown from Peak (%)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.legend(loc="lower left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.92, ncol=2)
    fig.tight_layout()
    p3 = charts_dir / "drawdown_comparison.png"
    fig.savefig(p3)
    plt.close(fig)
    chart_paths["drawdown_comparison"] = p3

    # 4. Calendar Year Returns Bar Chart + Risk-Return Scatter (2-panel)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.5, 6.2), dpi=160, gridspec_kw={"width_ratios": [1.35, 1.0]})
    bar_series = [
        ("Baseline (SMH Bull Core + Swing)", "#059669"),
        ("ML (SMH Bull Core + Swing)", "#2563eb"),
        ("Pure Pre-2022 Semi (SMH Bull Core + Swing)", "#0d9488"),
        ("Baseline (Adaptive L_t)", "#10b981"),
        ("ML (LightGBM + Platt)", "#60a5fa"),
        ("SMH Buy & Hold", "#dc2626"),
        ("VGT Buy & Hold", "#7c3aed"),
        ("QQQ Buy & Hold", "#d97706"),
        ("S&P 500 (SPY) Buy & Hold", "#475569"),
    ]
    all_max_dates = [pd.to_datetime(r.equity_curve["date"].max()) for r in results.values() if not r.equity_curve.empty]
    max_dt = max(all_max_dates) if all_max_dates else pd.Timestamp("2026-10-16")
    years = sorted({int(yr) for r in results.values() if not r.yearly_table.empty for yr in r.yearly_table["year"].tolist()})
    if not years:
        years = [2022, 2023, 2024, 2025, 2026]
    is_partial_last_year = not (max_dt.month == 12 and max_dt.day >= 29)

    x = np.arange(len(years))
    width = 0.088
    for idx, (s_name, col) in enumerate(bar_series):
        if s_name not in results or results[s_name].yearly_table.empty:
            continue
        yt = results[s_name].yearly_table.set_index("year")
        vals = [round(float(yt.loc[yr, "total_return_pct"])) if yr in yt.index else 0.0 for yr in years]
        offset = (idx - len(bar_series) / 2.0 + 0.5) * width
        ax1.bar(x + offset, vals, width=width, label=s_name, color=col, alpha=0.9)

    ax1.axhline(0.0, color="#1e293b", linewidth=1.0)
    ax1.set_xticks(x)
    x_labels = [f"{y} YTD" if (y == years[-1] and is_partial_last_year) else str(y) for y in years]
    ax1.set_xticklabels(x_labels, fontweight="bold")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax1.set_ylabel("Calendar Year Return (%)", fontsize=10.5, fontweight="bold")
    ax1.set_title(f"Annual Returns by Year ({years[0]}–{years[-1]})", fontsize=12.5, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=7.4, ncol=2, frameon=True, facecolor="white")

    scatter_items = []
    for name, res in results.items():
        if res.equity_curve.empty or name == "Baseline (Fixed 20d)":
            continue
        st = styles.get(name, {"color": "#334155"})
        dd = float(res.metrics_overall.get("max_dd_pct", 0.0))
        cagr = float(res.metrics_overall.get("cagr_pct", 0.0))
        sr = float(res.metrics_overall.get("sharpe", 0.0))
        is_strat = any(k in name for k in ("Baseline", "ML", "Pure Pre-2022"))
        marker = "D" if is_strat else "o"
        sz = 110 if is_strat else 75
        ax2.scatter(
            dd,
            cagr,
            color=st["color"],
            s=sz,
            marker=marker,
            zorder=8,
            edgecolors="#0f172a",
            linewidths=0.8,
            label=f"{name} (SR {sr:.2f})",
        )
        scatter_items.append((name, dd, cagr, is_strat))

    max_dd_val = max((it[1] for it in scatter_items), default=45.0)
    min_cagr_val = min((it[2] for it in scatter_items), default=0.0)
    max_cagr_val = max((it[2] for it in scatter_items), default=55.0)
    span_y = max(max_cagr_val - min_cagr_val, 15.0)
    x_left, x_right = -1.8, max_dd_val * 1.22
    y_bot, y_top = min_cagr_val - span_y * 0.14, max_cagr_val + span_y * 0.16
    ax2.set_xlim(x_left, x_right)
    ax2.set_ylim(y_bot, y_top)

    # Algorithmic 2D bounding-box collision avoidance for static scatter labels
    plot_w, plot_h = 420.0, 320.0
    to_px_x = lambda xv: ((xv - x_left) / max(x_right - x_left, 1e-6)) * plot_w
    to_px_y = lambda yv: ((y_top - yv) / max(y_top - y_bot, 1e-6)) * plot_h
    marker_boxes = [
        (to_px_x(dd) - 9, to_px_y(cg) - 9, to_px_x(dd) + 9, to_px_y(cg) + 9, to_px_x(dd), to_px_y(cg))
        for _, dd, cg, _ in scatter_items
    ]
    cand_offsets = [
        (-12, 10, "right"),
        (12, 10, "left"),
        (-12, -12, "right"),
        (12, -12, "left"),
        (-14, 0, "right"),
        (14, 0, "left"),
        (0, 15, "center"),
        (0, -16, "center"),
        (-22, 18, "right"),
        (22, -18, "left"),
    ]

    def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
        ox = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        oy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        return ox * oy

    placed_boxes: list[tuple[float, float, float, float]] = []
    sorted_order = sorted(range(len(scatter_items)), key=lambda i: scatter_items[i][2], reverse=True)
    for i in sorted_order:
        name, dd, cagr, is_strat = scatter_items[i]
        _, _, _, _, m_px, m_py = marker_boxes[i]
        short_lbl = name.replace(" (", "\n(") if " (" in name else name
        lines = short_lbl.split("\n")
        bw = max(58.0, max(len(l) for l in lines) * 4.8 + 8.0)
        bh = 24.0 if len(lines) > 1 else 14.0

        best_off = cand_offsets[0]
        best_cost = 1e12
        for dx, dy, ha_align in cand_offsets:
            if ha_align == "right":
                cx = m_px + dx - bw / 2.0
            elif ha_align == "left":
                cx = m_px + dx + bw / 2.0
            else:
                cx = m_px + dx
            cy = m_py - dy
            cbox = (cx - bw / 2.0 - 2, cy - bh / 2.0 - 2, cx + bw / 2.0 + 2, cy + bh / 2.0 + 2)
            cost = sum(_overlap(cbox, mb[:4]) * 20.0 for mb in marker_boxes)
            cost += sum(_overlap(cbox, pb) * 35.0 for pb in placed_boxes)
            if cbox[0] < 4:
                cost += (4 - cbox[0]) * 40.0
            if cbox[2] > plot_w - 4:
                cost += (cbox[2] - (plot_w - 4)) * 40.0
            if cbox[1] < 4:
                cost += (4 - cbox[1]) * 40.0
            if cbox[3] > plot_h - 4:
                cost += (cbox[3] - (plot_h - 4)) * 40.0
            if cost < best_cost:
                best_cost = cost
                best_off = (dx, dy, ha_align)
                best_box = cbox

        placed_boxes.append(best_box)
        dx, dy, ha_align = best_off
        ax2.annotate(
            short_lbl,
            (dd, cagr),
            xytext=(dx, dy),
            textcoords="offset points",
            ha=ha_align,
            va="center",
            fontsize=7.1,
            fontweight="bold" if is_strat else "normal",
            arrowprops={"arrowstyle": "-", "color": "#94a3b8", "lw": 0.7, "shrinkA": 0, "shrinkB": 3},
        )

    ax2.set_xlabel(f"Max Drawdown {years[0]}–{years[-1]} (%) — Lower is Better", fontsize=10.5, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Compound Annual Growth Rate — CAGR (%)", fontsize=10.5, fontweight="bold")
    ax2.set_title(f"Risk vs. Return Efficiency ({years[0]}–{years[-1]} OOS)", fontsize=12.5, fontweight="bold")
    fig.tight_layout()
    p4 = charts_dir / "annual_returns_and_risk_scatter.png"
    fig.savefig(p4)
    plt.close(fig)
    chart_paths["annual_returns_and_risk_scatter"] = p4

    return chart_paths


WHITELIST_METRIC_TIPS = {
    "CAGR (%)": "Compound Annual Growth Rate: annualized geometric rate of return.",
    "Ann. Vol (%)": "Annualized standard deviation of daily percentage portfolio returns: std(r) * sqrt(252).",
    "Sharpe": "Annualized Sharpe ratio measuring excess return over 3M US Treasury bills per unit annual volatility: (CAGR - Rf) / Vol.",
    "Sortino": "Downside risk-adjusted ratio measuring excess return divided by downside semi-deviation (penalizes negative volatility only).",
    "Deflated SR Prob": "Deflated Sharpe Ratio (Bailey & López de Prado, 2014): statistical probability that the Sharpe ratio is not a false discovery after penalizing for selection bias across multiple strategy iterations.",
    "Deflated Sharpe (Prob)": "Deflated Sharpe Ratio (Bailey & López de Prado, 2014): statistical probability that the Sharpe ratio is not a false discovery after penalizing for selection bias across multiple strategy iterations.",
    "Profit Factor": "Gross payoff asymmetry: ratio of gross dollar profits to gross dollar losses (Target > 1.5).",
    "Avg R": "Average profit per trade expressed in units of initial dollar risk (1.0R). Target > 1.5R.",
}


def _render_metric_tooltip(label: str, tip_text: str | None = None, align: str = "center") -> str:
    """Render metric text with a tiny superscript 'i' icon where mouse-over on the text triggers the tooltip."""
    if not tip_text:
        return label
    clean_tip = tip_text.replace('"', '&quot;').replace("'", "&#39;")
    align_cls = f" tip-{align}" if align in ("left", "right") else ""
    return (
        f'<span class="metric-tip{align_cls}">'
        f'{label}<sup class="metric-tip-sup">ⓘ</sup>'
        f'<span class="metric-tip-popup" role="tooltip">{clean_tip}</span>'
        f'</span>'
    )


def _build_interactive_dashboard_html(results: Dict[str, BacktestResult]) -> str:
    """
    Build a rich, interactive JavaScript dashboard allowing the user to:
    - Slide Start Date and End Date (or pick exact dates / click preset period buttons)
    - Toggle individual strategies & benchmark ETFs on/off
    - Switch between Rebased Dollar Value ($10,000 start) and Cumulative Return (%)
    - Toggle Linear vs Log scale
    - View dynamically rebased Equity Curve, Underwater Drawdown Curve,
      Dynamic Annual Returns Bar Chart, Dynamic Risk vs. Return Scatter Chart,
      and Live Recomputed Metrics Table with consistent full names everywhere.
    """
    styles = _style_map()
    all_dates_set = set()
    for res in results.values():
        if not res.equity_curve.empty:
            all_dates_set.update(pd.to_datetime(res.equity_curve["date"]).dt.strftime("%Y-%m-%d").tolist())
    dates_sorted = sorted(all_dates_set)
    if not dates_sorted:
        return ""

    rf_map: Dict[str, float] = {}
    for res in results.values():
        if not res.equity_curve.empty and "rf_daily" in res.equity_curve.columns:
            eq_tmp = res.equity_curve
            d_strs = pd.to_datetime(eq_tmp["date"]).dt.strftime("%Y-%m-%d")
            for ds, rfv in zip(d_strs, eq_tmp["rf_daily"]):
                if pd.notna(rfv):
                    rf_map[ds] = float(rfv)
            break
    rf_list = [round(rf_map.get(d, 0.035 / 252.0), 8) for d in dates_sorted]

    series_payload = []
    for name, res in results.items():
        if res.equity_curve.empty:
            continue
        st = styles.get(
            name,
            {"color": "#334155", "lw": 2.0, "dash": "solid", "default_on": True},
        )
        eq = res.equity_curve.copy()
        eq["d_str"] = pd.to_datetime(eq["date"]).dt.strftime("%Y-%m-%d")
        eq_map = dict(zip(eq["d_str"], eq["equity"]))
        pos_map = dict(zip(eq["d_str"], eq["n_positions"]))

        vals = []
        pos_list = []
        first_valid = float(eq["equity"].iloc[0]) if not eq.empty else 10000.0
        last_v = first_valid
        for d in dates_sorted:
            if d in eq_map and not np.isnan(eq_map[d]):
                last_v = float(eq_map[d])
            vals.append(round(last_v, 2))
            pos_list.append(int(pos_map.get(d, 1)))

        series_payload.append(
            {
                "name": name,
                "color": st["color"],
                "lw": st["lw"],
                "dash": st.get("dash", "solid"),
                "default_on": bool(st.get("default_on", True)),
                "is_strategy": any(k in name for k in ("Baseline", "ML", "Pure Pre-2022")),
                "equity": vals,
                "n_pos": pos_list,
            }
        )

    data_json = json.dumps({"dates": dates_sorted, "rf_daily": rf_list, "series": series_payload})

    return f"""
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <div class="interactive-panel">
      <div class="panel-header">
        <div>
          <h2 style="margin:0 0 4px 0;">1. Interactive Strategy &amp; Benchmark Explorer (Dynamic Date Re-Basing)</h2>
          <p style="margin:0; color:#4b5563; font-size:13.5px;">
            Slide the <b>Start Date</b> or <b>End Date</b> (or click a preset period) to dynamically rebase all selected strategies &amp; indexes to <b>$10,000</b> on your chosen start date. All 4 charts and the table update in real time.
          </p>
        </div>
        <div class="mode-toggles">
          <label class="toggle-lbl"><input type="radio" name="y_mode" value="dollar" checked onchange="updateInteractiveCharts()"/> Rebased $10,000</label>
          <label class="toggle-lbl"><input type="radio" name="y_mode" value="pct" onchange="updateInteractiveCharts()"/> Cumulative Return (%)</label>
          <label class="toggle-lbl" style="margin-left:10px;"><input type="checkbox" id="log_scale_cb" onchange="updateInteractiveCharts()"/> Log Scale</label>
        </div>
      </div>

      <!-- Date Controls: Quick Presets + Date Inputs + Dual Range Sliders -->
      <div class="date-controls-card">
        <div class="preset-row">
          <span class="control-title">Quick Periods:</span>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2022-01-03', '9999-12-31')">Full OOS (2022–2026)</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2022-01-03', '2022-12-30')">2022 Bear Market</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2023-01-03', '9999-12-31')">Modern AI Cycle (2023–2026)</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2024-01-02', '9999-12-31')">2024–2026</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2025-01-02', '9999-12-31')">2025–2026</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2026-01-02', '9999-12-31')">2026 YTD</button>
          <button type="button" class="btn-preset" onclick="setPeriodPreset('2023-01-03', '2025-12-31')">2023–2025 Only</button>
        </div>

        <div class="dual-slider-header">
          <div class="date-input-group">
            <span><b>Start Date:</b> <input type="date" id="start_date_picker" onchange="onDateInputChanged('start')"/></span>
          </div>
          <div id="window_summary_badge" class="idx-badge"></div>
          <div class="date-input-group">
            <span><b>End Date:</b> <input type="date" id="end_date_picker" onchange="onDateInputChanged('end')"/></span>
          </div>
        </div>

        <div class="dual-slider-wrap">
          <div class="dual-slider-track"></div>
          <div id="dual_slider_fill" class="dual-slider-fill"></div>
          <input type="range" id="start_slider" min="0" max="{len(dates_sorted) - 1}" value="0" oninput="onSliderInput('start')" class="dual-range-input"/>
          <input type="range" id="end_slider" min="0" max="{len(dates_sorted) - 1}" value="{len(dates_sorted) - 1}" oninput="onSliderInput('end')" class="dual-range-input"/>
        </div>
        <div id="dual_slider_ticks" class="dual-slider-ticks"></div>
      </div>

      <!-- Fund / Strategy Picker Pills -->
      <div class="funds-card">
        <div class="funds-header">
          <span class="control-title">Select Strategies &amp; Benchmark Indexes:</span>
          <div>
            <button type="button" class="btn-mini" onclick="setFundSelection('all')">Select All</button>
            <button type="button" class="btn-mini" onclick="setFundSelection('default')">Default View</button>
            <button type="button" class="btn-mini" onclick="setFundSelection('strategies_vs_core_idx')">Strategies vs SPY/QQQ/VGT/SMH</button>
            <button type="button" class="btn-mini" onclick="setFundSelection('cash_strategies')">Cash-Only Swing vs Indexes</button>
          </div>
        </div>
        <div id="fund_pills_container" class="pills-wrap"></div>
      </div>

      <!-- Plotly Interactive Charts: Equity + Drawdown -->
      <div class="chart-card" style="margin-bottom: 18px;">
        <div id="plotly_equity_chart" style="width:100%; height:500px;"></div>
      </div>
      <div class="chart-card" style="margin-bottom: 18px;">
        <div id="plotly_dd_chart" style="width:100%; height:340px;"></div>
      </div>

      <!-- Dynamic 2-Column Row: Annual Returns Bar Chart & Risk vs. Return Scatter Chart -->
      <div class="two-col-charts" style="margin-bottom: 18px;">
        <div class="chart-card">
          <div id="plotly_annual_bars" style="width:100%; height:520px;"></div>
        </div>
        <div class="chart-card">
          <div id="plotly_risk_scatter" style="width:100%; height:520px;"></div>
        </div>
      </div>

      <!-- Dynamic Live Performance Table for Selected Date Window -->
      <div class="chart-card">
        <h3 id="live_table_title" style="margin-top:0;">Live Recomputed Metrics for Selected Window</h3>
        <div style="overflow-x:auto;">
          <table id="live_metrics_table" style="margin-bottom:0;">
            <thead>
              <tr>
                <th>Strategy / Benchmark</th>
                <th>Start $</th>
                <th>Ending $</th>
                <th>Total Return (%)</th>
                <th>{_render_metric_tooltip("CAGR (%)", WHITELIST_METRIC_TIPS["CAGR (%)"])}</th>
                <th>{_render_metric_tooltip("Ann. Vol (%)", WHITELIST_METRIC_TIPS["Ann. Vol (%)"])}</th>
                <th>{_render_metric_tooltip("Sharpe", WHITELIST_METRIC_TIPS["Sharpe"])}</th>
                <th>{_render_metric_tooltip("Sortino", WHITELIST_METRIC_TIPS["Sortino"])}</th>
                <th>Max Drawdown (%)</th>
                <th>100% Cash Days (%)</th>
              </tr>
            </thead>
            <tbody id="live_metrics_tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <script>
    const DASH_DATA = {data_json};
    let activeFunds = new Set();

    function initDashboard() {{
      const pillsDiv = document.getElementById('fund_pills_container');
      pillsDiv.innerHTML = '';
      DASH_DATA.series.forEach((s, idx) => {{
        if (s.default_on) activeFunds.add(s.name);
        const lbl = document.createElement('label');
        lbl.className = 'fund-pill ' + (s.default_on ? 'active' : '');
        lbl.style.borderColor = s.color;
        lbl.id = 'pill_' + idx;

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = s.default_on;
        cb.onchange = () => {{
          if (cb.checked) {{
            activeFunds.add(s.name);
            lbl.classList.add('active');
          }} else {{
            activeFunds.delete(s.name);
            lbl.classList.remove('active');
          }}
          updateInteractiveCharts();
        }};

        const dot = document.createElement('span');
        dot.className = 'color-dot';
        dot.style.backgroundColor = s.color;

        const txt = document.createElement('span');
        txt.textContent = s.name;

        lbl.appendChild(cb);
        lbl.appendChild(dot);
        lbl.appendChild(txt);
        pillsDiv.appendChild(lbl);
      }});

      // Position year tick labels at their exact trading-day index percentage along the slider track
      const ticksDiv = document.getElementById('dual_slider_ticks');
      if (ticksDiv) {{
        ticksDiv.innerHTML = '';
        const maxIdx = Math.max(DASH_DATA.dates.length - 1, 1);
        const seenYears = new Set();
        DASH_DATA.dates.forEach((d, i) => {{
          const yr = d.substring(0, 4);
          if (!seenYears.has(yr)) {{
            seenYears.add(yr);
            const pct = (i / maxIdx) * 100.0;
            const spn = document.createElement('span');
            spn.className = 'year-tick-mark';
            spn.style.left = pct + '%';
            spn.textContent = yr;
            ticksDiv.appendChild(spn);
          }}
        }});
      }}

      const d0 = DASH_DATA.dates[0];
      const dN = DASH_DATA.dates[DASH_DATA.dates.length - 1];
      const sp = document.getElementById('start_date_picker');
      const ep = document.getElementById('end_date_picker');
      sp.min = d0; sp.max = dN; sp.value = d0;
      ep.min = d0; ep.max = dN; ep.value = dN;

      updateInteractiveCharts();
      window.addEventListener('resize', () => {{
        updateInteractiveCharts();
      }});
    }}

    function setFundSelection(mode) {{
      activeFunds.clear();
      DASH_DATA.series.forEach((s, idx) => {{
        let on = false;
        if (mode === 'all') on = true;
        else if (mode === 'default') on = s.default_on;
        else if (mode === 'strategies_vs_core_idx') {{
          on = [
            'Baseline (SMH Bull Core + Swing)',
            'ML (SMH Bull Core + Swing)',
            'Pure Pre-2022 Semi (SMH Bull Core + Swing)',
            'Baseline (Adaptive L_t)',
            'ML (LightGBM + Platt)',
            'SMH Buy & Hold',
            'VGT Buy & Hold',
            'QQQ Buy & Hold',
            'S&P 500 (SPY) Buy & Hold'
          ].includes(s.name);
        }} else if (mode === 'cash_strategies') {{
          on = [
            'Baseline (Adaptive L_t)',
            'ML (LightGBM + Platt)',
            'Pure Pre-2022 Semi (Cash Swing)',
            'SMH Buy & Hold',
            'VGT Buy & Hold',
            'QQQ Buy & Hold',
            'S&P 500 (SPY) Buy & Hold',
            '3M T-Bill Cash (DTB3)'
          ].includes(s.name);
        }}
        const pill = document.getElementById('pill_' + idx);
        const cb = pill.querySelector('input');
        cb.checked = on;
        if (on) {{
          activeFunds.add(s.name);
          pill.classList.add('active');
        }} else {{
          pill.classList.remove('active');
        }}
      }});
      updateInteractiveCharts();
    }}

    function findClosestDateIndex(targetStr, isEnd) {{
      const dates = DASH_DATA.dates;
      if (targetStr <= dates[0]) return 0;
      if (targetStr >= dates[dates.length - 1]) return dates.length - 1;
      for (let i = 0; i < dates.length; i++) {{
        if (dates[i] >= targetStr) {{
          return isEnd && dates[i] > targetStr && i > 0 ? i - 1 : i;
        }}
      }}
      return dates.length - 1;
    }}

    function setPeriodPreset(startStr, endStr) {{
      let sIdx = findClosestDateIndex(startStr, false);
      let eIdx = findClosestDateIndex(endStr, true);
      if (sIdx >= eIdx) sIdx = Math.max(0, eIdx - 5);
      document.getElementById('start_slider').value = sIdx;
      document.getElementById('end_slider').value = eIdx;
      updateInteractiveCharts();
    }}

    function onSliderInput(which) {{
      let sIdx = parseInt(document.getElementById('start_slider').value, 10);
      let eIdx = parseInt(document.getElementById('end_slider').value, 10);
      if (eIdx <= sIdx + 2) {{
        if (which === 'start') {{
          sIdx = Math.max(0, eIdx - 2);
          document.getElementById('start_slider').value = sIdx;
        }} else {{
          eIdx = Math.min(DASH_DATA.dates.length - 1, sIdx + 2);
          document.getElementById('end_slider').value = eIdx;
        }}
      }}
      updateInteractiveCharts();
    }}

    function onDateInputChanged(which) {{
      const sVal = document.getElementById('start_date_picker').value;
      const eVal = document.getElementById('end_date_picker').value;
      let sIdx = findClosestDateIndex(sVal, false);
      let eIdx = findClosestDateIndex(eVal, true);
      if (eIdx <= sIdx + 2) {{
        if (which === 'start') sIdx = Math.max(0, eIdx - 2);
        else eIdx = Math.min(DASH_DATA.dates.length - 1, sIdx + 2);
      }}
      document.getElementById('start_slider').value = sIdx;
      document.getElementById('end_slider').value = eIdx;
      updateInteractiveCharts();
    }}

    function computeWindowStats(eqSlice, posSlice, rfSlice) {{
      const n = eqSlice.length;
      if (n < 2) return {{ endDollar: 10000, totRet: 0, cagr: 0, vol: 0, sharpe: 0, sortino: 0, maxDd: 0, cashPct: 0 }};
      const startVal = eqSlice[0];
      const endVal = eqSlice[n - 1];
      const endDollar = 10000.0 * (endVal / startVal);
      const totRet = (endVal / startVal - 1.0) * 100.0;
      const nYears = Math.max((n - 1) / 252.0, 1e-4);
      const cagr = (Math.pow(endVal / startVal, 1.0 / nYears) - 1.0) * 100.0;

      const exRets = [];
      let sumEx = 0.0;
      let sumDownSq = 0.0;
      let nDown = 0;
      let peak = eqSlice[0];
      let maxDd = 0.0;
      let cashDays = (posSlice[0] === 0 ? 1 : 0);

      for (let i = 1; i < n; i++) {{
        const r = (eqSlice[i] / eqSlice[i - 1]) - 1.0;
        const rf = rfSlice ? rfSlice[i] : 0.0;
        const ex = r - rf;
        exRets.push(ex);
        sumEx += ex;
        if (ex < 0) {{
          sumDownSq += ex * ex;
          nDown++;
        }}
        if (eqSlice[i] > peak) peak = eqSlice[i];
        const dd = (eqSlice[i] / peak) - 1.0;
        if (dd < maxDd) maxDd = dd;
        if (posSlice[i] === 0) cashDays++;
      }}

      const meanEx = sumEx / exRets.length;
      let varSum = 0.0;
      for (let i = 0; i < exRets.length; i++) {{
        const d = exRets[i] - meanEx;
        varSum += d * d;
      }}
      const stdEx = exRets.length > 1 ? Math.sqrt(varSum / (exRets.length - 1)) : 0.0;
      const vol = stdEx * Math.sqrt(252.0) * 100.0;
      const sharpe = stdEx > 1e-7 ? (meanEx / stdEx) * Math.sqrt(252.0) : 0.0;
      const downStd = nDown > 0 ? Math.sqrt(sumDownSq / nDown) : 0.0;
      const sortino = downStd > 1e-7 ? (meanEx / downStd) * Math.sqrt(252.0) : 0.0;
      const cashPct = (cashDays / n) * 100.0;

      return {{
        endDollar,
        totRet,
        cagr,
        vol,
        sharpe,
        sortino,
        maxDd: Math.abs(maxDd) * 100.0,
        cashPct,
      }};
    }}

    function computeYearlyReturnsInWindow(dateSlice, eqSlice) {{
      // Group indices by calendar year within the selected [startDate, endDate] slice
      const byYear = {{}};
      for (let i = 0; i < dateSlice.length; i++) {{
        const yr = dateSlice[i].substring(0, 4);
        if (!byYear[yr]) byYear[yr] = [];
        byYear[yr].push(i);
      }}
      const years = Object.keys(byYear).sort();
      const maxDatasetDate = DASH_DATA.dates[DASH_DATA.dates.length - 1];
      const maxDatasetYear = maxDatasetDate.substring(0, 4);
      const yRets = [];
      for (let k = 0; k < years.length; k++) {{
        const yr = years[k];
        const idxs = byYear[yr];
        const firstIdx = idxs[0] > 0 ? idxs[0] - 1 : idxs[0];
        const lastIdx = idxs[idxs.length - 1];
        const lastDateOfYr = dateSlice[lastIdx];
        const isFullDecEnd = lastDateOfYr.endsWith('-12-31') || lastDateOfYr.endsWith('-12-30') || lastDateOfYr.endsWith('-12-29');
        const r = ((eqSlice[lastIdx] / eqSlice[firstIdx]) - 1.0) * 100.0;
        const yrLabel = (yr === maxDatasetYear && !isFullDecEnd) ? (yr + ' YTD') : yr;
        yRets.push({{ year: yrLabel, ret: Math.round(r) }});
      }}
      return yRets;
    }}

    function updateInteractiveCharts() {{
      const sIdx = parseInt(document.getElementById('start_slider').value, 10);
      const eIdx = parseInt(document.getElementById('end_slider').value, 10);
      const maxIdx = Math.max(DASH_DATA.dates.length - 1, 1);
      const startDate = DASH_DATA.dates[sIdx];
      const endDate = DASH_DATA.dates[eIdx];

      document.getElementById('start_date_picker').value = startDate;
      document.getElementById('end_date_picker').value = endDate;
      document.getElementById('window_summary_badge').textContent =
        startDate + '  →  ' + endDate + ' (' + (eIdx - sIdx + 1) + ' trading days)';

      // Update blue highlight bar between left and right slider thumbs
      const leftPct = (sIdx / maxIdx) * 100.0;
      const rightPct = (eIdx / maxIdx) * 100.0;
      const fillEl = document.getElementById('dual_slider_fill');
      if (fillEl) {{
        fillEl.style.left = leftPct + '%';
        fillEl.style.width = Math.max(0, rightPct - leftPct) + '%';
      }}

      const yMode = document.querySelector('input[name="y_mode"]:checked').value;
      const useLog = document.getElementById('log_scale_cb').checked;
      const dateSlice = DASH_DATA.dates.slice(sIdx, eIdx + 1);
      const rfSlice = DASH_DATA.rf_daily ? DASH_DATA.rf_daily.slice(sIdx, eIdx + 1) : null;

      const eqTraces = [];
      const ddTraces = [];
      const barTraces = [];
      const scatterTraces = [];
      const tableRows = [];
      let barYearLabels = [];

      DASH_DATA.series.forEach(s => {{
        if (!activeFunds.has(s.name)) return;
        const eqSlice = s.equity.slice(sIdx, eIdx + 1);
        const posSlice = s.n_pos.slice(sIdx, eIdx + 1);
        const baseVal = eqSlice[0];

        const yVals = [];
        const ddVals = [];
        let peak = baseVal;
        for (let i = 0; i < eqSlice.length; i++) {{
          const v = eqSlice[i];
          if (yMode === 'dollar') {{
            yVals.push(10000.0 * (v / baseVal));
          }} else {{
            yVals.push(((v / baseVal) - 1.0) * 100.0);
          }}
          if (v > peak) peak = v;
          ddVals.push(((v / peak) - 1.0) * 100.0);
        }}

        const stats = computeWindowStats(eqSlice, posSlice, rfSlice);
        tableRows.push({{ name: s.name, color: s.color, is_strategy: s.is_strategy, ...stats }});

        const shortStat = (stats.totRet >= 0 ? '+' : '') + stats.totRet.toFixed(1) + '% | SR ' + stats.sharpe.toFixed(2);
        eqTraces.push({{
          x: dateSlice,
          y: yVals,
          mode: 'lines',
          name: s.name + ' (' + shortStat + ')',
          line: {{ color: s.color, width: s.lw, dash: s.dash }},
          hovertemplate: '<b>' + s.name + '</b><br>Date: %{{x}}<br>' +
            (yMode === 'dollar' ? 'Value: $%{{y:,.0f}}' : 'Return: %{{y:+.2f}}%') + '<extra></extra>'
        }});

        ddTraces.push({{
          x: dateSlice,
          y: ddVals,
          mode: 'lines',
          name: s.name + ' (Max DD: -' + stats.maxDd.toFixed(1) + '%)',
          line: {{ color: s.color, width: Math.max(1.5, s.lw - 0.3), dash: s.dash }},
          hovertemplate: '<b>' + s.name + '</b><br>Date: %{{x}}<br>Drawdown: %{{y:.2f}}%<extra></extra>'
        }});

        // Annual returns bar trace within selected window (whole percentages, discrete year labels)
        const yrData = computeYearlyReturnsInWindow(dateSlice, eqSlice);
        barYearLabels = yrData.map(d => d.year);
        barTraces.push({{
          x: barYearLabels,
          y: yrData.map(d => d.ret),
          type: 'bar',
          name: s.name,
          marker: {{ color: s.color }},
          hovertemplate: '<b>' + s.name + '</b><br>Year: %{{x}}<br>Return: %{{y:+.0f}}%<extra></extra>'
        }});

        // Risk vs Return scatter trace with full consistent name + Sharpe in legend
        scatterTraces.push({{
          x: [stats.maxDd],
          y: [stats.cagr],
          mode: 'markers',
          type: 'scatter',
          name: s.name + ' (SR ' + stats.sharpe.toFixed(2) + ')',
          _rawName: s.name,
          _isStrategy: s.is_strategy,
          _maxDd: stats.maxDd,
          _cagr: stats.cagr,
          marker: {{
            color: s.color,
            size: s.is_strategy ? 14 : 11,
            symbol: s.is_strategy ? 'diamond' : 'circle',
            line: {{ color: '#0f172a', width: 1 }}
          }},
          hovertemplate: '<b>' + s.name + '</b><br>CAGR: ' + stats.cagr.toFixed(2) +
            '%<br>Max Drawdown: -' + stats.maxDd.toFixed(2) +
            '%<br>Total Return: ' + (stats.totRet >= 0 ? '+' : '') + stats.totRet.toFixed(2) +
            '%<br>Sharpe: ' + stats.sharpe.toFixed(2) + '<extra></extra>'
        }});
      }});

      // Compute padded X/Y ranges (clamping min Drawdown near 0%) and non-overlapping 2-line annotations
      let minX = -1.8, maxX = 45.0, minY = 0.0, maxY = 50.0;
      if (scatterTraces.length > 0) {{
        const xs = scatterTraces.map(t => t._maxDd);
        const ys = scatterTraces.map(t => t._cagr);
        const rawMinX = Math.min(...xs);
        const rawMaxX = Math.max(...xs);
        const rawMinY = Math.min(...ys);
        const rawMaxY = Math.max(...ys);
        const spanX = Math.max(rawMaxX - rawMinX, 10.0);
        const spanY = Math.max(rawMaxY - rawMinY, 15.0);
        minX = Math.max(-1.8, rawMinX - spanX * 0.14);
        maxX = rawMaxX + spanX * 0.26;
        minY = rawMinY - spanY * 0.18;
        maxY = rawMaxY + spanY * 0.18;
      }}

      const scatterEl = document.getElementById('plotly_risk_scatter');
      const plotW = Math.max(320.0, (scatterEl && scatterEl.clientWidth ? scatterEl.clientWidth : 548) - 88.0);
      const plotH = Math.max(220.0, (scatterEl && scatterEl.clientHeight ? scatterEl.clientHeight : 520) - 201.0);
      const toPxX = x => ((x - minX) / Math.max(maxX - minX, 1e-6)) * plotW;
      const toPxY = y => ((maxY - y) / Math.max(maxY - minY, 1e-6)) * plotH;

      const markerBoxes = scatterTraces.map(t => {{
        const px = toPxX(t._maxDd);
        const py = toPxY(t._cagr);
        return {{ x1: px - 10, y1: py - 10, x2: px + 10, y2: py + 10, px, py }};
      }});

      const placedBoxes = [];
      const candidateOffsets = [
        {{ ax: -54, ay: -18 }},
        {{ ax: 54, ay: -18 }},
        {{ ax: -54, ay: 18 }},
        {{ ax: 54, ay: 18 }},
        {{ ax: -64, ay: 0 }},
        {{ ax: 64, ay: 0 }},
        {{ ax: 0, ay: -28 }},
        {{ ax: 0, ay: 28 }},
        {{ ax: -72, ay: -30 }},
        {{ ax: 72, ay: -30 }},
        {{ ax: -72, ay: 30 }},
        {{ ax: 72, ay: 30 }},
      ];

      function boxOverlapArea(a, b) {{
        const ox = Math.max(0, Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1));
        const oy = Math.max(0, Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1));
        return ox * oy;
      }}

      // Sort points by CAGR descending so top strategies get first choice of label placement
      const sortedIndices = scatterTraces.map((_, i) => i).sort((a, b) => scatterTraces[b]._cagr - scatterTraces[a]._cagr);
      const scatterAnnotations = [];

      sortedIndices.forEach(idx => {{
        const t = scatterTraces[idx];
        const mBox = markerBoxes[idx];
        // Wrap parenthetical part onto second line so label width is compact (~95px instead of 220px)
        const shortText = t._rawName.includes(' (')
          ? t._rawName.replace(' (', '<br>(')
          : t._rawName;
        const lines = shortText.split('<br>');
        const maxChars = Math.max(...lines.map(l => l.length));
        const boxW = Math.max(66, maxChars * 5.6 + 10);
        const boxH = lines.length > 1 ? 28 : 16;

        let bestOff = candidateOffsets[0];
        let bestScore = 1e12;

        candidateOffsets.forEach(off => {{
          const cx = mBox.px + off.ax;
          const cy = mBox.py + off.ay;
          const candBox = {{
            x1: cx - boxW / 2 - 3,
            y1: cy - boxH / 2 - 2,
            x2: cx + boxW / 2 + 3,
            y2: cy + boxH / 2 + 2
          }};
          let score = 0;
          // Penalize overlapping any marker
          markerBoxes.forEach(mb => {{
            score += boxOverlapArea(candBox, mb) * 20.0;
          }});
          // Penalize overlapping any already placed label box
          placedBoxes.forEach(pb => {{
            score += boxOverlapArea(candBox, pb) * 35.0;
          }});
          // Penalize going outside the plot frame
          if (candBox.x1 < 4) score += (4 - candBox.x1) * 40.0;
          if (candBox.x2 > plotW - 4) score += (candBox.x2 - (plotW - 4)) * 40.0;
          if (candBox.y1 < 4) score += (4 - candBox.y1) * 40.0;
          if (candBox.y2 > plotH - 4) score += (candBox.y2 - (plotH - 4)) * 40.0;
          // Mild preference for closer offsets
          score += Math.hypot(off.ax, off.ay) * 0.08;

          if (score < bestScore) {{
            bestScore = score;
            bestOff = off;
          }}
        }});

        const finalCx = mBox.px + bestOff.ax;
        const finalCy = mBox.py + bestOff.ay;
        placedBoxes.push({{
          x1: finalCx - boxW / 2 - 3,
          y1: finalCy - boxH / 2 - 2,
          x2: finalCx + boxW / 2 + 3,
          y2: finalCy + boxH / 2 + 2
        }});

        scatterAnnotations.push({{
          x: t._maxDd,
          y: t._cagr,
          xref: 'x',
          yref: 'y',
          text: t._isStrategy ? '<b>' + shortText + '</b>' : shortText,
          showarrow: true,
          arrowhead: 0,
          arrowwidth: 1,
          arrowcolor: '#94a3b8',
          ax: bestOff.ax,
          ay: bestOff.ay,
          font: {{ size: 9.8, color: '#0f172a' }},
          bgcolor: 'rgba(255,255,255,0.86)',
          borderpad: 2
        }});
      }});

      const eqLayout = {{
        title: {{
          text: (yMode === 'dollar' ? 'Rebased Growth of $10,000' : 'Cumulative Percentage Return (%)') +
                ' from ' + startDate + ' to ' + endDate,
          font: {{ size: 15, color: '#0f172a' }}
        }},
        margin: {{ l: 68, r: 24, t: 48, b: 42 }},
        hovermode: 'x unified',
        xaxis: {{ gridcolor: '#e2e8f0' }},
        yaxis: {{
          title: yMode === 'dollar' ? 'Portfolio Value ($ USD)' : 'Cumulative Return (%)',
          tickprefix: yMode === 'dollar' ? '$' : '',
          ticksuffix: yMode === 'pct' ? '%' : '',
          type: (useLog && yMode === 'dollar') ? 'log' : 'linear',
          gridcolor: '#e2e8f0'
        }},
        legend: {{ orientation: 'h', yanchor: 'bottom', y: -0.32, xanchor: 'left', x: 0, font: {{ size: 11.5 }} }},
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff'
      }};

      const ddLayout = {{
        title: {{
          text: 'Underwater Drawdown (%) Within Window (' + startDate + ' to ' + endDate + ')',
          font: {{ size: 14, color: '#0f172a' }}
        }},
        margin: {{ l: 68, r: 24, t: 42, b: 36 }},
        hovermode: 'x unified',
        xaxis: {{ gridcolor: '#e2e8f0' }},
        yaxis: {{ title: 'Drawdown from Peak (%)', ticksuffix: '%', gridcolor: '#e2e8f0' }},
        showlegend: false,
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff'
      }};

      const barLayout = {{
        title: {{
          text: 'Annual Returns by Year (%) (' + startDate + ' to ' + endDate + ')',
          font: {{ size: 14, color: '#0f172a' }}
        }},
        barmode: 'group',
        margin: {{ l: 58, r: 18, t: 46, b: 155 }},
        xaxis: {{
          title: {{ text: 'Calendar Year', standoff: 16 }},
          type: 'category',
          tickmode: 'array',
          tickvals: barYearLabels,
          ticktext: barYearLabels,
          gridcolor: '#e2e8f0'
        }},
        yaxis: {{
          title: 'Calendar Year Return (%)',
          tickformat: '.0f',
          ticksuffix: '%',
          gridcolor: '#e2e8f0',
          zeroline: true,
          zerolinecolor: '#334155'
        }},
        legend: {{ orientation: 'h', yanchor: 'top', y: -0.26, xanchor: 'left', x: 0, font: {{ size: 10.2 }} }},
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff'
      }};

      const scatterLayout = {{
        title: {{
          text: 'Risk vs. Return Efficiency (' + startDate + ' to ' + endDate + ')',
          font: {{ size: 14, color: '#0f172a' }}
        }},
        margin: {{ l: 62, r: 26, t: 46, b: 155 }},
        xaxis: {{
          title: {{ text: 'Max Drawdown in Window (%) — Lower is Better', standoff: 18 }},
          ticksuffix: '%',
          range: [minX, maxX],
          gridcolor: '#e2e8f0'
        }},
        yaxis: {{
          title: 'Annualized CAGR (%)',
          ticksuffix: '%',
          range: [minY, maxY],
          gridcolor: '#e2e8f0'
        }},
        annotations: scatterAnnotations,
        legend: {{ orientation: 'h', yanchor: 'top', y: -0.26, xanchor: 'left', x: 0, font: {{ size: 10.2 }} }},
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff'
      }};

      if (typeof Plotly !== 'undefined') {{
        Plotly.react('plotly_equity_chart', eqTraces, eqLayout, {{ responsive: true, displayModeBar: true }});
        Plotly.react('plotly_dd_chart', ddTraces, ddLayout, {{ responsive: true, displayModeBar: false }});
        Plotly.react('plotly_annual_bars', barTraces, barLayout, {{ responsive: true, displayModeBar: false }});
        Plotly.react('plotly_risk_scatter', scatterTraces, scatterLayout, {{ responsive: true, displayModeBar: false }});
      }}

      // Sort table rows by Total Return descending
      tableRows.sort((a, b) => b.totRet - a.totRet);
      document.getElementById('live_table_title').textContent =
        'Live Recomputed Performance (' + startDate + ' → ' + endDate + ', Rebased to $10,000)';
      const tbody = document.getElementById('live_metrics_tbody');
      tbody.innerHTML = tableRows.map(r => {{
        const retColor = r.totRet >= 0 ? '#059669' : '#dc2626';
        const weight = r.is_strategy ? '600' : '400';
        return `<tr style="font-weight:${{weight}};">
          <td><span class="color-dot" style="background:${{r.color}};display:inline-block;margin-right:7px;"></span>${{r.name}}</td>
          <td>$10,000</td>
          <td>$${{Math.round(r.endDollar).toLocaleString()}}</td>
          <td style="color:${{retColor}};font-weight:700;">${{(r.totRet >= 0 ? '+' : '') + r.totRet.toFixed(2)}}%</td>
          <td>${{(r.cagr >= 0 ? '+' : '') + r.cagr.toFixed(2)}}%</td>
          <td>${{r.vol.toFixed(1)}}%</td>
          <td>${{r.sharpe.toFixed(2)}}</td>
          <td>${{r.sortino.toFixed(2)}}</td>
          <td style="color:#dc2626;">-${{r.maxDd.toFixed(2)}}%</td>
          <td>${{r.cashPct.toFixed(1)}}%</td>
        </tr>`;
      }}).join('');
    }}

    window.addEventListener('DOMContentLoaded', initDashboard);
    </script>
    """


def _format_comparison_df(results: Dict[str, BacktestResult], attr: str) -> pd.DataFrame:
    rows = []
    for label, res in results.items():
        m = getattr(res, attr)
        rows.append(
            {
                "Strategy / Benchmark": label,
                "Total Return (%)": m.get("total_return_pct", 0.0),
                "CAGR (%)": m.get("cagr_pct", 0.0),
                "Sharpe": m.get("sharpe", 0.0),
                "Deflated SR Prob": m.get("deflated_sharpe_prob", 0.0),
                "Sortino": m.get("sortino", 0.0),
                "Max DD (%)": m.get("max_dd_pct", 0.0),
                "100% Cash Days (%)": m.get("cash_days_pct", 0.0),
                "Trades": m.get("trades", 0),
                "Win Rate (%)": m.get("win_rate_pct", 0.0),
                "Profit Factor": m.get("profit_factor", 0.0),
                "Avg R": m.get("avg_r", 0.0),
            }
        )
    return pd.DataFrame(rows)


def _img_to_base64_uri(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


CASH_SWING_HURDLES = {
    "ai_sharpe": 1.50,
    "dsr": 0.95,
    "pf": 1.50,
    "ai_max_dd": 36.0,
    "oos_max_dd": 40.0,
    "oos_sharpe": 1.00,
    "bear_ret": -25.0,
    "bear_dd": 25.0,
    "bear_cash": 80.0,
}

SMH_CORE_HURDLES = {
    "ai_sharpe": 1.60,
    "dsr": 0.95,
    "pf": 2.00,
    "ai_max_dd": 36.0,
    "oos_max_dd": 40.0,
    "oos_sharpe": 1.20,
    "bear_ret": -40.0,
    "bear_dd": 40.0,
    "bear_cash": 80.0,
}


def _build_institutional_gates(
    ml_res: BacktestResult | None,
    base_res: BacktestResult | None,
    smh_res: BacktestResult | None,
    mode_name: str,
    hurdles: dict,
    cal_stats: dict,
    trial_k: int = 14,
) -> Tuple[pd.DataFrame, List[dict], bool]:
    m_ov = ml_res.metrics_overall if ml_res else {}
    m_ai = ml_res.metrics_ai_era if ml_res else {}
    m_22 = ml_res.metrics_2022_bear if ml_res else {}

    b_ov = base_res.metrics_overall if base_res else {}
    b_ai = base_res.metrics_ai_era if base_res else {}

    smh_ov_dd = smh_res.metrics_overall.get("max_dd_pct", 45.14) if smh_res else 45.14
    smh_ai_dd = smh_res.metrics_ai_era.get("max_dd_pct", 35.74) if smh_res else 35.74

    ai_sr = m_ai.get("sharpe", 0.0)
    ai_dsr = m_ai.get("deflated_sharpe_prob", 0.0)
    ai_pf = m_ai.get("profit_factor", 0.0)
    ov_pf = m_ov.get("profit_factor", 0.0)
    ai_dd = m_ai.get("max_dd_pct", 100.0)
    ov_dd = m_ov.get("max_dd_pct", 100.0)
    ov_sr = m_ov.get("sharpe", 0.0)
    ret_22 = m_22.get("total_return_pct", -100.0)
    dd_22 = m_22.get("max_dd_pct", 100.0)
    cash_22 = m_22.get("cash_days_pct", 0.0)

    bss = cal_stats.get("brier_skill_score", np.nan)
    base_ai_sr = b_ai.get("sharpe", 0.0)
    sr_lift = ai_sr - base_ai_sr
    base_ai_dd = b_ai.get("max_dd_pct", 0.0)
    dd_reduction = base_ai_dd - ai_dd
    ai_sortino = m_ai.get("sortino", 0.0)
    base_ai_sortino = b_ai.get("sortino", 0.0)
    sortino_lift = ai_sortino - base_ai_sortino
    ai_cagr = m_ai.get("cagr_pct", 0.0)
    base_ai_cagr = b_ai.get("cagr_pct", 0.0)
    cagr_lift = ai_cagr - base_ai_cagr

    gates = [
        {
            "Gate": f"Gate 1: Modern AI Era Sharpe >= {hurdles['ai_sharpe']:.2f} (2023-2026)",
            "Value": f"{ai_sr:.2f}",
            "Status": "PASS" if ai_sr >= hurdles["ai_sharpe"] else "FAIL",
        },
        {
            "Gate": f"Gate 2: Deflated Sharpe Probability >= {hurdles['dsr']:.2f} (K={trial_k} trials)",
            "Value": f"{ai_dsr:.3f}",
            "Status": "PASS" if ai_dsr >= hurdles["dsr"] else "FAIL",
        },
        {
            "Gate": f"Gate 3: Profit Factor >= {hurdles['pf']:.2f} (Gross Payoff Asymmetry)",
            "Value": f"AI: {ai_pf:.2f} | OOS: {ov_pf:.2f}",
            "Status": "PASS" if (ai_pf >= hurdles["pf"] and ov_pf >= hurdles["pf"]) else "FAIL",
        },
        {
            "Gate": f"Gate 4a: Modern AI Era Max DD <= {hurdles['ai_max_dd']:.1f}% (vs SMH {smh_ai_dd:.1f}%)",
            "Value": f"{ai_dd:.2f}%",
            "Status": "PASS" if ai_dd <= hurdles["ai_max_dd"] else "FAIL",
        },
        {
            "Gate": f"Gate 4b: Full OOS Max DD <= {hurdles['oos_max_dd']:.1f}% (vs SMH {smh_ov_dd:.1f}%)",
            "Value": f"{ov_dd:.2f}%",
            "Status": "PASS" if ov_dd <= hurdles["oos_max_dd"] else "FAIL",
        },
        {
            "Gate": f"Gate 5: Full OOS Sharpe >= {hurdles['oos_sharpe']:.2f} (2022-2026 Full Cycle)",
            "Value": f"{ov_sr:.2f}",
            "Status": "PASS" if ov_sr >= hurdles["oos_sharpe"] else "FAIL",
        },
        {
            "Gate": f"Gate 6: 2022 Bear Stress (Ret >= {hurdles['bear_ret']:.0f}%, DD <= {hurdles['bear_dd']:.0f}%, Cash >= {hurdles['bear_cash']:.0f}%)",
            "Value": f"Ret: {ret_22:.1f}% | DD: {dd_22:.1f}% | Cash: {cash_22:.1f}%",
            "Status": "PASS"
            if (ret_22 >= hurdles["bear_ret"] and dd_22 <= hurdles["bear_dd"] and cash_22 >= hurdles["bear_cash"])
            else "FAIL",
        },
        {
            "Gate": "Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)",
            "Value": f"BSS: {bss:.4f} | SR Lift: {sr_lift:+.2f} | Sortino Lift: {sortino_lift:+.2f} | CAGR Lift: {cagr_lift:+.1f}% | DD Red: {dd_reduction:+.1f}%",
            "Status": "PASS"
            if (
                (not np.isnan(bss) and bss >= 0.02)
                and (
                    sr_lift >= 0.05
                    or (sr_lift >= -0.05 and sortino_lift >= 0.02)
                    or (sr_lift >= -0.05 and cagr_lift >= 3.0)
                    or (sr_lift >= 0.0 and dd_reduction >= 1.5)
                )
            )
            else "FAIL",
        },
    ]

    all_pass = all(g["Status"] == "PASS" for g in gates)
    return pd.DataFrame(gates), gates, all_pass


def _format_yearly_table_df(df: pd.DataFrame) -> pd.DataFrame:
    """Format yearly breakdown table with professional Title Case headers and clean financial formats."""
    if df.empty:
        return df
    records = []
    for _, r in df.iterrows():
        yr = int(r["year"])
        tot_ret = float(r.get("total_return_pct", 0.0))
        cagr = float(r.get("cagr_pct", tot_ret))
        max_dd = float(r.get("max_dd_pct", 0.0))
        vol = float(r.get("vol_pct", r.get("vol", 0.0)))
        records.append({
            "Year": str(yr),
            "Total Return (%)": f"{tot_ret:+.2f}%",
            "CAGR (%)": f"{cagr:+.2f}%",
            "Ann. Vol (%)": f"{vol:.1f}%" if vol > 0 else "N/A",
            "Sharpe": f"{float(r.get('sharpe', 0.0)):.2f}",
            "Sortino": f"{float(r.get('sortino', 0.0)):.2f}",
            "Max Drawdown (%)": f"-{abs(max_dd):.2f}%",
            "100% Cash Days (%)": f"{float(r.get('cash_days_pct', 0.0)):.1f}%",
            "Trades": int(r.get("trades", 0)),
            "Win Rate (%)": f"{float(r.get('win_rate_pct', 0.0)):.1f}%",
            "Profit Factor": f"{float(r.get('profit_factor', 0.0)):.2f}",
            "Avg R": f"{float(r.get('avg_r', 0.0)):+.2f}R",
        })
    return pd.DataFrame(records)


def _format_trade_blotter_df(df: pd.DataFrame) -> pd.DataFrame:
    """Format closed trades log into an institutional trade blotter with zero internal database field leaks."""
    if df.empty:
        return df
    records = []
    for _, r in df.iterrows():
        ret_pct = float(r.get("return_pct", 0.0))
        net_pnl = float(r.get("net_pnl", 0.0))
        r_mult = float(r.get("r_multiple", 0.0))
        raw_reason = str(r.get("exit_reason", "")).replace("_", " ").title()
        sh = float(r.get("shares", 0.0))
        sh_str = f"{sh:,.0f}" if sh.is_integer() else f"{sh:,.1f}"
        notional = float(r.get("notional", 0.0))
        records.append({
            "Ticker": str(r.get("ticker", "")),
            "Tier": str(r.get("tier", "MEDIUM")),
            "Shares": sh_str,
            "Position ($)": f"${notional:,.2f}",
            "Entry Date": pd.to_datetime(r.get("entry_date")).strftime("%Y-%m-%d"),
            "Exit Date": pd.to_datetime(r.get("exit_date")).strftime("%Y-%m-%d"),
            "Days Held": int(r.get("days_held", 0)),
            "Entry ($)": f"${float(r.get('entry_price', 0.0)):.2f}",
            "Exit ($)": f"${float(r.get('exit_price', 0.0)):.2f}",
            "Initial Stop ($)": f"${float(r.get('initial_stop', 0.0)):.2f}",
            "Return (%)": f"{ret_pct:+.2f}%",
            "Net P&L ($)": f"{net_pnl:+,.0f}",
            "R-Multiple": f"{r_mult:+.2f}R",
            "Exit Reason": raw_reason,
            "Win Prob": f"{float(r.get('entry_prob', 0.0)) * 100:.1f}%",
            "Sizing Scalar": f"{float(r.get('size_scalar', 1.0)):.2f}x",
            "Top Model Drivers": str(r.get("shap_summary", "N/A")),
        })
    return pd.DataFrame(records)


def _decorate_html_table(html_str: str) -> str:
    """Add mouse-over tooltips to whitelisted metrics in table headers where mouse-over is on the text."""
    for col, tip in WHITELIST_METRIC_TIPS.items():
        pattern = re.compile(rf"<th>\s*{re.escape(col)}\s*</th>", re.IGNORECASE)
        html_str = pattern.sub(f"<th>{_render_metric_tooltip(col, tip)}</th>", html_str)
    return html_str


def _df_to_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data_"
    col_name_map = {
        "total_return_pct": "Total Return (%)",
        "cagr_pct": "CAGR (%)",
        "sharpe": "Sharpe",
        "deflated_sharpe_prob": "Deflated SR Prob",
        "sortino": "Sortino",
        "max_dd_pct": "Max Drawdown (%)",
        "profit_factor": "Profit Factor",
        "win_rate_pct": "Win Rate (%)",
        "avg_r": "Avg R",
        "cash_days_pct": "100% Cash Days (%)",
        "Gate": "Institutional Gate",
        "Value": "Realized Metric",
        "Status": "Gate Status",
    }
    cols = [col_name_map.get(str(c), str(c).replace("_", " ")) for c in df.columns]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    body = []
    for _, r in df.iterrows():
        row_vals = []
        for c in df.columns:
            val_str = str(r[c]).replace("|", ";").replace("Adaptive L_t", "Adaptive `L_t`")
            if ("_" in val_str or "=" in val_str) and not val_str.startswith("`"):
                val_str = f"`{val_str}`"
            row_vals.append(val_str)
        body.append("| " + " | ".join(row_vals) + " |")
    return "\n".join([header, sep] + body)


def _render_trade_legend_html() -> str:
    return """
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-left:5px solid #2563eb; border-radius:8px; padding:16px 20px; margin-bottom:20px; font-size:13px; line-height:1.55; color:#334155;">
      <div style="font-weight:700; color:#0f172a; margin-bottom:8px; font-size:14px;">Section 8 Trade Blotter Legend &amp; Quantitative Diagnostics</div>
      <div style="margin-bottom:6px;">
        <strong>Tier:</strong>
        <span style="display:inline-block; padding:1px 6px; background:#dcfce7; color:#166534; border-radius:4px; font-size:11px; font-weight:700;">CONSENSUS</span> Dual-engine alignment (both Baseline OLS trend significance t_norm &ge; 1.8 and ML classifier agree; 1.0% risk). &nbsp;
        <span style="display:inline-block; padding:1px 6px; background:#e0f2fe; color:#0369a1; border-radius:4px; font-size:11px; font-weight:700;">HIGH</span> Standalone ML qualification with top-quintile residual momentum (1.0% risk). &nbsp;
        <span style="display:inline-block; padding:1px 6px; background:#f1f5f9; color:#475569; border-radius:4px; font-size:11px; font-weight:700;">MEDIUM</span> Baseline trend qualification or secondary ML score (0.75% conservative risk). &nbsp;
        <span style="display:inline-block; padding:1px 6px; background:#fff1f2; color:#be123c; border-radius:4px; font-size:11px; font-weight:700;">LOW</span> Lower-conviction meta-labeling score (S_i,t &lt; 0.85; 0.50% risk or conservative bottom tier).
      </div>
      <div style="margin-bottom:6px;">
        <strong>Shares &amp; Position ($):</strong> Dynamically calculated via Volatility-Parity / Fixed-Fractional Risk Sizing: <code>Shares = (Portfolio Equity &times; Base Risk &times; M_t &times; S_i,t) / Stop Distance</code>. Each trade risks a fixed fraction of total portfolio equity at execution, so position dollar allocations and share counts vary according to individual stock ATR volatility, tier conviction, meta-labeling multiplier S_i,t, and compounding portfolio equity over time.
      </div>
      <div style="margin-bottom:6px;">
        <strong>Partial Profit Taking (TP1) &amp; Blended Returns:</strong> When Take Profit 1 (TP1) triggers, partial shares are sold and stop is moved to breakeven. <code>Exit ($)</code> reports the final runner share exit price, while <code>Return (%)</code> and <code>R Multiple</code> reflect the blended net performance across the entire position.
      </div>
      <div style="margin-bottom:6px;">
        <strong>Win Prob:</strong> Platt-calibrated posterior probability P(Hits +1.5R target before Hard Stop) produced out-of-fold by shallow LightGBM trees. With a 1.5:1 reward-to-risk ratio, any probability P &gt; 40.0% yields positive mathematical expectancy.
      </div>
      <div style="margin-bottom:6px;">
        <strong>Sizing Scalar:</strong> Continuous meta-labeling position sizing multiplier S_i,t &isin; [0.50, 1.50] (L&oacute;pez de Prado framework). Maps predicted win probability into historical out-of-fold percentile rank: S_i,t = 0.50 + Rank_OOF(p). Conviction scales position sizes dynamically between 0.50x and 1.50x without expanding total risk caps.
      </div>
      <div>
        <strong>Top Model Drivers (SHAP):</strong> Single-feature marginal contributions detailing model conviction:
        <ul style="margin: 6px 0 0 18px; padding: 0; line-height: 1.55;">
          <li><code>sector_rs</code>: 20-day relative strength of SMH vs SPY: Delta%20d(SMH) - Delta%20d(SPY). Positive values confirm semiconductor sector leadership.</li>
          <li><code>vix_ts</code>: Volatility term structure ratio (VIX / VIX3M). Values &lt; 1.0 confirm normal contango (calm regime); &ge; 1.0 indicates backwardation (near-term panic).</li>
          <li><code>skew_idx</code>: CBOE SKEW Index 60-day rolling z-score (min_periods=20). Elevated values (&gt; +1.5) indicate institutional tail-risk hedging and out-of-the-money put demand.</li>
          <li><code>resid_mom_60</code>: 60-day idiosyncratic residual momentum relative to SMH after stripping market beta. Confirms stock-specific momentum decoupled from sector drift.</li>
          <li><code>resid_mom_20</code>: 20-day idiosyncratic residual momentum relative to SMH after stripping market beta.</li>
          <li><code>rs_rank</code>: Cross-sectional percentile rank [0.0, 1.0] of 20-day residual momentum across the active tradeable universe.</li>
          <li><code>vol_compress</code>: Realized volatility compression ratio (RV_10d / RV_60d). Values &lt; 0.70 indicate price coiling prior to directional breakout.</li>
          <li><code>vxn_squeeze_vel</code>: 252-day rolling z-score of 5-day rate of change in Nasdaq Volatility Index (VXN). Rapid drops detect post-panic volatility compression.</li>
          <li><code>slope_r2_20d</code>: Coefficient of determination (R^2 in [0, 1]) from 20-day log-price linear regression measuring trend smoothness.</li>
          <li><code>slope_t_norm</code>: Adaptive window L_t sample-size normalized OLS t-statistic measuring directional trend conviction.</li>
          <li><code>slope_accel</code>: Multi-scale slope acceleration: (beta_10d - beta_40d) / sigma_20 normalized by 20-day return volatility.</li>
          <li><code>ema20_slope</code>: 5-day slope of 20-day exponential moving average in ATR units: (EMA20_t / EMA20_{t-5} - 1) / ATR%_14.</li>
          <li><code>ema50_slope</code>: 10-day slope of 50-day exponential moving average in ATR units: (EMA50_t / EMA50_{t-10} - 1) / ATR%_14.</li>
        </ul>
      </div>
    </div>
    """


def _render_trade_legend_md() -> str:
    return (
        "> **Section 8 Trade Blotter Legend & Quantitative Diagnostics**\n"
        "> - **Shares & Position ($):** Dynamically calculated via Volatility-Parity / Fixed-Fractional Risk Sizing: $\\text{Shares} = (\\text{Portfolio Equity} \\times \\text{Base Risk} \\times M_t \\times S_{i,t}) / \\text{Stop Distance}$. Each trade risks a fixed fraction of portfolio equity, so share counts and dollar allocations vary based on stock ATR volatility, tier conviction, meta-labeling multiplier $S_{i,t}$, and compounding portfolio equity over time.\n"
        "> - **Partial Exits (TP1) & Blended Returns:** When Take Profit 1 triggers, partial shares are sold and stop ratchets to breakeven. `Exit ($)` reports final runner exit; `Return (%)` is the blended net return.\n"
        "> - **Tier:** `CONSENSUS` (dual-engine alignment, 1.0% risk), `HIGH` (standalone ML top-quintile RS, 1.0% risk), `MEDIUM` (conservative 0.75% risk), `LOW` (lower-conviction meta-labeling score $S_{i,t} < 0.85$, 0.50% risk).\n"
        "> - **Win Prob:** Platt-calibrated out-of-fold probability $P(\\text{TP1 before Stop})$. Break-even threshold is $> 40.0\\%$ with a 1.5:1 payoff ratio.\n"
        "> - **Sizing Scalar:** Meta-labeling sizing multiplier $S_{i,t} = 0.50 + \\text{Rank}_{\\text{OOF}}(\\hat{p}) \\in [0.50, 1.50]$ scaling allocation by model confidence.\n"
        "> - **Top Model Drivers (SHAP):** Single-feature marginal attributions detailing model conviction:\n"
        ">   - `sector_rs`: 20-day relative strength of SMH vs SPY. Positive values confirm semiconductor sector leadership.\n"
        ">   - `vix_ts`: Volatility term structure ratio (VIX / VIX3M). Values $< 1.0$ confirm normal contango (calm regime); $\\ge 1.0$ indicates backwardation.\n"
        ">   - `skew_idx`: CBOE SKEW Index 60-day rolling z-score. Elevated values ($> +1.5$) indicate institutional tail-risk put demand.\n"
        ">   - `resid_mom_60`: 60-day idiosyncratic residual momentum relative to SMH after stripping market beta.\n"
        ">   - `resid_mom_20`: 20-day idiosyncratic residual momentum relative to SMH after stripping market beta.\n"
        ">   - `rs_rank`: Cross-sectional percentile rank ($[0.0, 1.0]$) of 20-day residual momentum across the universe.\n"
        ">   - `vol_compress`: Realized volatility compression ratio (RV_10d / RV_60d). Values $< 0.70$ indicate price coiling prior to breakout.\n"
        ">   - `vxn_squeeze_vel`: 252-day rolling z-score of 5-day change in Nasdaq Volatility Index (VXN).\n"
        ">   - `slope_r2_20d`: Coefficient of determination ($R^2 \\in [0, 1]$) from 20-day log-price regression measuring trend smoothness.\n"
        ">   - `slope_t_norm`: Adaptive window $L_t$ normalized OLS $t$-statistic measuring directional trend conviction.\n"
        ">   - `slope_accel`: Multi-scale slope acceleration: $(\\beta_{10d} - \\beta_{40d}) / \\sigma_{20}$.\n"
        ">   - `ema20_slope`: 5-day slope of 20-day EMA in ATR units.\n"
        ">   - `ema50_slope`: 10-day slope of 50-day EMA in ATR units."
    )


def generate_reports(
    results: Dict[str, BacktestResult],
    cal_stats: Dict[str, float],
    health_score: float,
    html_path: Path,
    md_path: Path | None = None,
) -> Tuple[Path, Path]:
    """Write both interactive HTML and Dropbox-friendly Markdown backtest reports."""
    html_path.parent.mkdir(parents=True, exist_ok=True)
    if md_path is None:
        md_path = html_path.with_suffix(".md")

    charts_dir = html_path.parent / "charts"
    chart_paths = generate_benchmark_charts(results, charts_dir=charts_dir)

    df_overall = _format_comparison_df(results, "metrics_overall")
    df_2022 = _format_comparison_df(results, "metrics_2022_bear")
    df_ai = _format_comparison_df(results, "metrics_ai_era")

    trial_k = load_trial_count_k(html_path.parent)

    ml_core_res = results.get("ML (SMH Bull Core + Swing)")
    base_core_res = results.get("Baseline (SMH Bull Core + Swing)")
    ml_cash_res = results.get("ML (LightGBM + Platt)")
    base_cash_res = results.get("Baseline (Adaptive L_t)")
    base_res = base_cash_res
    ml_res = ml_cash_res
    smh_res = results.get("SMH Buy & Hold")

    gates_core_df, gates_core_raw, core_all_pass = _build_institutional_gates(
        ml_core_res, base_core_res, smh_res, "SMH Bull Core + Swing Mode", SMH_CORE_HURDLES, cal_stats, trial_k
    )

    gates_cash_df, gates_cash_raw, cash_all_pass = _build_institutional_gates(
        ml_cash_res, base_cash_res, smh_res, "Cash Swing Mode", CASH_SWING_HURDLES, cal_stats, trial_k
    )

    best_sys = ml_core_res or ml_cash_res or base_core_res or base_cash_res
    best_name = "ML (SMH Bull Core + Swing)" if ml_core_res else "ML (LightGBM + Platt)"

    # Export machine-readable institutional audit manifest
    manifest_path = html_path.parent / "audit_manifest.json"
    manifest_data = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": compute_strategy_source_sha256(),
        "trial_count_k": trial_k,
        "all_gates_pass": bool(core_all_pass and cash_all_pass),
        "smh_core_gates_pass": bool(core_all_pass),
        "cash_swing_gates_pass": bool(cash_all_pass),
        "gates_smh_core": gates_core_raw,
        "gates_cash_swing": gates_cash_raw,
        "metrics": {
            "ml_smh_core": ml_core_res.metrics_ai_era if ml_core_res else {},
            "base_smh_core": base_core_res.metrics_ai_era if base_core_res else {},
            "ml_cash_swing": ml_cash_res.metrics_ai_era if ml_cash_res else {},
            "base_cash_swing": base_cash_res.metrics_ai_era if base_cash_res else {},
        },
        "cal_stats": cal_stats,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")



    md_lines = [
        "# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)",
        "",
        f"- **Data Health Score:** `{health_score}/100`",
        f"- **Warmup Training Period:** `2018-01-01` to `2021-12-31`",
        f"- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present",
        f"- **Platt Calibration OOF Brier Score:** Raw `{cal_stats.get('brier_raw', 'N/A')}` -> Calibrated `{cal_stats.get('brier_calibrated', 'N/A')}` (Brier Skill Score: `{cal_stats.get('brier_skill_score', 'N/A')}`)",
        "",
        "## 1. Visual Benchmark Comparison Charts (`S&P 500`, `QQQ`, `VGT`, `SMH`, `SOXX`, `AIQ`, `IGV`, `T-Bills`)",
        "",
        "### 1.1 Full Out-of-Sample Growth of `$10,000` (`2022–2026`, Includes 2022 Bear Market)",
        f"![Full OOS Equity Curve](charts/{chart_paths['equity_2022_2026'].name})",
        "",
        "### 1.2 Modern AI Cycle Growth of `$10,000` (`2023–2026`, Rebased Jan 1, 2023)",
        f"![Modern AI Cycle Equity Curve](charts/{chart_paths['equity_2023_2026_ai_era'].name})",
        "",
        "### 1.3 Underwater Drawdown Comparison (`2022–2026`)",
        f"![Underwater Drawdowns](charts/{chart_paths['drawdown_comparison'].name})",
        "",
        "### 1.4 Calendar Year Returns & Risk-Return Efficiency (`2022–2026`)",
        f"![Annual Returns and Risk-Return Scatter](charts/{chart_paths['annual_returns_and_risk_scatter'].name})",
        "",
        "## 2. Institutional Validation Gates (§9)",
        "",
        "### 2.1 SMH Bull Core + Swing Mode (Active Secular Bull Core Sweep)",
        "",
        _df_to_md(gates_core_df),
        "",
        "### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)",
        "",
        _df_to_md(gates_cash_df),
        "",
        "## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)",
        "",
        _df_to_md(df_overall),
        "",
        "## 4. View A — 2022 Bear Market Stress Test (`2022`)",
        "",
        _df_to_md(df_2022),
        "",
        "## 5. View B — Modern AI Cycle (`2023–2026`)",
        "",
        _df_to_md(df_ai),
        "",
    ]

    if base_res is not None and not base_res.yearly_table.empty:
        formatted_base_yr = _format_yearly_table_df(base_res.yearly_table)
        md_lines.extend(
            [
                "## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)",
                "",
                _df_to_md(formatted_base_yr),
                "",
            ]
        )

    if ml_res is not None and not ml_res.yearly_table.empty:
        formatted_ml_yr = _format_yearly_table_df(ml_res.yearly_table)
        md_lines.extend(
            [
                "## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)",
                "",
                _df_to_md(formatted_ml_yr),
                "",
            ]
        )

    if best_sys is not None and not best_sys.trades.empty:
        recent_tr = best_sys.trades.tail(25)
        formatted_tr = _format_trade_blotter_df(recent_tr)
        md_lines.extend(
            [
                f"## 8. Recent 25 OOS Trades ({best_name})",
                "",
                _render_trade_legend_md(),
                "",
                _df_to_md(formatted_tr),
                "",
            ]
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # Build self-contained styled HTML report with 100% Dynamic Interactive Charts
    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 28px; color: #1f2937; background: #f1f5f9; max-width: 1480px; margin-left: auto; margin-right: auto; }
    h1, h2, h3 { color: #0f172a; }
    .meta { background: #ffffff; padding: 16px 20px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
    .interactive-panel { background: #e2e8f0; padding: 22px; border-radius: 12px; margin-bottom: 32px; border: 1px solid #cbd5e1; }
    .panel-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
    .mode-toggles { background: #ffffff; padding: 8px 14px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-size: 13px; font-weight: 600; display: flex; gap: 12px; align-items: center; }
    .toggle-lbl { cursor: pointer; display: flex; align-items: center; gap: 5px; }
    .date-controls-card, .funds-card { background: #ffffff; padding: 16px 18px; border-radius: 10px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .preset-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 14px; }
    .control-title { font-weight: 700; font-size: 13.5px; color: #1e293b; margin-right: 6px; }
    .btn-preset { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 11px; font-size: 12.5px; font-weight: 600; color: #1e293b; cursor: pointer; transition: all 0.15s; }
    .btn-preset:hover { background: #2563eb; color: #ffffff; border-color: #2563eb; }
    .btn-mini { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px; padding: 4px 9px; font-size: 12px; font-weight: 600; color: #334155; cursor: pointer; margin-left: 4px; }
    .btn-mini:hover { background: #0f172a; color: #ffffff; }
    .dual-slider-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; font-size: 13.5px; }
    .dual-slider-header input[type="date"] { padding: 4px 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; font-weight: 600; color: #0f172a; }
    .idx-badge { font-size: 12.5px; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 999px; font-weight: 700; }
    .dual-slider-wrap { position: relative; width: 100%; height: 28px; display: flex; align-items: center; margin-top: 4px; }
    .dual-slider-track { position: absolute; left: 0; right: 0; height: 8px; border-radius: 999px; background: #cbd5e1; z-index: 1; }
    .dual-slider-fill { position: absolute; height: 8px; border-radius: 999px; background: #2563eb; z-index: 2; }
    .dual-range-input { position: absolute; left: 0; width: 100%; height: 8px; margin: 0; background: transparent; pointer-events: none; -webkit-appearance: none; appearance: none; z-index: 3; }
    .dual-range-input::-webkit-slider-thumb { pointer-events: auto; -webkit-appearance: none; appearance: none; width: 22px; height: 22px; border-radius: 50%; background: #2563eb; border: 2.5px solid #ffffff; box-shadow: 0 1px 5px rgba(15,23,42,0.35); cursor: grab; transition: transform 0.1s; }
    .dual-range-input::-webkit-slider-thumb:hover { transform: scale(1.12); background: #1d4ed8; }
    .dual-range-input::-moz-range-thumb { pointer-events: auto; width: 22px; height: 22px; border-radius: 50%; background: #2563eb; border: 2.5px solid #ffffff; box-shadow: 0 1px 5px rgba(15,23,42,0.35); cursor: grab; }
    .dual-slider-ticks { position: relative; width: 100%; height: 18px; font-size: 11.5px; font-weight: 600; color: #64748b; margin-top: 4px; }
    .year-tick-mark { position: absolute; transform: translateX(-50%); white-space: nowrap; }
    .year-tick-mark:first-child { transform: translateX(0%); }
    .funds-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
    .pills-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
    .fund-pill { display: inline-flex; align-items: center; gap: 6px; padding: 6px 11px; border-radius: 999px; border: 1.5px solid #cbd5e1; background: #f8fafc; font-size: 12.5px; font-weight: 500; cursor: pointer; opacity: 0.55; transition: all 0.15s; user-select: none; }
    .fund-pill input { display: none; }
    .fund-pill.active { opacity: 1.0; background: #ffffff; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .color-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .two-col-charts { display: grid; grid-template-columns: 1.15fr 1fr; gap: 18px; }
    @media (max-width: 1100px) { .two-col-charts { grid-template-columns: 1fr; } }
    .chart-card { background: #ffffff; padding: 18px; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); overflow: visible; }
    table { border-collapse: separate; border-spacing: 0; width: 100%; background: #ffffff; margin-bottom: 28px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); font-size: 13.5px; }
    table tr:first-child th:first-child { border-top-left-radius: 8px; }
    table tr:first-child th:last-child { border-top-right-radius: 8px; }
    th { background: #1e293b; color: #ffffff; text-align: left; padding: 10px 12px; font-weight: 600; position: relative; }
    td { padding: 9px 12px; border-bottom: 1px solid #e5e7eb; }
    tr:nth-child(even) { background: #f8fafc; }
    
    /* Text-Based Hover Tooltip Component */
    .metric-tip {
      position: relative;
      display: inline-flex;
      align-items: baseline;
      white-space: nowrap;
      cursor: help;
      border-bottom: 1px dotted rgba(100, 116, 139, 0.6);
      transition: color 0.15s ease, border-bottom-color 0.15s ease;
    }
    .metric-tip:hover {
      color: #0284c7;
      border-bottom-color: #0284c7;
    }
    .metric-tip-sup {
      font-size: 0.68em;
      line-height: 0;
      vertical-align: super;
      margin-left: 2.5px;
      color: #0f172a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-style: normal;
      font-weight: 800;
      opacity: 0.95;
      user-select: none;
      transition: color 0.15s ease, transform 0.15s ease;
    }
    th .metric-tip-sup {
      color: #38bdf8 !important;
      opacity: 1 !important;
    }
    .metric-tip:hover .metric-tip-sup {
      color: #0284c7;
      opacity: 1;
      transform: translateY(-1px);
    }
    .metric-tip-popup {
      visibility: hidden;
      opacity: 0;
      position: absolute;
      bottom: calc(100% + 7px);
      left: 50%;
      transform: translateX(-50%) translateY(4px);
      width: max-content;
      max-width: 270px;
      min-width: 150px;
      padding: 8px 12px;
      background-color: #0f172a;
      color: #f8fafc;
      font-size: 11.5px;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      text-transform: none;
      letter-spacing: normal;
      white-space: normal;
      border-radius: 6px;
      border: 1px solid #334155;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
      z-index: 10000;
      pointer-events: none;
      transition: opacity 0.18s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.18s cubic-bezier(0.16, 1, 0.3, 1),
                  visibility 0.18s;
    }
    .metric-tip-popup::after {
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border-width: 5px 5px 0 5px;
      border-style: solid;
      border-color: #0f172a transparent transparent transparent;
    }
    .metric-tip:hover .metric-tip-popup {
      visibility: visible;
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
    .metric-tip.tip-left .metric-tip-popup { left: 0; transform: translateX(0) translateY(4px); }
    .metric-tip.tip-left:hover .metric-tip-popup { transform: translateX(0) translateY(0); }
    .metric-tip.tip-left .metric-tip-popup::after { left: 14px; transform: none; }
    .metric-tip.tip-right .metric-tip-popup { left: auto; right: 0; transform: translateX(0) translateY(4px); }
    .metric-tip.tip-right:hover .metric-tip-popup { transform: translateX(0) translateY(0); }
    .metric-tip.tip-right .metric-tip-popup::after { left: auto; right: 14px; transform: none; }

    /* Table Header Specific: Pop downward so popups are never clipped by table tops */
    th .metric-tip-popup {
      bottom: auto;
      top: calc(100% + 7px);
      transform: translateX(-50%) translateY(-4px);
    }
    th .metric-tip:hover .metric-tip-popup {
      transform: translateX(-50%) translateY(0);
    }
    th .metric-tip-popup::after {
      top: auto;
      bottom: 100%;
      border-width: 0 5px 5px 5px;
      border-color: transparent transparent #0f172a transparent;
    }
    th .metric-tip.tip-left .metric-tip-popup { left: 0; transform: translateX(0) translateY(-4px); }
    th .metric-tip.tip-left:hover .metric-tip-popup { transform: translateX(0) translateY(0); }
    th .metric-tip.tip-left .metric-tip-popup::after { left: 14px; transform: none; }
    th .metric-tip.tip-right .metric-tip-popup { left: auto; right: 0; transform: translateX(0) translateY(-4px); }
    th .metric-tip.tip-right:hover .metric-tip-popup { transform: translateX(0) translateY(0); }
    th .metric-tip.tip-right .metric-tip-popup::after { left: auto; right: 14px; transform: none; }
    """

    interactive_html = _build_interactive_dashboard_html(results)

    html_parts = [
        f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>SemiSwing Interactive Backtest Report</title><style>{css}</style></head><body>",
        "<h1>SemiSwing Walk-Forward Backtest &amp; Interactive Benchmark Report (2022–2026)</h1>",
        f"<div class='meta'><b>Data Health Score:</b> {health_score}/100 &nbsp;|&nbsp; "
        f"<b>Initial Training Warmup:</b> 2018–2021 &nbsp;|&nbsp; "
        f"<b>Platt OOF Brier:</b> {cal_stats.get('brier_raw', 'N/A')} &rarr; {cal_stats.get('brier_calibrated', 'N/A')} &nbsp;|&nbsp; "
        f"<b>Brier Skill Score:</b> {cal_stats.get('brier_skill_score', 'N/A')}</div>",
        interactive_html,
        "<h2>2. Institutional Validation Gates (§9)</h2>",
        "<h3>2.1 SMH Bull Core + Swing Mode (Active Secular Bull Core Sweep)</h3>",
        _decorate_html_table(gates_core_df.to_html(index=False, border=0)),
        "<h3>2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)</h3>",
        _decorate_html_table(gates_cash_df.to_html(index=False, border=0)),
        "<h2>3. Full Out-of-Sample Walk-Forward Table (2022–2026)</h2>",
        _decorate_html_table(df_overall.to_html(index=False, border=0)),
        "<h2>4. View A — 2022 Bear Market Stress Test (2022)</h2>",
        _decorate_html_table(df_2022.to_html(index=False, border=0)),
        "<h2>5. View B — Modern AI Cycle (2023–2026)</h2>",
        _decorate_html_table(df_ai.to_html(index=False, border=0)),
    ]

    if base_res is not None and not base_res.yearly_table.empty:
        html_parts.append("<h2>6. Yearly Breakdown — Baseline (Adaptive L_t)</h2>")
        formatted_base_yr = _format_yearly_table_df(base_res.yearly_table)
        html_parts.append(_decorate_html_table(formatted_base_yr.to_html(index=False, border=0)))

    if ml_res is not None and not ml_res.yearly_table.empty:
        html_parts.append("<h2>7. Yearly Breakdown — ML (LightGBM + Platt Calibration)</h2>")
        formatted_ml_yr = _format_yearly_table_df(ml_res.yearly_table)
        html_parts.append(_decorate_html_table(formatted_ml_yr.to_html(index=False, border=0)))

    if best_sys is not None and not best_sys.trades.empty:
        recent_tr = best_sys.trades.tail(25)
        formatted_tr = _format_trade_blotter_df(recent_tr)
        html_parts.append(f"<h2>8. Recent 25 OOS Trades ({best_name})</h2>")
        html_parts.append(_render_trade_legend_html())
        html_parts.append(_decorate_html_table(formatted_tr.to_html(index=False, border=0)))

    now_ts = pd.Timestamp.now(tz="America/New_York").strftime("%Y-%m-%d %H:%M:%S %Z")
    html_parts.append(
        f"<footer style='margin-top:50px; padding:24px 0 32px 0; border-top:1px solid #cbd5e1; text-align:center; font-size:12px; color:#64748b; font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;'>"
        f"SemiSwing Systematic Trading Engine &bull; Report Created: <strong>{now_ts}</strong>"
        f"</footer>"
    )
    html_parts.append("</body></html>")
    html_path.write_text("\n".join(html_parts), encoding="utf-8")

    return html_path, md_path


def write_recent_trades_and_open_positions_report(
    best_sys: BacktestResult,
    panel: pd.DataFrame,
    out_path: Path | None = None,
) -> Path:
    """Generate a standalone public HTML report for Active Open Positions (MTM) and Recent 25 Closed Trades."""
    target_path = out_path or (PROJECT_ROOT / "reports" / "backtests" / "recent_trades_and_open_positions.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    now_ts = pd.Timestamp.now(tz="America/New_York").strftime("%Y-%m-%d %H:%M:%S %Z")
    latest_panel_prices = {}
    if panel is not None and not panel.empty:
        latest_panel_prices = panel.groupby("ticker")["close"].last().to_dict()

    open_rows = []
    tot_invested = 0.0
    tot_unrealized_pnl = 0.0
    tot_cost = 0.0

    if hasattr(best_sys, "open_positions") and best_sys.open_positions:
        for ticker, pos in best_sys.open_positions.items():
            last_close = latest_panel_prices.get(ticker, pos.last_valid_close or pos.entry_price)
            pos_val = pos.shares * last_close
            cost = pos.shares * pos.entry_price
            unrealized_pnl = (last_close - pos.entry_price) * pos.shares
            unrealized_ret = (last_close / pos.entry_price - 1.0) * 100.0 if pos.entry_price > 0 else 0.0
            stop_dist_pct = (last_close - pos.current_stop) / last_close * 100.0 if last_close > 0 else 0.0
            entry_dt_str = str(pos.entry_date)[:10]

            tot_invested += pos_val
            tot_cost += cost
            tot_unrealized_pnl += unrealized_pnl

            open_rows.append({
                "Ticker": ticker,
                "Tier": pos.tier,
                "Shares": f"{pos.shares:.1f}",
                "Entry Date": entry_dt_str,
                "Days Held": pos.days_held,
                "Entry ($)": f"${pos.entry_price:,.2f}",
                "Current Stop ($)": f"${pos.current_stop:,.2f}",
                "Latest Close ($)": f"${last_close:,.2f}",
                "Position Value ($)": f"${pos_val:,.2f}",
                "Unrealized P&L ($)": f"{unrealized_pnl:+,.2f}",
                "Unrealized Ret (%)": f"{unrealized_ret:+.2f}%",
                "Stop Distance (%)": f"{stop_dist_pct:+.2f}%",
                "Top Model Drivers": pos.shap_summary or "N/A",
            })

    open_df = pd.DataFrame(open_rows)

    recent_tr = best_sys.trades.tail(25) if (best_sys is not None and not best_sys.trades.empty) else pd.DataFrame()
    formatted_tr = _format_trade_blotter_df(recent_tr) if not recent_tr.empty else pd.DataFrame()

    tot_unrealized_ret = (tot_unrealized_pnl / tot_cost * 100.0) if tot_cost > 0 else 0.0
    pnl_color = "#16a34a" if tot_unrealized_pnl >= 0 else "#dc2626"

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>SemiSwing: Active Open Positions &amp; Recent Closed Trades</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #f1f5f9; color: #1e293b; line-height: 1.5; }",
        ".container { max-width: 1280px; margin: 0 auto; background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }",
        "h1 { margin-top: 0; font-size: 26px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }",
        "h2 { font-size: 19px; color: #1e293b; margin-top: 28px; margin-bottom: 12px; border-left: 4px solid #0284c7; padding-left: 10px; }",
        ".header-meta { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; font-size: 13px; color: #64748b; }",
        ".meta-badge { background: #f8fafc; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; }",
        ".cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }",
        ".metric-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }",
        ".metric-card .title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }",
        ".metric-card .val { font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 4px; }",
        "table { width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 24px; font-size: 13px; border: 1px solid #e2e8f0; }",
        "th { background: #1e293b; color: #ffffff; text-align: left; padding: 10px 12px; font-weight: 600; white-space: nowrap; }",
        "td { padding: 9px 12px; border-bottom: 1px solid #e2e8f0; }",
        "tr:nth-child(even) { background: #f8fafc; }",
        ".badge-open { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: 11px; }",
        ".badge-public { background: #052e16; color: #4ade80; border: 1px solid #16a34a; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; }",
        "footer { margin-top: 48px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #64748b; }",
        "</style></head><body>",
        "<div class='container'>",
        "<div style='display:flex; justify-content:space-between; align-items:center;'>",
        "  <div><div style='font-size:12px; font-weight:700; color:#0284c7; text-transform:uppercase; letter-spacing:1px;'>SemiSwing Quantitative Desk</div>",
        "  <h1>Active Open Positions &amp; Recent 25 Closed Trades</h1></div>",
        "  <span class='badge-public'>PUBLIC AUDIT</span>",
        "</div>",
        "<div class='header-meta'>",
        f"  <div class='meta-badge'>Strategy Mode: <strong>{best_sys.name}</strong></div>",
        f"  <div class='meta-badge'>Active Open Count: <strong>{len(open_rows)}</strong></div>",
        f"  <div class='meta-badge'>Report Created: <strong>{now_ts}</strong></div>",
        "</div>",
        "<div class='cards-grid'>",
        f"  <div class='metric-card'><div class='title'>Active Open Trades</div><div class='val'>{len(open_rows)}</div></div>",
        f"  <div class='metric-card'><div class='title'>Total Invested Capital</div><div class='val'>${tot_invested:,.2f}</div></div>",
        f"  <div class='metric-card'><div class='title'>Temporary Unrealized P&amp;L</div><div class='val' style='color:{pnl_color};'>{tot_unrealized_pnl:+,.2f} ({tot_unrealized_ret:+.2f}%)</div></div>",
        f"  <div class='metric-card'><div class='title'>Total Closed Trades (OOS)</div><div class='val'>{len(best_sys.trades) if best_sys is not None else 0}</div></div>",
        "</div>",
        "<h2>1. Active Open Positions (Daily Mark-to-Market)</h2>",
    ]

    if not open_df.empty:
        html_parts.append(_decorate_html_table(open_df.to_html(index=False, border=0)))
    else:
        html_parts.append(
            "<div style='background:#f8fafc; border:1px solid #cbd5e1; border-left:4px solid #0284c7; padding:16px; border-radius:6px; color:#475569; margin:16px 0;'>"
            "<strong>No Open Swing Positions Active:</strong> All prior trades have reached their natural exits (Stop Loss, TP1, or Time Stop). Portfolio capital is currently parked in 100% Cash / 3-Month T-Bills."
            "</div>"
        )

    html_parts.append(f"<h2>2. Recent 25 Out-of-Sample Closed Trades ({best_sys.name})</h2>")
    html_parts.append(_render_trade_legend_html())
    if not formatted_tr.empty:
        html_parts.append(_decorate_html_table(formatted_tr.to_html(index=False, border=0)))
    else:
        html_parts.append("<p>No closed trades recorded.</p>")

    html_parts.append(
        f"<footer>SemiSwing Systematic Trading Engine &bull; Report Created: <strong>{now_ts}</strong></footer>"
        "</div></body></html>"
    )

    target_path.write_text("\n".join(html_parts), encoding="utf-8")
    return target_path
