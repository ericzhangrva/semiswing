# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2401` -> Calibrated `0.2401` (Brier Skill Score: `0.0396`)

## 1. Visual Benchmark Comparison Charts (`S&P 500`, `QQQ`, `VGT`, `SMH`, `SOXX`, `AIQ`, `IGV`, `T-Bills`)

### 1.1 Full Out-of-Sample Growth of `$10,000` (`2022–2026`, Includes 2022 Bear Market)
![Full OOS Equity Curve](charts/equity_2022_2026.png)

### 1.2 Modern AI Cycle Growth of `$10,000` (`2023–2026`, Rebased Jan 1, 2023)
![Modern AI Cycle Equity Curve](charts/equity_2023_2026_ai_era.png)

### 1.3 Underwater Drawdown Comparison (`2022–2026`)
![Underwater Drawdowns](charts/drawdown_comparison.png)

### 1.4 Calendar Year Returns & Risk-Return Efficiency (`2022–2026`)
![Annual Returns and Risk-Return Scatter](charts/annual_returns_and_risk_scatter.png)

## 2. Institutional Validation Gates (§9)

### 2.1 SMH Bull Core + Swing Mode (Active Secular Bull Core Sweep)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.77 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.962 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.68 ; OOS: 3.44 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.35% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.35% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.42 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -20.9% ; DD: 21.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0396 ; SR Lift: -0.01 ; Sortino Lift: +0.03 ; CAGR Lift: +4.1% ; DD Red: -5.0% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.75 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.959 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.76 ; OOS: 3.49 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.71% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.71% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.38 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -21.0% ; DD: 21.2% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0396 ; SR Lift: +0.06 ; Sortino Lift: +0.08 ; CAGR Lift: +9.6% ; DD Red: -4.9% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 839.5 | 59.88 | 1.42 | 0.922 | 1.46 | 30.38 | 25.8 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 912.84 | 62.42 | 1.42 | 0.924 | 1.49 | 35.35 | 25.8 | 91 | 47.3 | 3.44 | 1.65 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 370.17 | 38.3 | 1.02 | 0.712 | 1.03 | 37.84 | 27.4 | 87 | 54.0 | 3.19 | 1.2 |
| `Baseline (Adaptive `L_t`)` | 623.3 | 51.36 | 1.33 | 0.893 | 1.4 | 30.79 | 25.8 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 773.81 | 57.47 | 1.38 | 0.914 | 1.47 | 35.71 | 25.8 | 91 | 47.3 | 3.49 | 1.65 |
| Pure Pre-2022 Semi (Cash Swing) | 288.01 | 32.85 | 0.96 | 0.662 | 0.98 | 35.52 | 27.4 | 88 | 53.4 | 3.14 | 1.18 |
| Baseline (Fixed 20d) | 654.27 | 52.69 | 1.32 | 0.887 | 1.39 | 34.9 | 25.9 | 96 | 45.8 | 3.79 | 1.64 |
| SMH Buy & Hold | 256.31 | 30.5 | 0.8 | 0.529 | 0.79 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 182.25 | 24.28 | 0.65 | 0.402 | 0.64 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 114.76 | 17.36 | 0.59 | 0.353 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 84.03 | 13.63 | 0.5 | 0.28 | 0.49 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 99.55 | 15.57 | 0.53 | 0.302 | 0.52 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 34.86 | 6.47 | 0.22 | 0.12 | 0.22 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 70.95 | 11.89 | 0.51 | 0.288 | 0.5 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.9 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -20.89 | -20.96 | -2.54 | 0.0 | -2.01 | 21.1 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -20.97 | -21.05 | -2.56 | 0.0 | -2.02 | 21.19 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (Cash Swing) | -20.88 | -20.95 | -2.64 | 0.0 | -2.06 | 21.14 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| Baseline (Fixed 20d) | -15.72 | -15.78 | -2.41 | 0.0 | -1.94 | 16.0 | 88.8 | 13 | 0.0 | 0.0 | -0.56 |
| SMH Buy & Hold | -34.97 | -35.08 | -0.85 | 0.0 | -0.87 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | -36.35 | -36.47 | -0.88 | 0.0 | -0.89 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | -30.28 | -30.38 | -0.96 | 0.0 | -0.98 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | -33.22 | -33.33 | -1.17 | 0.0 | -1.19 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | -36.62 | -36.74 | -1.2 | 0.0 | -1.24 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | -34.91 | -35.02 | -1.0 | 0.0 | -1.02 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | -18.65 | -18.71 | -0.82 | 0.0 | -0.85 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 2.03 | 2.04 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 5. View B — Modern AI Cycle (`2023–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 1081.78 | 92.27 | 1.78 | 0.961 | 1.79 | 30.38 | 8.9 | 78 | 60.3 | 3.59 | 1.98 |
| ML (SMH Bull Core + Swing) | 1180.07 | 96.38 | 1.77 | 0.962 | 1.82 | 35.35 | 8.9 | 74 | 58.1 | 3.68 | 2.18 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 495.58 | 60.37 | 1.34 | 0.822 | 1.33 | 37.84 | 11.0 | 73 | 64.4 | 3.71 | 1.56 |
| `Baseline (Adaptive `L_t`)` | 807.63 | 79.29 | 1.69 | 0.947 | 1.74 | 30.79 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 1005.52 | 88.9 | 1.75 | 0.959 | 1.82 | 35.71 | 8.9 | 74 | 58.1 | 3.76 | 2.18 |
| Pure Pre-2022 Semi (Cash Swing) | 390.32 | 52.33 | 1.28 | 0.792 | 1.31 | 35.52 | 11.0 | 74 | 63.5 | 3.75 | 1.53 |
| Baseline (Fixed 20d) | 794.79 | 78.62 | 1.63 | 0.931 | 1.68 | 34.9 | 9.2 | 83 | 53.0 | 4.11 | 1.99 |
| SMH Buy & Hold | 452.13 | 57.19 | 1.33 | 0.818 | 1.31 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 347.8 | 48.71 | 1.12 | 0.694 | 1.11 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 211.0 | 35.03 | 1.2 | 0.746 | 1.15 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 177.45 | 31.01 | 1.22 | 0.764 | 1.21 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 214.71 | 35.46 | 1.19 | 0.74 | 1.16 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 106.76 | 21.2 | 0.7 | 0.377 | 0.69 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 111.02 | 21.86 | 1.1 | 0.686 | 1.1 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.47 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.42% | +125.14% | 53.9% | 1.71 | 1.71 | -30.79% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.97% | -21.05% | 9.9% | -2.56 | -2.02 | -21.19% | 89.6% | 17 | 0.0% | 0.00 | -0.62R |
| 2023 | +47.20% | +47.65% | 20.8% | 1.74 | 1.84 | -19.10% | 6.0% | 25 | 68.0% | 4.33 | +0.89R |
| 2024 | +85.71% | +85.71% | 31.9% | 1.95 | 2.18 | -23.63% | 7.5% | 22 | 59.1% | 5.08 | +1.18R |
| 2025 | +121.18% | +122.59% | 34.2% | 2.40 | 2.63 | -19.04% | 20.4% | 12 | 58.3% | 29.92 | +8.39R |
| 2026 | +76.43% | +104.50% | 60.0% | 1.44 | 1.45 | -35.71% | 0.0% | 15 | 40.0% | 1.14 | +0.81R |

## 8. Recent 25 OOS Trades (ML (SMH Bull Core + Swing))

> **Section 8 Trade Blotter Legend & Quantitative Diagnostics**
> - **Shares & Position ($):** Dynamically calculated via Volatility-Parity / Fixed-Fractional Risk Sizing: $\text{Shares} = (\text{Portfolio Equity} \times \text{Base Risk} \times M_t \times S_{i,t}) / \text{Stop Distance}$. Each trade risks a fixed fraction of portfolio equity, so share counts and dollar allocations vary based on stock ATR volatility, tier conviction, meta-labeling multiplier $S_{i,t}$, and compounding portfolio equity over time.
> - **Partial Exits (TP1) & Blended Returns:** When Take Profit 1 triggers, partial shares are sold and stop ratchets to breakeven. `Exit ($)` reports final runner exit; `Return (%)` is the blended net return.
> - **Tier:** `CONSENSUS` (dual-engine alignment, 1.0% risk), `HIGH` (standalone ML top-quintile RS, 1.0% risk), `MEDIUM` (conservative 0.75% risk), `LOW` (lower-conviction meta-labeling score $S_{i,t} < 0.85$, 0.50% risk).
> - **Win Prob:** Platt-calibrated out-of-fold probability $P(\text{TP1 before Stop})$. Break-even threshold is $> 40.0\%$ with a 1.5:1 payoff ratio.
> - **Sizing Scalar:** Meta-labeling sizing multiplier $S_{i,t} = 0.50 + \text{Rank}_{\text{OOF}}(\hat{p}) \in [0.50, 1.50]$ scaling allocation by model confidence.
> - **Top Model Drivers (SHAP):** Single-feature marginal attributions detailing model conviction:
>   - `sector_rs`: 20-day relative strength of SMH vs SPY. Positive values confirm semiconductor sector leadership.
>   - `vix_ts`: Volatility term structure ratio (VIX / VIX3M). Values $< 1.0$ confirm normal contango (calm regime); $\ge 1.0$ indicates backwardation.
>   - `skew_idx`: CBOE SKEW Index 60-day rolling z-score. Elevated values ($> +1.5$) indicate institutional tail-risk put demand.
>   - `resid_mom_60`: 60-day idiosyncratic residual momentum relative to SMH after stripping market beta.
>   - `resid_mom_20`: 20-day idiosyncratic residual momentum relative to SMH after stripping market beta.
>   - `rs_rank`: Cross-sectional percentile rank ($[0.0, 1.0]$) of 20-day residual momentum across the universe.
>   - `vol_compress`: Realized volatility compression ratio (RV_10d / RV_60d). Values $< 0.70$ indicate price coiling prior to breakout.
>   - `vxn_squeeze_vel`: 252-day rolling z-score of 5-day change in Nasdaq Volatility Index (VXN).
>   - `slope_r2_20d`: Coefficient of determination ($R^2 \in [0, 1]$) from 20-day log-price regression measuring trend smoothness.
>   - `slope_t_norm`: Adaptive window $L_t$ normalized OLS $t$-statistic measuring directional trend conviction.
>   - `slope_accel`: Multi-scale slope acceleration: $(\beta_{10d} - \beta_{40d}) / \sigma_{20}$.
>   - `ema20_slope`: 5-day slope of 20-day EMA in ATR units.
>   - `ema50_slope`: 10-day slope of 50-day EMA in ATR units.

| Ticker | Tier | Shares | Position ($) | Entry Date | Exit Date | Days Held | Entry ($) | Exit ($) | Initial Stop ($) | Return (%) | Net P&L ($) | R-Multiple | Exit Reason | Win Prob | Sizing Scalar | Top Model Drivers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STX | MEDIUM | 22.7 | $2,182.63 | 2025-01-31 | 2025-02-28 | 20 | $95.99 | $99.58 | $85.96 | +3.74% | +82 | +0.36R | Regime Off | 36.1% | 1.02x | `vol_compress=1.65 (+0.010) ; sector_rs=-0.03 (-0.010) ; skew_idx=-0.52 (-0.004) ; vix_ts=0.88 (+0.003) ; slope_r2_20d=0.71 (-0.003)` |
| INTC | MEDIUM | 222.2 | $5,457.76 | 2025-02-24 | 2025-02-28 | 5 | $24.57 | $23.71 | $20.88 | -3.48% | -190 | -0.23R | Regime Off | 37.5% | 1.12x | `sector_rs=-0.05 (+0.033) ; vxn_squeeze_vel=0.92 (-0.030) ; slope_accel=0.63 (+0.008) ; vol_compress=1.77 (+0.007) ; vix_ts=0.93 (-0.006)` |
| CEG | MEDIUM | 9.2 | $2,550.34 | 2025-05-13 | 2025-09-02 | 77 | $278.39 | $298.61 | $237.89 | +12.09% | +308 | +0.83R | Stop Gap | 36.1% | 1.06x | `vix_ts=0.91 (+0.026) ; slope_r2_20d=0.89 (-0.008) ; skew_idx=-0.25 (-0.007) ; sector_rs=0.09 (-0.003) ; rs_rank=0.86 (+0.002)` |
| STX | MEDIUM | 34.9 | $3,511.38 | 2025-05-13 | 2025-10-10 | 105 | $100.52 | $212.97 | $89.16 | +89.06% | +3,127 | +7.88R | Trail Stop Eod | 37.2% | 1.13x | `vix_ts=0.91 (+0.026) ; skew_idx=-0.25 (-0.007) ; sector_rs=0.09 (-0.004) ; rs_rank=0.98 (+0.003) ; slope_r2_20d=0.95 (-0.003)` |
| AMD | LOW | 23.4 | $5,149.93 | 2025-10-13 | 2025-11-18 | 27 | $220.35 | $230.13 | $187.30 | +4.44% | +228 | +0.30R | Time Stop 25D | 31.4% | 0.68x | `skew_idx=-2.34 (-0.130) ; sector_rs=0.07 (+0.060) ; vix_ts=0.95 (+0.035) ; slope_accel=0.75 (+0.031) ; slope_t_norm_40d=1.22 (+0.024)` |
| VRT | MEDIUM | 24 | $2,426.90 | 2025-05-13 | 2025-12-17 | 152 | $100.97 | $149.62 | $85.82 | +43.88% | +1,065 | +2.93R | Trail Stop Eod | 35.9% | 1.04x | `vix_ts=0.91 (+0.025) ; skew_idx=-0.25 (-0.007) ; slope_r2_20d=0.88 (-0.006) ; vol_compress=0.61 (-0.003) ; slope_r2=0.90 (-0.003)` |
| GOOGL | HIGH | 58.2 | $18,964.39 | 2025-11-25 | 2025-12-31 | 25 | $325.59 | $312.17 | $292.61 | -4.12% | -782 | -0.41R | Time Stop 25D | 42.8% | 1.37x | `resid_mom_60=0.33 (+0.064) ; sector_rs=-0.03 (+0.040) ; resid_mom_20=0.19 (+0.009) ; slope_r2_20d=0.50 (-0.008) ; slope_t_norm_40d=8.84 (+0.007)` |
| APP | HIGH | 4.2 | $3,071.14 | 2025-12-24 | 2026-01-02 | 6 | $728.36 | $628.82 | $629.26 | -13.67% | -420 | -1.00R | Stop | 38.9% | 1.20x | `vix_ts=0.78 (-0.064) ; skew_idx=2.44 (+0.035) ; rs_rank=1.00 (+0.025) ; slope_r2_20d=0.60 (-0.009) ; resid_mom_20=0.21 (+0.006)` |
| LRCX | LOW | 14.8 | $2,811.84 | 2026-01-05 | 2026-03-06 | 43 | $189.69 | $198.84 | $170.24 | +8.58% | +241 | +0.84R | Trail Stop Eod | 26.5% | 0.55x | `skew_idx=-0.98 (-0.053) ; vxn_squeeze_vel=0.75 (-0.034) ; vix_ts=0.81 (-0.027) ; slope_r2_20d=0.62 (-0.007) ; resid_mom_20=0.11 (+0.004)` |
| MU | HIGH | 61.1 | $18,031.48 | 2026-01-02 | 2026-03-30 | 60 | $295.12 | $321.47 | $254.16 | +13.04% | +2,351 | +0.94R | Trail Stop Eod | 45.2% | 1.42x | `rs_rank=0.98 (+0.033) ; resid_mom_60=0.33 (+0.032) ; vxn_squeeze_vel=0.62 (+0.022) ; sector_rs=0.00 (+0.020) ; slope_r2_20d=0.64 (-0.012)` |
| WDC | MEDIUM | 66.3 | $3,104.16 | 2025-05-13 | 2026-07-07 | 288 | $46.85 | $531.86 | $41.29 | +781.78% | +24,268 | +65.85R | Stop Gap | 36.0% | 1.05x | `vix_ts=0.91 (+0.025) ; slope_r2_20d=0.91 (-0.009) ; skew_idx=-0.25 (-0.007) ; slope_r2=0.91 (-0.003) ; vol_compress=0.65 (-0.003)` |
| LITE | HIGH | 88.1 | $11,666.59 | 2025-09-03 | 2026-07-07 | 211 | $132.43 | $698.93 | $115.52 | +326.65% | +38,109 | +25.58R | Stop Gap | 39.0% | 1.23x | `resid_mom_60=0.29 (+0.049) ; slope_r2_20d=0.79 (-0.007) ; ema50_slope=1.93 (-0.006) ; slope_t_norm_40d=12.28 (+0.004) ; vix_ts=0.89 (+0.004)` |
| ARM | HIGH | 101.6 | $15,700.31 | 2026-04-01 | 2026-07-14 | 71 | $154.50 | $280.97 | $131.32 | +69.41% | +10,898 | +4.63R | Trail Stop Eod | 42.3% | 1.35x | `rs_rank=0.98 (+0.036) ; vix_ts=0.99 (+0.018) ; slope_t_norm=6.62 (+0.013) ; skew_idx=0.04 (-0.009) ; slope_r2_20d=0.73 (-0.009)` |
| P | HIGH | 588.5 | $47,003.83 | 2026-07-09 | 2026-07-15 | 5 | $79.87 | $67.84 | $67.89 | -15.06% | -7,079 | -1.00R | Stop | 45.0% | 1.43x | `skew_idx=1.86 (+0.040) ; vxn_squeeze_vel=0.21 (+0.024) ; rs_rank=0.80 (+0.008) ; vix_ts=0.87 (+0.004) ; slope_accel=0.33 (+0.003)` |
| META | HIGH | 32.4 | $21,530.40 | 2026-07-15 | 2026-07-27 | 9 | $663.54 | $592.99 | $587.40 | -10.63% | -2,289 | -0.93R | Earnings Exit | 39.3% | 1.20x | `rs_rank=0.98 (+0.020) ; sector_rs=-0.05 (+0.016) ; vix_ts=0.85 (-0.007) ; skew_idx=0.75 (-0.007) ; vxn_squeeze_vel=-0.62 (-0.006)` |
| AMZN | HIGH | 150.4 | $37,434.78 | 2026-07-20 | 2026-07-28 | 7 | $248.93 | $230.70 | $226.16 | -7.33% | -2,742 | -0.80R | Earnings Exit | 39.7% | 1.23x | `vxn_squeeze_vel=1.39 (+0.020) ; skew_idx=1.15 (-0.020) ; slope_t_norm_40d=-2.14 (+0.013) ; sector_rs=-0.11 (-0.008) ; vix_ts=0.91 (+0.004)` |
| AAPL | MEDIUM | 106.1 | $33,395.57 | 2026-07-10 | 2026-08-13 | 25 | $314.67 | $305.05 | $289.65 | -3.06% | -1,021 | -0.38R | Time Stop 25D | 35.8% | 0.94x | `vix_ts=0.83 (-0.017) ; rs_rank=0.80 (+0.008) ; vxn_squeeze_vel=-0.33 (-0.004) ; slope_sharpe=4.73 (-0.003) ; slope_t_norm_40d=-0.46 (-0.002)` |
| AMZN | MEDIUM | 113.5 | $31,991.78 | 2026-08-05 | 2026-08-20 | 12 | $281.79 | $259.93 | $252.32 | -7.76% | -2,482 | -0.74R | Time Stop 12D | 36.7% | 1.00x | `vxn_squeeze_vel=-1.14 (+0.068) ; sector_rs=-0.04 (+0.040) ; slope_t_norm_40d=0.85 (+0.024) ; skew_idx=-3.40 (-0.013) ; slope_accel=0.48 (+0.009)` |
| P | HIGH | 388.4 | $43,140.77 | 2026-08-21 | 2026-08-24 | 2 | $111.08 | $100.37 | $94.76 | -9.64% | -4,159 | -0.66R | Earnings Exit | 49.1% | 1.48x | `vxn_squeeze_vel=0.67 (+0.036) ; sector_rs=-0.06 (+0.023) ; resid_mom_60=0.27 (+0.022) ; ema20_slope=2.29 (+0.019) ; vix_ts=0.84 (+0.012)` |
| PLTR | MEDIUM | 124.8 | $19,468.49 | 2026-08-06 | 2026-09-10 | 25 | $155.98 | $165.74 | $132.58 | +6.26% | +1,219 | +0.42R | Time Stop 25D | 35.3% | 0.88x | `skew_idx=-1.91 (-0.054) ; vxn_squeeze_vel=-2.33 (+0.051) ; sector_rs=-0.07 (+0.031) ; slope_t_norm_40d=0.83 (+0.025) ; slope_accel=0.34 (+0.008)` |
| ORCL | LOW | 114.4 | $17,779.84 | 2026-08-14 | 2026-09-10 | 19 | $155.37 | $152.27 | $132.74 | -2.00% | -355 | -0.14R | Earnings Exit | 33.6% | 0.76x | `slope_t_norm_40d=-1.24 (+0.017) ; vix_ts=0.79 (-0.016) ; sector_rs=-0.00 (+0.016) ; skew_idx=-1.48 (-0.015) ; vxn_squeeze_vel=-0.96 (+0.015)` |
| SNDK | MEDIUM | 15.4 | $23,641.38 | 2026-08-25 | 2026-10-08 | 32 | $1534.76 | $1608.33 | $1304.55 | +4.79% | +1,133 | +0.32R | Time Stop 25D | 38.5% | 1.14x | `vxn_squeeze_vel=0.38 (+0.017) ; sector_rs=-0.04 (-0.006) ; slope_t_norm_40d=-1.74 (+0.004) ; slope_r2_20d=0.68 (-0.003) ; vix_ts=0.85 (-0.002)` |
| MU | HIGH | 37.3 | $37,038.55 | 2026-09-11 | 2026-10-15 | 25 | $993.74 | $930.59 | $844.68 | -6.35% | -2,354 | -0.42R | Time Stop 25D | 40.3% | 1.27x | `rs_rank=0.98 (+0.026) ; skew_idx=0.54 (-0.018) ; vix_ts=0.90 (-0.009) ; vol_compress=0.54 (+0.006) ; vxn_squeeze_vel=1.06 (+0.006)` |
| DELL | HIGH | 58.5 | $8,483.57 | 2026-03-11 | 2026-10-16 | 153 | $145.07 | $451.39 | $123.31 | +165.23% | +14,017 | +11.02R | Trail Stop Eod | 41.0% | 1.29x | `rs_rank=0.98 (+0.023) ; vix_ts=0.98 (+0.013) ; sector_rs=0.00 (+0.012) ; slope_r2_20d=0.66 (-0.011) ; skew_idx=1.02 (-0.003)` |
| SNPS | MEDIUM | 48.5 | $24,779.63 | 2026-10-09 | 2026-10-16 | 6 | $510.84 | $454.03 | $454.35 | -11.12% | -2,755 | -1.01R | Stop | 37.8% | 1.09x | `vix_ts=0.85 (-0.019) ; rs_rank=0.98 (+0.012) ; slope_r2_20d=0.87 (-0.010) ; resid_mom_60=0.15 (-0.006) ; skew_idx=0.95 (-0.004)` |
