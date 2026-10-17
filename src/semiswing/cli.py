"""Command-line interface for SemiSwing."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from semiswing.alerts.sender import send_html_email, send_macos_sms, send_ntfy_push
from semiswing.backtest.engine import CORE_PRE2022_SEMI_TICKERS, run_portfolio_backtest
from semiswing.backtest.report import (
    compute_benchmark_result,
    compute_cash_tbill_benchmark,
    generate_reports,
)
from semiswing.config import (
    PROJECT_ROOT,
    export_private_portfolios_json,
    load_all_portfolio_settings,
    load_events_settings,
    load_portfolio_settings,
    load_strategy_settings,
    load_universe_settings,
)
from semiswing.data.store import ingest_all, load_stored_data
from semiswing.features.build import build_feature_panel
from semiswing.labels.triple_barrier import compute_triple_barrier_labels
from semiswing.models.signal_models import (
    evaluate_baseline_signals,
    run_walkforward_ml_predictions,
)
from semiswing.recommend.engine import (
    build_daily_recommendation_plan,
    render_recommendation_email_html,
    render_recommendation_email_text,
    write_recommendation_reports,
)

app = typer.Typer(help="SemiSwing: Semiconductor & AI 2-4 Week Momentum Swing System")
console = Console()


@app.command()
def ingest(
    since: str = typer.Option("2018-01-01", help="Start date for historical data (YYYY-MM-DD)"),
) -> None:
    """Ingest daily OHLCV, FRED macro series, and earnings dates, and run cross-source validation."""
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    console.print(f"[bold cyan]Ingesting SemiSwing universe since {since} (with 1y warmup)...[/bold cyan]")
    stats = ingest_all(strategy, universe, start_date=since)

    tbl = Table(title="Data Ingestion & Health Summary")
    tbl.add_column("Metric", style="bold")
    tbl.add_column("Value")
    for k, v in stats.items():
        tbl.add_row(str(k), str(v))
    console.print(tbl)


@app.command()
def backtest(
    report: str = typer.Option(
        "reports/backtests/backtest_report.html",
        help="Output path for HTML backtest report (Markdown report written alongside)",
    ),
) -> None:
    """Run full 2022-2026 Walk-Forward Backtest (Baseline Adaptive vs Fixed 20d vs LightGBM+Platt vs Benchmarks)."""
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()

    db_file = PROJECT_ROOT / "data" / "semiswing.duckdb"
    if not db_file.exists():
        console.print("[yellow]No local DuckDB found; running initial data ingestion first...[/yellow]")
        ingest_all(strategy, universe, start_date=strategy.backtest.start_date)

    bars, fred, earnings, health_score = load_stored_data()
    console.print(f"[bold cyan]Building causal feature panel ({bars['ticker'].nunique()} tickers)...[/bold cyan]")
    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)

    console.print("[bold cyan]Evaluating Baseline (Adaptive L_t) & Fixed-20d Strategies...[/bold cyan]")
    panel_adap = evaluate_baseline_signals(panel, strategy, use_fixed_20d=False, health_score=health_score)
    panel_fix20 = evaluate_baseline_signals(panel, strategy, use_fixed_20d=True, health_score=health_score)
    panel_pure_semi = evaluate_baseline_signals(
        panel,
        strategy,
        use_fixed_20d=False,
        health_score=health_score,
        allowed_tickers=CORE_PRE2022_SEMI_TICKERS,
    )

    console.print("[bold cyan]Running Walk-Forward LightGBM + Platt Calibration (2022-2026 OOS)...[/bold cyan]")
    panel_ml, _, cal_stats = run_walkforward_ml_predictions(panel_adap, strategy, health_score=health_score)

    res_base_adap = run_portfolio_backtest(panel_adap, strategy, mode="baseline", bull_core_smh=False)
    res_ml = run_portfolio_backtest(panel_ml, strategy, mode="ml", bull_core_smh=False)
    res_base_core = run_portfolio_backtest(panel_adap, strategy, mode="baseline", bull_core_smh=True)
    res_ml_core = run_portfolio_backtest(panel_ml, strategy, mode="ml", bull_core_smh=True)
    res_pure_semi_core = run_portfolio_backtest(
        panel_pure_semi,
        strategy,
        mode="baseline",
        bull_core_smh=True,
        allowed_tickers=CORE_PRE2022_SEMI_TICKERS,
    )
    res_pure_semi_cash = run_portfolio_backtest(
        panel_pure_semi,
        strategy,
        mode="baseline",
        bull_core_smh=False,
        allowed_tickers=CORE_PRE2022_SEMI_TICKERS,
    )
    res_base_fix20 = run_portfolio_backtest(panel_fix20, strategy, mode="baseline", bull_core_smh=False)

    res_smh = compute_benchmark_result(panel_adap, strategy, ticker="SMH", label="SMH Buy & Hold")
    res_soxx = compute_benchmark_result(panel_adap, strategy, ticker="SOXX", label="SOXX Buy & Hold")
    res_vgt = compute_benchmark_result(panel_adap, strategy, ticker="VGT", label="VGT Buy & Hold")
    res_qqq = compute_benchmark_result(panel_adap, strategy, ticker="QQQ", label="QQQ Buy & Hold")
    res_aiq = compute_benchmark_result(panel_adap, strategy, ticker="AIQ", label="AIQ Buy & Hold")
    res_igv = compute_benchmark_result(panel_adap, strategy, ticker="IGV", label="IGV Buy & Hold")
    res_spy = compute_benchmark_result(panel_adap, strategy, ticker="SPY", label="S&P 500 (SPY) Buy & Hold")
    res_cash = compute_cash_tbill_benchmark(panel_adap, strategy)

    results = {
        "Baseline (SMH Bull Core + Swing)": res_base_core,
        "ML (SMH Bull Core + Swing)": res_ml_core,
        "Pure Pre-2022 Semi (SMH Bull Core + Swing)": res_pure_semi_core,
        "Baseline (Adaptive L_t)": res_base_adap,
        "ML (LightGBM + Platt)": res_ml,
        "Pure Pre-2022 Semi (Cash Swing)": res_pure_semi_cash,
        "Baseline (Fixed 20d)": res_base_fix20,
        "SMH Buy & Hold": res_smh,
        "SOXX Buy & Hold": res_soxx,
        "VGT Buy & Hold": res_vgt,
        "QQQ Buy & Hold": res_qqq,
        "AIQ Buy & Hold": res_aiq,
        "IGV Buy & Hold": res_igv,
        "S&P 500 (SPY) Buy & Hold": res_spy,
        "3M T-Bill Cash (DTB3)": res_cash,
    }

    html_path = PROJECT_ROOT / report
    html_out, md_out = generate_reports(results, cal_stats, health_score, html_path)

    for title, attr in [
        ("Full Out-of-Sample Walk-Forward (2022-2026)", "metrics_overall"),
        ("View A: 2022 Bear Market Stress Test (2022)", "metrics_2022_bear"),
        ("View B: Modern AI Cycle (2023-2026)", "metrics_ai_era"),
    ]:
        tbl = Table(title=title)
        for col in [
            "Strategy",
            "Return %",
            "CAGR %",
            "Sharpe",
            "Sortino",
            "Max DD %",
            "Cash Days %",
            "Trades",
            "Win Rate %",
            "Profit Factor",
            "Avg R",
        ]:
            tbl.add_column(col)
        for name, res in results.items():
            m = getattr(res, attr)
            tbl.add_row(
                name,
                f"{m['total_return_pct']:.1f}%",
                f"{m['cagr_pct']:.1f}%",
                f"{m['sharpe']:.2f}",
                f"{m['sortino']:.2f}",
                f"{m['max_dd_pct']:.1f}%",
                f"{m['cash_days_pct']:.1f}%",
                str(m["trades"]),
                f"{m['win_rate_pct']:.1f}%",
                f"{m['profit_factor']:.2f}",
                f"{m['avg_r']:.2f}R",
            )
        console.print(tbl)

    console.print(f"[bold green]HTML Report written to:[/bold green] {html_out}")
    console.print(f"[bold green]Markdown Report written to:[/bold green] {md_out}")


@app.command()
def scan() -> None:
    """Evaluate latest trading bar across all tradeable stocks & ETFs and display current signal status."""
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()

    bars, fred, earnings, health_score = load_stored_data()
    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)
    panel = evaluate_baseline_signals(panel, strategy, use_fixed_20d=False, health_score=health_score)
    panel, _, _ = run_walkforward_ml_predictions(panel, strategy, health_score=health_score)

    latest_date = panel["date"].max()
    latest = panel[(panel["date"] == latest_date) & (panel["is_tradeable_universe"] == 1)].sort_values(
        "slope_t_norm", ascending=False
    )

    regime_state = "ON" if int(latest["regime_on"].iloc[0]) == 1 else "OFF (100% CASH)"
    console.print(
        f"[bold]Latest Date:[/bold] {latest_date.strftime('%Y-%m-%d')} | "
        f"[bold]Regime:[/bold] {regime_state} | [bold]Data Health:[/bold] {health_score}/100"
    )

    tbl = Table(title=f"SemiSwing Universe Snapshot ({latest_date.strftime('%Y-%m-%d')})")
    for col in [
        "Ticker",
        "Close",
        "L_t",
        "slope_t_norm",
        "slope_r2",
        "ema20_slope",
        "rs_rank",
        "ext_atr",
        "ML Prob",
        "Baseline Sig",
        "ML Sig",
    ]:
        tbl.add_column(col)

    for _, row in latest.iterrows():
        tbl.add_row(
            str(row["ticker"]),
            f"${row['close']:.2f}",
            str(int(row["L_t"])) if pd.notna(row["L_t"]) else "-",
            f"{row['slope_t_norm']:.2f}",
            f"{row['slope_r2']:.2f}",
            f"{row['ema20_slope']:.2f}",
            f"{row['rs_rank']:.2f}",
            f"{row['ext_atr']:.2f}",
            f"{row['ml_prob']:.2f}",
            "YES" if int(row["baseline_signal"]) == 1 else "-",
            str(row["ml_tier"]) if int(row["ml_signal"]) == 1 else "-",
        )
    console.print(tbl)


@app.command()
def recommend(
    refresh: bool = typer.Option(False, "--refresh/--no-refresh", help="Refresh market data from yfinance/FRED before running"),
    capital: float = typer.Option(0.0, help="Optional stateless capital override (0 uses portfolio configs)"),
    email: bool = typer.Option(False, "--email/--no-email", help="Send the HTML Trade Ticket email via SMTP (.env credentials)"),
    to: str = typer.Option("", "--to", help="Optional recipient email override (defaults to ALERT_EMAIL or SMTP_USER in .env)"),
) -> None:
    """Generate today's Multi-Portfolio Action Plan & Passcode-Encrypted HTML Trade Tickets."""
    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    all_portfolios = load_all_portfolio_settings()

    db_file = PROJECT_ROOT / "data" / "semiswing.duckdb"
    if refresh or not db_file.exists():
        console.print("[bold cyan]Refreshing market & macro data...[/bold cyan]")
        ingest_all(strategy, universe, start_date=strategy.backtest.start_date)

    bars, fred, earnings, health_score = load_stored_data()
    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)
    panel = evaluate_baseline_signals(panel, strategy, use_fixed_20d=False, health_score=health_score)
    panel, _, _ = run_walkforward_ml_predictions(panel, strategy, health_score=health_score)

    cap_override = capital if capital > 0 else None
    all_plans = {}
    for slug, pcfg in all_portfolios.items():
        all_plans[slug] = build_daily_recommendation_plan(
            panel=panel,
            strategy=strategy,
            universe=universe,
            portfolio=pcfg,
            health_score=health_score,
            capital_override=cap_override,
        )

    primary_plan = next(iter(all_plans.values()))
    html_out, md_out = write_recommendation_reports(primary_plan, all_plans=all_plans)
    idx_out = _write_cloudflare_pages_index(primary_plan.as_of_date, primary_plan.regime_on, len(all_plans))

    for slug, plan in all_plans.items():
        console.print(f"\n[bold cyan]=== PORTFOLIO: {slug} ===[/bold cyan]")
        console.print(render_recommendation_email_text(plan))

    console.print(f"\n[bold green]Encrypted Multi-Portfolio HTML Trade Ticket written to:[/bold green] {html_out}")
    console.print(f"[bold green]Local Plain-Text / Markdown Ticket written to:[/bold green] {md_out}")
    console.print(f"[bold green]Cloudflare Pages Dashboard Index updated:[/bold green] {idx_out}")

    if email:
        subj = f"SemiSwing Daily Trade Ticket ({primary_plan.as_of_date}) — {'RISK-ON' if primary_plan.regime_on else 'DEFENSIVE'}"
        ok = send_html_email(
            subject=subj,
            html_body=render_recommendation_email_html(primary_plan),
            text_body=render_recommendation_email_text(primary_plan),
            recipient=to or None,
        )
        if ok:
            console.print("[bold green]HTML Trade Ticket Email sent![/bold green]")
        else:
            console.print(
                "[bold yellow]HTML Email skipped/failed — check .env or GitHub Secrets (see data/alerts.log).[/bold yellow]"
            )


