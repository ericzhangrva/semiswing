# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2402` -> Calibrated `0.2402` (Brier Skill Score: `0.0393`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.79 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.964 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.74 ; OOS: 3.50 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 35.0% (vs SMH 35.7%)` | 35.50% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.50% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.44 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -19.8% ; DD: 20.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.01 ; Sortino Lift: +0.05 ; CAGR Lift: +5.2% ; DD Red: -5.1% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.962 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.82 ; OOS: 3.55 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.88% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.88% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.41 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.9% ; DD: 20.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.07 ; Sortino Lift: +0.11 ; CAGR Lift: +11.1% ; DD Red: -5.1% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 840.8 | 59.93 | 1.42 | 0.923 | 1.46 | 30.38 | 25.8 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 949.63 | 63.64 | 1.44 | 0.93 | 1.52 | 35.5 | 25.8 | 91 | 47.3 | 3.5 | 1.66 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 371.27 | 38.37 | 1.02 | 0.713 | 1.03 | 37.84 | 27.4 | 87 | 54.0 | 3.19 | 1.2 |
| `Baseline (Adaptive `L_t`)` | 623.67 | 51.37 | 1.33 | 0.894 | 1.4 | 30.79 | 25.8 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 813.14 | 58.93 | 1.41 | 0.923 | 1.51 | 35.88 | 25.8 | 91 | 47.3 | 3.55 | 1.66 |
| Pure Pre-2022 Semi (Cash Swing) | 288.51 | 32.88 | 0.96 | 0.663 | 0.99 | 35.52 | 27.4 | 88 | 53.4 | 3.14 | 1.18 |
| Baseline (Fixed 20d) | 655.02 | 52.73 | 1.32 | 0.887 | 1.39 | 34.9 | 25.9 | 96 | 45.8 | 3.79 | 1.64 |
| SMH Buy & Hold | 256.95 | 30.54 | 0.8 | 0.53 | 0.79 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 182.83 | 24.33 | 0.65 | 0.403 | 0.65 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 115.11 | 17.4 | 0.59 | 0.354 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 84.34 | 13.67 | 0.5 | 0.281 | 0.49 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 99.88 | 15.61 | 0.53 | 0.303 | 0.52 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 35.16 | 6.51 | 0.23 | 0.12 | 0.22 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 71.24 | 11.93 | 0.51 | 0.289 | 0.5 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.9 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -19.79 | -19.86 | -2.54 | 0.0 | -2.03 | 20.01 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -19.89 | -19.96 | -2.56 | 0.0 | -2.04 | 20.11 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
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
| Baseline (SMH Bull Core + Swing) | 1083.41 | 92.34 | 1.78 | 0.961 | 1.79 | 30.38 | 8.9 | 78 | 60.3 | 3.59 | 1.98 |
| ML (SMH Bull Core + Swing) | 1208.41 | 97.52 | 1.79 | 0.964 | 1.84 | 35.5 | 8.9 | 74 | 58.1 | 3.74 | 2.18 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 496.97 | 60.47 | 1.34 | 0.823 | 1.33 | 37.84 | 11.0 | 73 | 64.4 | 3.71 | 1.56 |
| `Baseline (Adaptive `L_t`)` | 808.1 | 79.32 | 1.69 | 0.948 | 1.74 | 30.79 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 1039.71 | 90.43 | 1.76 | 0.962 | 1.85 | 35.88 | 8.9 | 74 | 58.1 | 3.82 | 2.18 |
| Pure Pre-2022 Semi (Cash Swing) | 390.95 | 52.38 | 1.28 | 0.793 | 1.31 | 35.52 | 11.0 | 74 | 63.5 | 3.75 | 1.53 |
| Baseline (Fixed 20d) | 795.68 | 78.67 | 1.63 | 0.931 | 1.68 | 34.9 | 9.2 | 83 | 53.0 | 4.11 | 1.99 |
| SMH Buy & Hold | 453.12 | 57.26 | 1.33 | 0.819 | 1.31 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 348.73 | 48.79 | 1.12 | 0.695 | 1.11 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 211.51 | 35.09 | 1.2 | 0.747 | 1.15 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 177.91 | 31.07 | 1.23 | 0.765 | 1.21 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 215.23 | 35.52 | 1.19 | 0.741 | 1.16 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 107.22 | 21.27 | 0.7 | 0.379 | 0.69 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 111.38 | 21.91 | 1.11 | 0.688 | 1.1 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.47 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.52% | +125.28% | 53.9% | 1.72 | 1.71 | -30.79% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.89% | -19.96% | 9.4% | -2.56 | -2.04 | -20.11% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +43.96% | +44.38% | 20.5% | 1.66 | 1.72 | -19.40% | 6.0% | 25 | 68.0% | 4.08 | +0.89R |
| 2024 | +85.63% | +85.63% | 31.4% | 1.98 | 2.20 | -23.38% | 7.5% | 22 | 59.1% | 5.25 | +1.18R |
| 2025 | +134.32% | +135.92% | 35.2% | 2.51 | 2.84 | -18.84% | 20.4% | 12 | 58.3% | 33.30 | +8.39R |
| 2026 | +75.69% | +103.42% | 60.1% | 1.43 | 1.44 | -35.88% | 0.0% | 15 | 40.0% | 1.16 | +0.81R |

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
| META | MEDIUM | 1 | $664.75 | 2025-01-31 | 2025-02-28 | 20 | $687.54 | $663.92 | $627.77 | -3.43% | -23 | -0.40R | Regime Off | 33.8% | 0.86x | `sector_rs=-0.03 (-0.012) ; resid_mom_60=0.19 (-0.011) ; slope_accel=0.72 (+0.010) ; slope_r2_20d=0.71 (-0.010) ; skew_idx=-0.52 (-0.007)` |
| INTC | HIGH | 312.3 | $7,672.15 | 2025-02-24 | 2025-02-28 | 5 | $24.57 | $23.71 | $20.88 | -3.48% | -267 | -0.23R | Regime Off | 38.3% | 1.17x | `vxn_squeeze_vel=0.92 (-0.033) ; sector_rs=-0.05 (+0.028) ; slope_accel=0.63 (+0.016) ; vol_compress=1.77 (+0.013) ; vix_ts=0.93 (-0.004)` |
| CEG | MEDIUM | 9.1 | $2,533.44 | 2025-05-13 | 2025-09-02 | 77 | $278.39 | $298.61 | $237.89 | +12.09% | +306 | +0.83R | Stop Gap | 35.7% | 1.04x | `vix_ts=0.91 (+0.022) ; skew_idx=-0.25 (-0.011) ; slope_r2_20d=0.89 (-0.009) ; slope_sharpe=6.83 (-0.004) ; vol_compress=0.80 (-0.003)` |
| STX | HIGH | 47.4 | $4,766.00 | 2025-05-13 | 2025-10-10 | 105 | $100.52 | $212.97 | $89.16 | +89.06% | +4,245 | +7.88R | Trail Stop Eod | 38.3% | 1.22x | `vix_ts=0.91 (+0.022) ; skew_idx=-0.25 (-0.010) ; rs_rank=0.98 (+0.008) ; slope_r2=0.93 (+0.004) ; slope_r2_20d=0.95 (-0.003)` |
| AMD | MEDIUM | 30.2 | $6,656.51 | 2025-10-13 | 2025-11-18 | 27 | $220.35 | $230.13 | $187.30 | +4.44% | +295 | +0.30R | Time Stop 25D | 34.2% | 0.85x | `skew_idx=-2.34 (-0.126) ; sector_rs=0.07 (+0.072) ; slope_t_norm_40d=1.22 (+0.038) ; vix_ts=0.95 (+0.019) ; slope_accel=0.75 (+0.015)` |
| VRT | MEDIUM | 24.1 | $2,428.50 | 2025-05-13 | 2025-12-17 | 152 | $100.97 | $149.62 | $85.82 | +43.88% | +1,066 | +2.93R | Trail Stop Eod | 35.6% | 1.02x | `vix_ts=0.91 (+0.021) ; skew_idx=-0.25 (-0.011) ; slope_r2_20d=0.88 (-0.007) ; vol_compress=0.61 (-0.005) ; slope_sharpe=7.39 (-0.004)` |
| GOOGL | HIGH | 60.8 | $19,807.13 | 2025-11-25 | 2025-12-31 | 25 | $325.59 | $312.17 | $292.61 | -4.12% | -816 | -0.41R | Time Stop 25D | 41.6% | 1.33x | `resid_mom_60=0.33 (+0.059) ; sector_rs=-0.03 (+0.020) ; resid_mom_20=0.19 (+0.008) ; slope_t_norm_40d=8.84 (+0.007) ; slope_r2_20d=0.50 (-0.006)` |
| APP | HIGH | 4.2 | $3,082.07 | 2025-12-24 | 2026-01-02 | 6 | $728.36 | $628.82 | $629.26 | -13.67% | -421 | -1.00R | Stop | 39.1% | 1.21x | `vix_ts=0.78 (-0.080) ; skew_idx=2.44 (+0.038) ; rs_rank=1.00 (+0.020) ; slope_r2_20d=0.60 (-0.008) ; ext_atr=1.63 (+0.004)` |
| LRCX | LOW | 14.9 | $2,829.47 | 2026-01-05 | 2026-03-06 | 43 | $189.69 | $198.84 | $170.24 | +8.58% | +243 | +0.84R | Trail Stop Eod | 24.8% | 0.54x | `skew_idx=-0.98 (-0.061) ; vxn_squeeze_vel=0.75 (-0.040) ; vix_ts=0.81 (-0.034) ; slope_r2_20d=0.62 (-0.005) ; resid_mom_20=0.11 (+0.003)` |
| MU | HIGH | 63.8 | $18,831.51 | 2026-01-02 | 2026-03-30 | 60 | $295.12 | $321.47 | $254.16 | +13.04% | +2,455 | +0.94R | Trail Stop Eod | 44.4% | 1.41x | `rs_rank=0.98 (+0.028) ; resid_mom_60=0.33 (+0.026) ; vxn_squeeze_vel=0.62 (+0.025) ; slope_r2_20d=0.64 (-0.010) ; sector_rs=0.00 (+0.007)` |
| WDC | MEDIUM | 65.3 | $3,058.75 | 2025-05-13 | 2026-07-07 | 288 | $46.85 | $531.86 | $41.29 | +781.78% | +23,913 | +65.85R | Stop Gap | 35.5% | 1.02x | `vix_ts=0.91 (+0.021) ; skew_idx=-0.25 (-0.010) ; slope_r2_20d=0.91 (-0.010) ; vol_compress=0.65 (-0.005) ; slope_sharpe=9.08 (-0.004)` |
| LITE | HIGH | 93 | $12,310.76 | 2025-09-03 | 2026-07-07 | 211 | $132.43 | $698.93 | $115.52 | +326.65% | +40,214 | +25.58R | Stop Gap | 39.3% | 1.26x | `resid_mom_60=0.29 (+0.047) ; vix_ts=0.89 (+0.011) ; ema50_slope=1.93 (-0.008) ; slope_t_norm_40d=12.28 (+0.006) ; slope_r2_20d=0.79 (-0.003)` |
| ARM | HIGH | 106.8 | $16,506.09 | 2026-04-01 | 2026-07-14 | 71 | $154.50 | $280.97 | $131.32 | +69.41% | +11,457 | +4.63R | Trail Stop Eod | 42.6% | 1.36x | `vix_ts=0.99 (+0.034) ; rs_rank=0.98 (+0.030) ; slope_r2_20d=0.73 (-0.016) ; resid_mom_20=0.23 (+0.006) ; slope_t_norm=6.62 (+0.006)` |
| P | HIGH | 610.4 | $48,747.21 | 2026-07-09 | 2026-07-15 | 5 | $79.87 | $67.84 | $67.89 | -15.06% | -7,341 | -1.00R | Stop | 45.3% | 1.43x | `skew_idx=1.86 (+0.046) ; vxn_squeeze_vel=0.21 (+0.028) ; sector_rs=-0.02 (+0.013) ; rs_rank=0.80 (+0.006) ; slope_accel=0.33 (+0.003)` |
| META | HIGH | 34.1 | $22,624.54 | 2026-07-15 | 2026-07-27 | 9 | $663.54 | $592.99 | $587.40 | -10.63% | -2,406 | -0.93R | Earnings Exit | 39.6% | 1.22x | `rs_rank=0.98 (+0.021) ; sector_rs=-0.05 (+0.017) ; vix_ts=0.85 (-0.006) ; slope_t_norm_10d=10.63 (-0.004) ; skew_idx=0.75 (-0.004)` |
| AMZN | MEDIUM | 156 | $38,825.98 | 2026-07-20 | 2026-07-28 | 7 | $248.93 | $230.70 | $226.16 | -7.33% | -2,844 | -0.80R | Earnings Exit | 37.9% | 1.10x | `skew_idx=1.15 (-0.022) ; sector_rs=-0.11 (-0.019) ; vxn_squeeze_vel=1.39 (+0.014) ; slope_t_norm_40d=-2.14 (+0.012) ; vix_ts=0.91 (+0.004)` |
| AAPL | MEDIUM | 108.1 | $34,011.34 | 2026-07-10 | 2026-08-13 | 25 | $314.67 | $305.05 | $289.65 | -3.06% | -1,040 | -0.38R | Time Stop 25D | 36.1% | 0.97x | `vix_ts=0.83 (-0.015) ; rs_rank=0.80 (+0.009) ; vxn_squeeze_vel=-0.33 (-0.004) ; vol_compress=1.66 (+0.003) ; resid_mom_60=0.13 (-0.002)` |
| AMZN | MEDIUM | 113.2 | $31,899.19 | 2026-08-05 | 2026-08-20 | 12 | $281.79 | $259.93 | $252.32 | -7.76% | -2,475 | -0.74R | Time Stop 12D | 36.3% | 0.96x | `sector_rs=-0.04 (+0.046) ; vxn_squeeze_vel=-1.14 (+0.038) ; slope_t_norm_40d=0.85 (+0.030) ; slope_accel=0.48 (+0.026) ; ema50_slope=0.08 (+0.023)` |
| P | HIGH | 401.9 | $44,639.64 | 2026-08-21 | 2026-08-24 | 2 | $111.08 | $100.37 | $94.76 | -9.64% | -4,303 | -0.66R | Earnings Exit | 48.6% | 1.47x | `sector_rs=-0.06 (+0.028) ; resid_mom_60=0.27 (+0.025) ; vxn_squeeze_vel=0.67 (+0.024) ; ema20_slope=2.29 (+0.021) ; rs_rank=1.00 (+0.015)` |
| PLTR | MEDIUM | 146.2 | $22,797.92 | 2026-08-06 | 2026-09-10 | 25 | $155.98 | $165.74 | $132.58 | +6.26% | +1,427 | +0.42R | Time Stop 25D | 36.8% | 1.00x | `vxn_squeeze_vel=-2.33 (+0.041) ; skew_idx=-1.91 (-0.039) ; sector_rs=-0.07 (+0.034) ; slope_t_norm_40d=0.83 (+0.031) ; slope_accel=0.34 (+0.018)` |
| ORCL | LOW | 120.2 | $18,672.80 | 2026-08-14 | 2026-09-10 | 19 | $155.37 | $152.27 | $132.74 | -2.00% | -373 | -0.14R | Earnings Exit | 33.8% | 0.77x | `vix_ts=0.79 (-0.027) ; slope_t_norm_40d=-1.24 (+0.019) ; vxn_squeeze_vel=-0.96 (+0.015) ; ema50_slope=-0.19 (+0.010) ; slope_accel=0.47 (+0.010)` |
| SNDK | MEDIUM | 15.6 | $23,923.19 | 2026-08-25 | 2026-10-08 | 32 | $1534.76 | $1608.33 | $1304.55 | +4.79% | +1,147 | +0.32R | Time Stop 25D | 38.1% | 1.11x | `vxn_squeeze_vel=0.38 (+0.015) ; sector_rs=-0.04 (-0.008) ; ema20_slope=0.32 (+0.003) ; vix_ts=0.85 (-0.003) ; rs_rank=0.86 (+0.002)` |
| MU | HIGH | 40 | $39,747.85 | 2026-09-11 | 2026-10-15 | 25 | $993.74 | $930.59 | $844.68 | -6.35% | -2,526 | -0.42R | Time Stop 25D | 41.2% | 1.31x | `rs_rank=0.98 (+0.031) ; skew_idx=0.54 (-0.011) ; vxn_squeeze_vel=1.06 (+0.009) ; vol_compress=0.54 (+0.008) ; slope_r2_20d=0.11 (+0.003)` |
| DELL | HIGH | 60.3 | $8,744.93 | 2026-03-11 | 2026-10-16 | 153 | $145.07 | $451.39 | $123.31 | +165.23% | +14,449 | +11.02R | Trail Stop Eod | 40.7% | 1.28x | `rs_rank=0.98 (+0.025) ; slope_r2_20d=0.66 (-0.016) ; vix_ts=0.98 (+0.012) ; skew_idx=1.02 (-0.008) ; sector_rs=0.00 (+0.006)` |
| SNPS | MEDIUM | 49.1 | $25,073.46 | 2026-10-09 | 2026-10-16 | 6 | $510.84 | $454.03 | $454.35 | -11.12% | -2,788 | -1.01R | Stop | 38.5% | 1.15x | `vix_ts=0.85 (-0.019) ; rs_rank=0.98 (+0.015) ; slope_r2_20d=0.87 (-0.006) ; sector_rs=0.06 (+0.005) ; resid_mom_60=0.15 (-0.005)` |
