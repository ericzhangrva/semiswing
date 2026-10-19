# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2404` -> Calibrated `0.2404` (Brier Skill Score: `0.0384`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.85 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.972 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 5.35 ; OOS: 4.79 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 29.39% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 29.39% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.48 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -21.5% ; DD: 21.7% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0384 ; SR Lift: +0.01 ; Sortino Lift: +0.06 ; CAGR Lift: +7.4% ; DD Red: -2.7% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.81 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.968 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 5.41 ; OOS: 4.78 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 28.96% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 28.96% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.44 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -21.6% ; DD: 21.8% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0384 ; SR Lift: +0.03 ; Sortino Lift: +0.08 ; CAGR Lift: +11.6% ; DD Red: -3.1% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 918.79 | 62.75 | 1.47 | 0.937 | 1.52 | 26.73 | 25.8 | 90 | 52.2 | 3.97 | 1.52 |
| ML (SMH Bull Core + Swing) | 1058.64 | 67.2 | 1.48 | 0.941 | 1.56 | 29.39 | 25.8 | 90 | 46.7 | 4.79 | 1.55 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 381.18 | 39.05 | 1.04 | 0.724 | 1.05 | 37.84 | 27.5 | 87 | 54.0 | 3.19 | 1.2 |
| `Baseline (Adaptive `L_t`)` | 699.16 | 54.67 | 1.4 | 0.918 | 1.47 | 25.88 | 25.8 | 89 | 51.7 | 3.99 | 1.49 |
| ML (LightGBM + Platt) | 891.76 | 61.83 | 1.44 | 0.931 | 1.54 | 28.96 | 25.8 | 90 | 46.7 | 4.78 | 1.55 |
| Pure Pre-2022 Semi (Cash Swing) | 292.82 | 33.25 | 0.97 | 0.669 | 0.99 | 35.03 | 27.5 | 88 | 53.4 | 3.14 | 1.18 |
| Baseline (Fixed 20d) | 594.63 | 50.18 | 1.26 | 0.861 | 1.33 | 34.33 | 26.1 | 96 | 45.8 | 3.43 | 1.64 |
| SMH Buy & Hold | 263.05 | 31.07 | 0.81 | 0.539 | 0.8 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 189.43 | 24.98 | 0.66 | 0.414 | 0.66 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 118.35 | 17.8 | 0.6 | 0.365 | 0.59 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 86.5 | 13.97 | 0.51 | 0.289 | 0.5 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 103.13 | 16.03 | 0.54 | 0.314 | 0.53 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 39.46 | 7.23 | 0.25 | 0.131 | 0.25 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 72.13 | 12.07 | 0.52 | 0.294 | 0.51 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.88 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.68 | -20.76 | -2.64 | 0.0 | -2.08 | 20.94 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -21.52 | -21.6 | -2.59 | 0.0 | -2.02 | 21.73 | 89.6 | 17 | 0.0 | 0.0 | -0.65 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.49 | -20.56 | -2.65 | 0.0 | -2.08 | 20.75 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -21.6 | -21.68 | -2.6 | 0.0 | -2.03 | 21.81 | 89.6 | 17 | 0.0 | 0.0 | -0.65 |
| Pure Pre-2022 Semi (Cash Swing) | -20.88 | -20.95 | -2.64 | 0.0 | -2.06 | 21.14 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| Baseline (Fixed 20d) | -15.23 | -15.28 | -2.4 | 0.0 | -1.92 | 15.51 | 88.8 | 13 | 0.0 | 0.0 | -0.56 |
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
| Baseline (SMH Bull Core + Swing) | 1184.24 | 96.83 | 1.84 | 0.97 | 1.86 | 26.73 | 8.9 | 75 | 62.7 | 4.39 | 1.95 |
| ML (SMH Bull Core + Swing) | 1376.09 | 104.23 | 1.85 | 0.972 | 1.92 | 29.39 | 8.9 | 73 | 57.5 | 5.35 | 2.07 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 509.52 | 61.52 | 1.36 | 0.831 | 1.35 | 37.84 | 11.1 | 73 | 64.4 | 3.71 | 1.56 |
| `Baseline (Adaptive `L_t`)` | 904.96 | 84.43 | 1.78 | 0.962 | 1.83 | 25.88 | 8.9 | 74 | 62.2 | 4.53 | 1.92 |
| ML (LightGBM + Platt) | 1164.79 | 96.03 | 1.81 | 0.968 | 1.91 | 28.96 | 8.9 | 73 | 57.5 | 5.41 | 2.07 |
| Pure Pre-2022 Semi (Cash Swing) | 396.4 | 52.96 | 1.29 | 0.798 | 1.32 | 35.03 | 11.1 | 74 | 63.5 | 3.75 | 1.53 |
| Baseline (Fixed 20d) | 719.27 | 74.7 | 1.56 | 0.911 | 1.61 | 34.33 | 9.5 | 83 | 53.0 | 3.69 | 1.98 |
| SMH Buy & Hold | 462.58 | 58.12 | 1.34 | 0.826 | 1.33 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 359.21 | 49.83 | 1.14 | 0.707 | 1.13 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 216.2 | 35.71 | 1.22 | 0.759 | 1.17 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 181.17 | 31.55 | 1.25 | 0.776 | 1.23 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 220.35 | 36.18 | 1.21 | 0.754 | 1.19 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 113.8 | 22.33 | 0.73 | 0.405 | 0.73 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 112.48 | 22.13 | 1.12 | 0.696 | 1.11 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.45 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.49% | -20.56% | 9.3% | -2.65 | -2.08 | -20.75% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +110.84% | +158.41% | 53.8% | 1.98 | 1.99 | -25.88% | 0.0% | 12 | 58.3% | 1.21 | +0.40R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -21.60% | -21.68% | 10.0% | -2.60 | -2.03 | -21.81% | 89.6% | 17 | 0.0% | 0.00 | -0.65R |
| 2023 | +46.57% | +47.02% | 20.9% | 1.72 | 1.83 | -19.33% | 6.0% | 25 | 68.0% | 4.20 | +0.89R |
| 2024 | +81.21% | +81.21% | 32.5% | 1.85 | 2.04 | -24.49% | 7.5% | 24 | 50.0% | 4.02 | +0.98R |
| 2025 | +131.48% | +133.04% | 36.7% | 2.39 | 2.58 | -18.85% | 20.4% | 12 | 58.3% | 35.00 | +8.39R |
| 2026 | +98.61% | +139.49% | 60.4% | 1.70 | 1.74 | -28.96% | 0.0% | 12 | 50.0% | 1.15 | +0.35R |

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
| PLTR | HIGH | 168.5 | $6,070.64 | 2024-09-20 | 2025-02-24 | 106 | $36.04 | $95.81 | $31.91 | +129.64% | +7,870 | +11.33R | Stop Gap | 41.1% | 1.27x | `sector_rs=-0.06 (-0.050) ; skew_idx=2.90 (-0.043) ; resid_mom_60=0.45 (+0.031) ; ema20_slope=1.50 (-0.011) ; ema50_slope=2.06 (-0.011)` |
| LRCX | MEDIUM | 55.6 | $4,753.85 | 2025-02-24 | 2025-02-27 | 4 | $85.47 | $76.16 | $76.21 | -10.90% | -518 | -1.01R | Stop | 35.5% | 0.98x | `sector_rs=-0.05 (+0.029) ; vxn_squeeze_vel=0.92 (-0.025) ; vix_ts=0.93 (-0.009) ; slope_r2_20d=0.77 (-0.008) ; resid_mom_60=0.13 (+0.007)` |
| STX | MEDIUM | 68.3 | $6,557.59 | 2025-01-31 | 2025-02-28 | 20 | $95.99 | $99.58 | $85.96 | +3.74% | +245 | +0.36R | Regime Off | 36.6% | 1.06x | `vol_compress=1.65 (+0.010) ; vix_ts=0.88 (+0.009) ; sector_rs=-0.03 (-0.009) ; skew_idx=-0.52 (-0.006) ; vxn_squeeze_vel=0.49 (-0.004)` |
| META | MEDIUM | 7 | $4,802.21 | 2025-01-31 | 2025-02-28 | 20 | $687.54 | $663.92 | $627.77 | -3.43% | -165 | -0.40R | Regime Off | 34.6% | 0.91x | `sector_rs=-0.03 (-0.009) ; vix_ts=0.88 (+0.008) ; slope_r2_20d=0.71 (-0.007) ; skew_idx=-0.52 (-0.006) ; resid_mom_60=0.19 (-0.006)` |
| INTC | HIGH | 299.3 | $7,353.36 | 2025-02-24 | 2025-02-28 | 5 | $24.57 | $23.71 | $20.88 | -3.48% | -256 | -0.23R | Regime Off | 38.2% | 1.17x | `sector_rs=-0.05 (+0.030) ; vxn_squeeze_vel=0.92 (-0.030) ; rs_rank=0.96 (+0.010) ; vol_compress=1.77 (+0.009) ; vix_ts=0.93 (-0.008)` |
| CEG | MEDIUM | 8.5 | $2,370.85 | 2025-05-13 | 2025-09-02 | 77 | $278.39 | $298.61 | $237.89 | +12.09% | +287 | +0.83R | Stop Gap | 35.4% | 1.00x | `vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.011) ; skew_idx=-0.25 (-0.010) ; slope_r2_20d=0.89 (-0.006) ; rs_rank=0.86 (+0.005)` |
| STX | HIGH | 43.8 | $4,402.69 | 2025-05-13 | 2025-10-10 | 105 | $100.52 | $212.97 | $89.16 | +89.06% | +3,921 | +7.88R | Trail Stop Eod | 37.5% | 1.16x | `vix_ts=0.91 (+0.029) ; sector_rs=0.09 (-0.011) ; skew_idx=-0.25 (-0.011) ; slope_r2_20d=0.95 (+0.010) ; rs_rank=0.98 (+0.010)` |
| AMD | LOW | 25.9 | $5,709.21 | 2025-10-13 | 2025-11-18 | 27 | $220.35 | $230.13 | $187.30 | +4.44% | +253 | +0.30R | Time Stop 25D | 32.8% | 0.75x | `skew_idx=-2.34 (-0.130) ; sector_rs=0.07 (+0.078) ; slope_accel=0.75 (+0.037) ; vix_ts=0.95 (+0.028) ; slope_t_norm_40d=1.22 (+0.019)` |
| VRT | MEDIUM | 22.3 | $2,253.93 | 2025-05-13 | 2025-12-17 | 152 | $100.97 | $149.62 | $85.82 | +43.88% | +989 | +2.93R | Trail Stop Eod | 35.1% | 0.98x | `vix_ts=0.91 (+0.028) ; skew_idx=-0.25 (-0.010) ; sector_rs=0.09 (-0.008) ; slope_r2_20d=0.88 (-0.006) ; vxn_squeeze_vel=-1.22 (-0.004)` |
| GOOGL | HIGH | 56.6 | $18,435.56 | 2025-11-25 | 2025-12-31 | 25 | $325.59 | $312.17 | $292.61 | -4.12% | -760 | -0.41R | Time Stop 25D | 42.4% | 1.35x | `resid_mom_60=0.33 (+0.059) ; sector_rs=-0.03 (+0.034) ; resid_mom_20=0.19 (+0.011) ; vix_ts=0.94 (-0.007) ; slope_r2_20d=0.50 (-0.007)` |
| APP | HIGH | 3.9 | $2,861.08 | 2025-12-24 | 2026-01-02 | 6 | $728.36 | $628.82 | $629.26 | -13.67% | -391 | -1.00R | Stop | 39.7% | 1.24x | `vix_ts=0.78 (-0.064) ; skew_idx=2.44 (+0.031) ; rs_rank=1.00 (+0.026) ; resid_mom_20=0.21 (+0.009) ; slope_r2_20d=0.60 (-0.008)` |
| LRCX | LOW | 13.8 | $2,627.08 | 2026-01-05 | 2026-03-06 | 43 | $189.69 | $198.84 | $170.24 | +8.58% | +225 | +0.84R | Trail Stop Eod | 24.4% | 0.53x | `skew_idx=-0.98 (-0.065) ; vix_ts=0.81 (-0.041) ; vxn_squeeze_vel=0.75 (-0.034) ; slope_r2_20d=0.62 (-0.005) ; resid_mom_20=0.11 (+0.003)` |
| MU | HIGH | 59.4 | $17,527.43 | 2026-01-02 | 2026-03-30 | 60 | $295.12 | $321.47 | $254.16 | +13.04% | +2,285 | +0.94R | Trail Stop Eod | 46.9% | 1.45x | `rs_rank=0.98 (+0.033) ; vxn_squeeze_vel=0.62 (+0.032) ; resid_mom_60=0.33 (+0.027) ; sector_rs=0.00 (+0.014) ; slope_r2_20d=0.64 (-0.011)` |
| WDC | MEDIUM | 62.7 | $2,939.56 | 2025-05-13 | 2026-07-07 | 288 | $46.85 | $531.86 | $41.29 | +781.78% | +22,981 | +65.85R | Stop Gap | 35.5% | 1.01x | `vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.012) ; skew_idx=-0.25 (-0.010) ; rs_rank=0.96 (+0.010) ; slope_r2_20d=0.91 (-0.006)` |
| LITE | HIGH | 97.2 | $12,869.22 | 2025-09-03 | 2026-07-07 | 211 | $132.43 | $698.93 | $115.52 | +326.65% | +42,038 | +25.58R | Stop Gap | 42.7% | 1.37x | `resid_mom_60=0.29 (+0.077) ; ema50_slope=1.93 (-0.009) ; vxn_squeeze_vel=0.58 (+0.008) ; slope_r2_20d=0.79 (-0.008) ; sector_rs=-0.03 (+0.008)` |
| ARM | HIGH | 108.3 | $16,738.03 | 2026-04-01 | 2026-07-14 | 71 | $154.50 | $280.97 | $131.32 | +69.41% | +11,618 | +4.63R | Trail Stop Eod | 43.6% | 1.38x | `vix_ts=0.99 (+0.031) ; rs_rank=0.98 (+0.027) ; slope_r2_20d=0.73 (-0.011) ; skew_idx=0.04 (-0.008) ; slope_t_norm_10d=4.87 (+0.007)` |
| META | HIGH | 64.2 | $41,874.98 | 2026-07-14 | 2026-07-27 | 10 | $651.94 | $592.99 | $573.96 | -9.04% | -3,787 | -0.76R | Earnings Exit | 41.6% | 1.33x | `rs_rank=0.96 (+0.018) ; sector_rs=-0.06 (+0.012) ; vxn_squeeze_vel=0.12 (+0.006) ; vol_compress=1.43 (-0.004) ; slope_t_norm_10d=11.76 (-0.002)` |
| ANET | MEDIUM | 125.1 | $23,031.04 | 2026-07-15 | 2026-08-03 | 14 | $184.13 | $184.76 | $156.51 | +0.34% | +79 | +0.02R | Earnings Exit | 37.9% | 1.09x | `sector_rs=-0.05 (+0.015) ; vix_ts=0.85 (-0.006) ; vxn_squeeze_vel=-0.62 (-0.006) ; skew_idx=0.75 (-0.005) ; rs_rank=0.94 (+0.004)` |
| AAPL | MEDIUM | 125.9 | $39,623.43 | 2026-07-10 | 2026-08-13 | 25 | $314.67 | $305.05 | $289.65 | -3.06% | -1,212 | -0.38R | Time Stop 25D | 35.7% | 0.93x | `vix_ts=0.83 (-0.015) ; rs_rank=0.82 (+0.006) ; vxn_squeeze_vel=-0.33 (-0.004) ; slope_t_norm_10d=16.30 (-0.004) ; skew_idx=0.70 (-0.003)` |
| AMZN | MEDIUM | 124.8 | $35,168.42 | 2026-08-05 | 2026-08-20 | 12 | $281.79 | $259.93 | $252.32 | -7.76% | -2,728 | -0.74R | Time Stop 12D | 36.8% | 1.00x | `vxn_squeeze_vel=-1.14 (+0.061) ; sector_rs=-0.04 (+0.048) ; slope_t_norm_40d=0.85 (+0.024) ; slope_accel=0.48 (+0.015) ; skew_idx=-3.40 (-0.012)` |
| MRVL | HIGH | 182.5 | $46,090.61 | 2026-08-21 | 2026-08-25 | 3 | $252.51 | $240.16 | $214.63 | -4.89% | -2,255 | -0.33R | Earnings Exit | 47.0% | 1.46x | `resid_mom_60=0.29 (+0.043) ; vxn_squeeze_vel=0.67 (+0.036) ; slope_t_norm_40d=-1.45 (-0.029) ; sector_rs=-0.06 (+0.023) ; skew_idx=0.06 (-0.009)` |
| PLTR | MEDIUM | 152.2 | $23,742.61 | 2026-08-06 | 2026-09-10 | 25 | $155.98 | $165.74 | $132.58 | +6.26% | +1,486 | +0.42R | Time Stop 25D | 36.5% | 0.98x | `skew_idx=-1.91 (-0.053) ; vxn_squeeze_vel=-2.33 (+0.052) ; sector_rs=-0.07 (+0.041) ; slope_t_norm_40d=0.83 (+0.025) ; slope_accel=0.34 (+0.017)` |
| ORCL | LOW | 120.9 | $18,782.32 | 2026-08-14 | 2026-09-10 | 19 | $155.37 | $152.27 | $132.74 | -2.00% | -375 | -0.14R | Earnings Exit | 33.0% | 0.73x | `vix_ts=0.79 (-0.023) ; sector_rs=-0.00 (+0.018) ; skew_idx=-1.48 (-0.016) ; slope_t_norm_40d=-1.24 (+0.014) ; vxn_squeeze_vel=-0.96 (+0.008)` |
| SNDK | MEDIUM | 16.5 | $23,980.35 | 2026-08-26 | 2026-10-12 | 33 | $1456.59 | $1486.29 | $1238.10 | +2.04% | +489 | +0.14R | Time Stop 25D | 37.2% | 1.03x | `skew_idx=0.04 (-0.011) ; vix_ts=0.85 (-0.005) ; ema20_slope=0.20 (+0.004) ; vxn_squeeze_vel=-0.28 (+0.004) ; rs_rank=0.90 (+0.002)` |
| MU | HIGH | 41.3 | $41,066.49 | 2026-09-11 | 2026-10-15 | 25 | $993.74 | $930.59 | $844.68 | -6.35% | -2,610 | -0.42R | Time Stop 25D | 40.0% | 1.24x | `rs_rank=0.98 (+0.020) ; skew_idx=0.54 (-0.013) ; vix_ts=0.90 (-0.008) ; sector_rs=-0.02 (-0.005) ; vxn_squeeze_vel=1.06 (+0.005)` |