def _is_us_market_open_day(dt: pd.Timestamp | None = None) -> tuple[bool, str]:
    """Check whether `dt` (defaults to today in US/Eastern) is an open NYSE trading day."""
    from datetime import date, timedelta

    now_et = pd.Timestamp.now(tz="America/New_York") if dt is None else pd.Timestamp(dt)
    d = now_et.date()
    if d.weekday() >= 5:
        return False, f"Weekend ({d.strftime('%A')})"

    y = d.year

    def _observe(fixed: date) -> date:
        if fixed.weekday() == 5:  # Saturday -> Friday
            return fixed - timedelta(days=1)
        if fixed.weekday() == 6:  # Sunday -> Monday
            return fixed + timedelta(days=1)
        return fixed

    def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
        first = date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + timedelta(days=offset + 7 * (n - 1))

    def _last_monday(year: int, month: int) -> date:
        nxt = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
        last_day = nxt - timedelta(days=1)
        offset = (last_day.weekday() - 0) % 7
        return last_day - timedelta(days=offset)

    # Computus (Easter Sunday) -> Good Friday
    a = y % 19
    b = y // 100
    c = y % 100
    dd = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - dd - g + 15) % 30
    i = c // 4
    k = c % 4
    l_val = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_val) // 451
    month = (h + l_val - 7 * m + 114) // 31
    day = ((h + l_val - 7 * m + 114) % 31) + 1
    good_friday = date(y, month, day) - timedelta(days=2)

    holidays = {
        _observe(date(y, 1, 1)): "New Year's Day",
        _nth_weekday(y, 1, 0, 3): "MLK Jr. Day",
        _nth_weekday(y, 2, 0, 3): "Presidents' Day",
        good_friday: "Good Friday",
        _last_monday(y, 5): "Memorial Day",
        _observe(date(y, 6, 19)): "Juneteenth",
        _observe(date(y, 7, 4)): "Independence Day",
        _nth_weekday(y, 9, 0, 1): "Labor Day",
        _nth_weekday(y, 11, 3, 4): "Thanksgiving Day",
        _observe(date(y, 12, 25)): "Christmas Day",
    }
    if d in holidays:
        return False, f"NYSE Holiday ({holidays[d]})"
    return True, "NYSE Market Open Day"


