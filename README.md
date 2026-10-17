# SemiSwing

A 2–5 week momentum swing signal, walk-forward backtest, and daily portfolio recommendation system focused on Semiconductor & AI leaders (`50` regular stocks across 5 AI ecosystem groups) and unleveraged sector/index ETFs (`SMH`, `SOXX`, `VGT`, `QQQ`, `SPY`, `AIQ`, `IGV`). Unallocated cash accrues daily 3-Month Treasury Bill interest (`FRED DTB3`), with an **SMH Bull Core + Swing** sleeve during secular semiconductor bull trends.

- **Live Cloud Dashboard (`semiswing.pages.dev`):** [https://semiswing.pages.dev/](https://semiswing.pages.dev/)
- **Live Daily Trade Tickets (Passcode Locked):** [https://semiswing.pages.dev/daily/latest_recommendations.html](https://semiswing.pages.dev/daily/latest_recommendations.html) *(multi-portfolio tabs)*
- **Live Interactive Backtest Report (Public `$10K`):** [https://semiswing.pages.dev/backtests/backtest_report.html](https://semiswing.pages.dev/backtests/backtest_report.html) *(local: [reports/backtests/backtest_report.html](reports/backtests/backtest_report.html))*
- **Static Markdown Backtest Report:** [reports/backtests/backtest_report.md](reports/backtests/backtest_report.md)
- **Architecture & Specification:** [docs/instruction.md](docs/instruction.md)

---

## How It Runs Daily (9:00 AM ET GitHub Actions + Cloudflare Pages)

1. **Automated 9:00 AM ET Cloud Run ([.github/workflows/daily_semiswing.yml](.github/workflows/daily_semiswing.yml)):**
   - Every weekday at **9:00 AM ET (`13:00 UTC`)**, GitHub Actions runs `semiswing daily-run --no-email`.
   - **NYSE Holiday Guard:** Automatically checks if the US stock market is open today (skipping weekends and all 10 NYSE holidays).
   - **Single-Pass Refresh:** Ingests the latest daily OHLCV (`yfinance` + `Stooq`), FRED macro series (`DTB3`, `DGS10`, `DTWEXBGS`, `VIXCLS`, `VXVCLS`, `BAMLH0A0HYM2`), and earnings dates, then runs the 19-feature walk-forward LightGBM + Platt pipeline once.
   - **Updates Both Reports & Redeploys Cloudflare Pages:**
     1. Recomputes the public `$10,000` `2022–Present` out-of-sample walk-forward backtest and equity charts at [reports/backtests/backtest_report.html](reports/backtests/backtest_report.html).
     2. Decrypts the portfolio vault in memory, generates **Step 1 (Holdings Actions) / Step 2 (Exact `$` Buy Tickets)** for all portfolio snapshots, and writes the passcode-encrypted multi-portfolio HTML report to [reports/daily/latest_recommendations.html](reports/daily/latest_recommendations.html).
     3. Commits the updated `reports/` directory back to `main`, automatically triggering **Cloudflare Pages** (`https://semiswing.pages.dev/`).
2. **Midnight Multi-Snapshot Sync (`snapshots/<name>.png` $\rightarrow$ Encrypted Vault):**
   - Drop one or more brokerage screenshots into `/snapshots/`, which stays gitignored on your Mac.
   - Private portfolio configs live in gitignored `config/portfolios/private/<name>.yaml` and are encrypted into [config/portfolios/encrypted_portfolios.json](config/portfolios/encrypted_portfolios.json) via `semiswing sync-secrets` so no plaintext holdings or dollar balances ever appear in the public GitHub repository.

---

## Out-of-Sample Walk-Forward Highlights (`2022–2026`, `$10,000` Initial Equity)

| Strategy / Benchmark | 2022–2026 Total Return | 2022–2026 CAGR | Excess Sharpe | Max Drawdown | 2022 Bear Return | Profit Factor | Trades |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Baseline (SMH Bull Core + Swing)** | `+652.62%` | `52.73%` | `1.21` | `32.58%` | `-23.03%` | `1.89` | `128` |
| **ML (SMH Bull Core + Swing)** | `+505.06%` | `45.90%` | `1.09` | `33.70%` | `-28.67%` | `3.35` | `71` |
| **Baseline (Adaptive $L_t$, Cash Swing)** | `+379.14%` | `38.92%` | `1.00` | `37.28%` | `-15.70%` | `2.00` | `128` |
| **ML (LightGBM + Platt, Cash Swing)** | `+328.75%` | `35.72%` | `1.01` | `25.44%` | `-11.79%` | `3.38` | `70` |
| **Pure Pre-2022 Semi (SMH Bull Core + Swing)** | `+265.86%` | `31.28%` | `0.85` | `42.22%` | `-24.48%` | `1.59` | `98` |
| **SMH Buy & Hold** | `+263.05%` | `31.07%` | `0.81` | `45.14%` | `-34.97%` | — | — |
| **QQQ Buy & Hold** | `+86.50%` | `13.97%` | `0.51` | `34.83%` | `-33.22%` | — | — |
| **S&P 500 (SPY) Buy & Hold** | `+72.13%` | `12.07%` | `0.52` | `24.50%` | `-18.65%` | — | — |

---

## CLI Quickstart (Local macOS or Cloud)

```bash
# 1. Full 9:00 AM Market-Day Pipeline (Refresh data + update Backtest Report + update Daily Trade Ticket)
.venv/bin/semiswing daily-run --force --no-email

# 2. Generate today's $1M Daily Trade Ticket only
.venv/bin/semiswing recommend --no-email

# 3. Run only the $10K walk-forward backtest report (Baseline vs LightGBM+Platt vs Benchmarks)
.venv/bin/semiswing backtest --report reports/backtests/backtest_report.html

# 4. Inspect raw universe feature & signal table on the latest bar
.venv/bin/semiswing scan

# 5. Run unit, purged CV, and causal look-ahead tests
.venv/bin/pytest -q
```