def _write_cloudflare_pages_index(as_of_date: str, regime_on: bool, num_portfolios: int = 2) -> Path:
    """Write a clean root `reports/index.html` dashboard hub for Cloudflare Pages (without exposing raw balances)."""
    idx_path = PROJECT_ROOT / "reports" / "index.html"
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    regime_badge = "RISK-ON (Swing Entries Enabled)" if regime_on else "DEFENSIVE (Hold Core / Cash)"
    regime_color = "#22c55e" if regime_on else "#eab308"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SemiSwing Cloud Dashboard ({as_of_date})</title>
</head>
<body style="margin:0; padding:32px 16px; background:#0f172a; color:#f8fafc; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="max-width:680px; margin:0 auto;">
    <div style="font-size:12px; text-transform:uppercase; letter-spacing:1px; color:#38bdf8; font-weight:700;">
      SemiSwing Automated Cloud Desk
    </div>
    <h1 style="margin:6px 0 8px 0; font-size:26px;">AI &amp; Semiconductor Swing Dashboard</h1>
    <p style="color:#94a3b8; font-size:14px; margin-top:0;">
      Latest Bar: <strong>{as_of_date}</strong> &bull;
      Regime: <strong style="color:{regime_color};">{regime_badge}</strong> &bull;
      Portfolios: <strong>Passcode Protected ({num_portfolios} Snapshots)</strong>
    </p>

    <div style="display:grid; gap:16px; margin-top:24px;">
      <a href="daily/latest_recommendations.html" style="display:block; text-decoration:none; background:#1e293b; border:1px solid #334155; border-left:5px solid #38bdf8; border-radius:10px; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div style="font-size:18px; font-weight:800; color:#f8fafc;">1. Today's Daily Trade Tickets (Passcode Locked) &rarr;</div>
          <span style="background:#0f172a; color:#38bdf8; border:1px solid #0284c7; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700;">PROTECTED</span>
        </div>
        <div style="font-size:13px; color:#94a3b8; margin-top:6px;">
          Requires passcode to decrypt. View Step 1 (Holdings SELL / HOLD actions) and Step 2 (Exact $ Buy Tickets, Stop-Loss, TP1, and SHAP drivers) across all portfolio snapshots.
        </div>
      </a>

      <a href="backtests/backtest_report.html" style="display:block; text-decoration:none; background:#1e293b; border:1px solid #334155; border-left:5px solid #4ade80; border-radius:10px; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div style="font-size:18px; font-weight:800; color:#f8fafc;">2. Walk-Forward Backtest Report &amp; Equity Curves ($10K) &rarr;</div>
          <span style="background:#052e16; color:#4ade80; border:1px solid #16a34a; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700;">PUBLIC</span>
        </div>
        <div style="font-size:13px; color:#94a3b8; margin-top:6px;">
          Public $10,000 out-of-sample walk-forward evaluation (2022&ndash;Present): compares Adaptive Baseline, LightGBM + Platt, SMH Bull Core + Swing, QQQ, and SPY.
        </div>
      </a>
    </div>
  </div>
</body>
</html>
"""
    idx_path.write_text(html, encoding="utf-8")
    return idx_path


@app.command("daily-run")
def daily_run(
    force: bool = typer.Option(False, "--force", help="Run even if today is a weekend or US market holiday"),
    email: bool = typer.Option(False, "--email/--no-email", help="Send the HTML Trade Ticket email"),
    to: str = typer.Option("", "--to", help="Optional recipient email override"),
) -> None:
    """9:00 AM Market-Day Pipeline: Refresh data, update Public Backtest Report, and generate Passcode-Encrypted Multi-Portfolio Trade Tickets."""
    is_open, reason = _is_us_market_open_day()
    if not is_open and not force:
        console.print(f"[yellow]Skipping daily-run: Today is not an NYSE trading day ({reason}). Use --force to override.[/yellow]")
        return

    strategy = load_strategy_settings()
    universe = load_universe_settings()
    events = load_events_settings()
    all_portfolios = load_all_portfolio_settings()

    console.print(f"[bold cyan]1/4 Refreshing market & FRED data ({reason})...[/bold cyan]")
    ingest_all(strategy, universe, start_date=strategy.backtest.start_date)

    bars, fred, earnings, health_score = load_stored_data()
    console.print("[bold cyan]2/4 Running shared 19-feature walk-forward LightGBM + Platt pipeline...[/bold cyan]")
    panel = build_feature_panel(bars, fred, earnings, strategy, universe, events)
    panel = compute_triple_barrier_labels(panel, strategy.labels)

    panel_adap = evaluate_baseline_signals(panel, strategy, use_fixed_20d=False, health_score=health_score)
    panel_fix20 = evaluate_baseline_signals(panel, strategy, use_fixed_20d=True, health_score=health_score)
    panel_pure_semi = evaluate_baseline_signals(
        panel,
        strategy,
        use_fixed_20d=False,
        health_score=health_score,
        allowed_tickers=CORE_PRE2022_SEMI_TICKERS,
    )
    panel_ml, _, cal_stats = run_walkforward_ml_predictions(panel_adap, strategy, health_score=health_score)

    console.print("[bold cyan]3/4 Updating Public Walk-Forward Backtest Report ($10K) & Equity Charts...[/bold cyan]")
    results = {
        "Baseline (SMH Bull Core + Swing)": run_portfolio_backtest(panel_adap, strategy, mode="baseline", bull_core_smh=True),
        "ML (SMH Bull Core + Swing)": run_portfolio_backtest(panel_ml, strategy, mode="ml", bull_core_smh=True),
        "Pure Pre-2022 Semi (SMH Bull Core + Swing)": run_portfolio_backtest(
            panel_pure_semi, strategy, mode="baseline", bull_core_smh=True, allowed_tickers=CORE_PRE2022_SEMI_TICKERS
        ),
        "Baseline (Adaptive L_t)": run_portfolio_backtest(panel_adap, strategy, mode="baseline", bull_core_smh=False),
        "ML (LightGBM + Platt)": run_portfolio_backtest(panel_ml, strategy, mode="ml", bull_core_smh=False),
        "Pure Pre-2022 Semi (Cash Swing)": run_portfolio_backtest(
            panel_pure_semi, strategy, mode="baseline", bull_core_smh=False, allowed_tickers=CORE_PRE2022_SEMI_TICKERS
        ),
        "Baseline (Fixed 20d)": run_portfolio_backtest(panel_fix20, strategy, mode="baseline", bull_core_smh=False),
        "SMH Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="SMH", label="SMH Buy & Hold"),
        "SOXX Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="SOXX", label="SOXX Buy & Hold"),
        "VGT Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="VGT", label="VGT Buy & Hold"),
        "QQQ Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="QQQ", label="QQQ Buy & Hold"),
        "AIQ Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="AIQ", label="AIQ Buy & Hold"),
        "IGV Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="IGV", label="IGV Buy & Hold"),
        "S&P 500 (SPY) Buy & Hold": compute_benchmark_result(panel_adap, strategy, ticker="SPY", label="S&P 500 (SPY) Buy & Hold"),
        "3M T-Bill Cash (DTB3)": compute_cash_tbill_benchmark(panel_adap, strategy),
    }
    bt_html, _ = generate_reports(
        results, cal_stats, health_score, PROJECT_ROOT / "reports" / "backtests" / "backtest_report.html"
    )

    console.print(f"[bold cyan]4/4 Generating Passcode-Encrypted Trade Tickets for {len(all_portfolios)} portfolio(s)...[/bold cyan]")
    all_plans = {}
    for slug, pcfg in all_portfolios.items():
        all_plans[slug] = build_daily_recommendation_plan(
            panel=panel_ml,
            strategy=strategy,
            universe=universe,
            portfolio=pcfg,
            health_score=health_score,
            capital_override=None,
        )

    primary_plan = next(iter(all_plans.values()))
    rec_html, rec_md = write_recommendation_reports(primary_plan, all_plans=all_plans)
    idx_html = _write_cloudflare_pages_index(primary_plan.as_of_date, primary_plan.regime_on, len(all_plans))

    console.print(f"[bold green]Updated Public Backtest Report:[/bold green] {bt_html}")
    console.print(f"[bold green]Updated Encrypted Daily Trade Tickets:[/bold green] {rec_html}")
    console.print(f"[bold green]Updated Dashboard Index:[/bold green] {idx_html}")

    if email:
        subj = f"SemiSwing Daily Trade Ticket ({primary_plan.as_of_date}) — {'RISK-ON' if primary_plan.regime_on else 'DEFENSIVE'}"
        ok = send_html_email(
            subject=subj,
            html_body=render_recommendation_email_html(primary_plan),
            text_body=render_recommendation_email_text(primary_plan),
            recipient=to or None,
        )
        console.print(
            f"[bold {'green' if ok else 'yellow'}]Email Status: {'SENT' if ok else 'SKIPPED (configure RESEND_API_KEY or SMTP in GitHub Secrets / .env)'}[/bold {'green' if ok else 'yellow'}]"
        )


@app.command("sync-secrets")
def sync_secrets(
    passcode: Optional[str] = typer.Option(
        None,
        envvar="PORTFOLIO_PASSCODE",
        help="Passcode to encrypt Daily Trade Ticket HTML reports and portfolio vault (or set PORTFOLIO_PASSCODE env var)",
    ),
) -> None:
    """Encrypt `config/portfolios/private/*.yaml` into `config/portfolios/encrypted_portfolios.json` for 9AM GitHub Actions."""
    import os
    from semiswing.config import save_encrypted_portfolios_vault

    eff_passcode = (passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if not eff_passcode:
        raise typer.BadParameter("PORTFOLIO_PASSCODE is required. Pass --passcode or set PORTFOLIO_PASSCODE in .env.")

    vault_path = save_encrypted_portfolios_vault(passcode=eff_passcode)
    console.print(f"[bold green]Successfully encrypted private portfolios into:[/bold green] {vault_path}")



@app.command()
def alert_test(
    channel: str = typer.Option("ntfy", help="Channel to test: 'email', 'ntfy', or 'sms_messages'"),
) -> None:
    """Send a test alert message over SMTP HTML email, ntfy.sh, or macOS Messages SMS."""
    msg = "SemiSwing TEST ALERT: Pipeline & risk monitor operational."
    if channel == "email":
        ok = send_html_email(
            subject="SemiSwing SMTP Test Alert",
            html_body=f"<h2>SemiSwing SMTP Test</h2><p>{msg}</p>",
            text_body=msg,
        )
    elif channel == "ntfy":
        ok = send_ntfy_push(msg)
    else:
        ok = send_macos_sms(msg)
    console.print(f"Alert test on channel '{channel}': {'SUCCESS' if ok else 'SKIPPED/FAILED (check .env & data/alerts.log)'}")


if __name__ == "__main__":
    app()

