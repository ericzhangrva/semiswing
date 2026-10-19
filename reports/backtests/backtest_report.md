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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.86 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.974 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 5.23 ; OOS: 4.67 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 35.0% (vs SMH 35.7%)` | 33.70% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 37.97% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.36 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -37.9% ; DD: 38.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or DD Red >= 1.5%)` | BSS: 0.0384 ; ML SR: 1.86 vs Base: 1.80 (Lift: +0.06, DD Red: +2.0%) | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.73 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.954 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 5.45 ; OOS: 4.79 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.52% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.52% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.36 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -22.5% ; DD: 22.7% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or DD Red >= 1.5%)` | BSS: 0.0384 ; ML SR: 1.73 vs Base: 1.62 (Lift: +0.11, DD Red: +1.5%) | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 767.45 | 57.29 | 1.3 | 0.872 | 1.31 | 37.77 | 25.8 | 89 | 52.8 | 4.15 | 1.54 |
| ML (SMH Bull Core + Swing) | 905.19 | 62.23 | 1.36 | 0.902 | 1.42 | 37.97 | 25.8 | 88 | 47.7 | 4.67 | 1.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 458.03 | 43.4 | 1.08 | 0.753 | 1.1 | 38.67 | 27.5 | 86 | 54.7 | 3.19 | 1.22 |
| `Baseline (Adaptive `L_t`)` | 599.27 | 50.34 | 1.26 | 0.857 | 1.28 | 37.06 | 25.8 | 88 | 52.3 | 4.15 | 1.51 |
| ML (LightGBM + Platt) | 779.94 | 57.76 | 1.36 | 0.904 | 1.44 | 35.52 | 25.8 | 88 | 47.7 | 4.79 | 1.6 |
| Pure Pre-2022 Semi (Cash Swing) | 326.01 | 35.51 | 1.0 | 0.698 | 1.04 | 35.76 | 27.5 | 87 | 54.0 | 3.25 | 1.2 |
| Baseline (Fixed 20d) | 585.44 | 49.71 | 1.24 | 0.852 | 1.31 | 34.97 | 26.1 | 96 | 45.8 | 3.35 | 1.64 |
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
| Baseline (SMH Bull Core + Swing) | -37.67 | -37.78 | -3.3 | 0.0 | -2.52 | 37.77 | 89.6 | 14 | 0.0 | 0.0 | -0.64 |
| ML (SMH Bull Core + Swing) | -37.86 | -37.98 | -3.24 | 0.0 | -2.47 | 37.97 | 89.6 | 16 | 0.0 | 0.0 | -0.66 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -38.25 | -38.37 | -3.36 | 0.0 | -2.57 | 38.36 | 89.6 | 13 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -22.13 | -22.21 | -2.68 | 0.0 | -2.08 | 22.39 | 89.6 | 14 | 0.0 | 0.0 | -0.64 |
| ML (LightGBM + Platt) | -22.46 | -22.54 | -2.64 | 0.0 | -2.06 | 22.67 | 89.6 | 16 | 0.0 | 0.0 | -0.66 |
| Pure Pre-2022 Semi (Cash Swing) | -21.94 | -22.02 | -2.67 | 0.0 | -2.08 | 22.2 | 89.6 | 13 | 0.0 | 0.0 | -0.68 |
| Baseline (Fixed 20d) | -16.16 | -16.22 | -2.51 | 0.0 | -2.01 | 16.44 | 88.8 | 13 | 0.0 | 0.0 | -0.56 |
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
| Baseline (SMH Bull Core + Swing) | 1291.37 | 100.91 | 1.8 | 0.961 | 1.78 | 35.68 | 8.9 | 75 | 62.7 | 4.65 | 1.95 |
| ML (SMH Bull Core + Swing) | 1517.44 | 109.08 | 1.86 | 0.974 | 1.93 | 33.7 | 8.9 | 72 | 58.3 | 5.23 | 2.1 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 803.58 | 79.19 | 1.57 | 0.913 | 1.58 | 36.23 | 11.0 | 73 | 64.4 | 3.69 | 1.56 |
| `Baseline (Adaptive `L_t`)` | 797.83 | 78.89 | 1.62 | 0.925 | 1.61 | 37.06 | 8.9 | 74 | 62.2 | 4.77 | 1.92 |
| ML (LightGBM + Platt) | 1034.59 | 90.33 | 1.73 | 0.954 | 1.79 | 35.52 | 8.9 | 72 | 58.3 | 5.45 | 2.1 |
| Pure Pre-2022 Semi (Cash Swing) | 445.66 | 56.77 | 1.34 | 0.823 | 1.37 | 35.76 | 11.0 | 74 | 63.5 | 3.91 | 1.53 |
| Baseline (Fixed 20d) | 717.46 | 74.5 | 1.54 | 0.906 | 1.6 | 34.97 | 9.6 | 83 | 53.0 | 3.62 | 1.98 |
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
| 2022 | -22.13% | -22.21% | N/A | -2.68 | -2.08 | -22.39% | 89.6% | 14 | 0.0% | 0.00 | -0.64R |
| 2023 | +40.11% | +40.49% | N/A | 1.52 | 1.57 | -19.99% | 6.0% | 24 | 70.8% | 3.60 | +1.04R |
| 2024 | +87.36% | +87.36% | N/A | 1.95 | 2.15 | -21.91% | 7.5% | 22 | 63.6% | 4.82 | +1.25R |
| 2025 | +75.61% | +76.40% | N/A | 1.78 | 1.77 | -16.46% | 20.4% | 16 | 50.0% | 9.76 | +5.31R |
| 2026 | +88.09% | +122.56% | N/A | 1.60 | 1.50 | -37.06% | 0.0% | 12 | 58.3% | 1.65 | +0.40R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -22.46% | -22.54% | N/A | -2.64 | -2.06 | -22.67% | 89.6% | 16 | 0.0% | 0.00 | -0.66R |
| 2023 | +47.55% | +48.01% | N/A | 1.75 | 1.85 | -19.27% | 6.0% | 25 | 68.0% | 4.37 | +0.89R |
| 2024 | +80.05% | +80.05% | N/A | 1.83 | 2.02 | -24.46% | 7.5% | 23 | 52.2% | 4.13 | +1.05R |
| 2025 | +133.95% | +135.55% | N/A | 2.44 | 2.68 | -18.80% | 20.4% | 12 | 58.3% | 35.06 | +8.39R |
| 2026 | +76.09% | +104.72% | N/A | 1.42 | 1.42 | -35.52% | 0.0% | 12 | 50.0% | 1.15 | +0.35R |

## 8. Recent 25 OOS Trades (ML (SMH Bull Core + Swing))

> **Section 8 Trade Blotter Legend & Quantitative Diagnostics**
> - **Tier:** `CONSENSUS` (dual-engine alignment, 1.0% risk), `HIGH` (standalone ML top-quintile RS, 1.0% risk), `MEDIUM` (conservative 0.75% risk).
> - **Win Prob:** Platt-calibrated out-of-fold probability $P(\text{TP1 before Stop})$. Break-even threshold is $> 40.0\%$ with a 1.5:1 payoff ratio.
> - **Sizing Scalar:** Meta-labeling sizing multiplier $S_{i,t} = 0.50 + \text{Rank}_{\text{OOF}}(\hat{p}) \in [0.50, 1.50]$ scaling allocation by model confidence.
> - **Top Model Drivers (SHAP):** Single-feature marginal attributions detailing `sector_rs` (20d RS vs SMH), `vix_ts` (VIX/VIX3M contango), `skew_idx` (tail-risk hedging), `resid_mom_60` (beta-neutral momentum), `vol_compress` (volatility squeeze), and `slope_r2_20d` (trend smoothness).

| Ticker | Tier | Entry Date | Exit Date | Days Held | Entry ($) | Exit ($) | Initial Stop ($) | Return (%) | Net P&L ($) | R-Multiple | Exit Reason | Win Prob | Sizing Scalar | Top Model Drivers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PLTR | HIGH | 2024-09-20 | 2025-02-24 | 106 | $36.04 | $95.81 | $31.91 | +129.64% | +6,794 | +11.33R | Stop Gap | 41.1% | 1.27x | `sector_rs=-0.06 (-0.050) ; skew_idx=2.90 (-0.043) ; resid_mom_60=0.45 (+0.031) ; ema20_slope=1.50 (-0.011) ; ema50_slope=2.06 (-0.011)` |
| LRCX | MEDIUM | 2025-02-24 | 2025-02-27 | 4 | $85.47 | $76.16 | $76.21 | -10.90% | -443 | -1.01R | Stop | 35.5% | 0.98x | `sector_rs=-0.05 (+0.029) ; vxn_squeeze_vel=0.92 (-0.025) ; vix_ts=0.93 (-0.009) ; slope_r2_20d=0.77 (-0.008) ; resid_mom_60=0.13 (+0.007)` |
| STX | MEDIUM | 2025-01-31 | 2025-02-28 | 20 | $95.99 | $99.58 | $85.96 | +3.74% | +213 | +0.36R | Regime Off | 36.6% | 1.06x | `vol_compress=1.65 (+0.010) ; vix_ts=0.88 (+0.009) ; sector_rs=-0.03 (-0.009) ; skew_idx=-0.52 (-0.006) ; vxn_squeeze_vel=0.49 (-0.004)` |
| META | MEDIUM | 2025-01-31 | 2025-02-28 | 20 | $687.54 | $663.92 | $627.77 | -3.43% | -145 | -0.40R | Regime Off | 34.6% | 0.91x | `sector_rs=-0.03 (-0.009) ; vix_ts=0.88 (+0.008) ; slope_r2_20d=0.71 (-0.007) ; skew_idx=-0.52 (-0.006) ; resid_mom_60=0.19 (-0.006)` |
| INTC | HIGH | 2025-02-24 | 2025-02-28 | 5 | $24.57 | $23.71 | $20.88 | -3.48% | -222 | -0.23R | Regime Off | 38.2% | 1.17x | `sector_rs=-0.05 (+0.030) ; vxn_squeeze_vel=0.92 (-0.030) ; rs_rank=0.96 (+0.010) ; vol_compress=1.77 (+0.009) ; vix_ts=0.93 (-0.008)` |
| CEG | MEDIUM | 2025-05-13 | 2025-09-02 | 77 | $278.39 | $298.61 | $237.89 | +12.09% | +258 | +0.83R | Stop Gap | 35.4% | 1.00x | `vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.011) ; skew_idx=-0.25 (-0.010) ; slope_r2_20d=0.89 (-0.006) ; rs_rank=0.86 (+0.005)` |
| STX | HIGH | 2025-05-13 | 2025-10-10 | 105 | $100.52 | $212.97 | $89.16 | +89.06% | +3,524 | +7.88R | Trail Stop Eod | 37.5% | 1.16x | `vix_ts=0.91 (+0.029) ; sector_rs=0.09 (-0.011) ; skew_idx=-0.25 (-0.011) ; slope_r2_20d=0.95 (+0.010) ; rs_rank=0.98 (+0.010)` |
| AMD | LOW | 2025-10-13 | 2025-11-18 | 27 | $220.35 | $230.13 | $187.30 | +4.44% | +234 | +0.30R | Time Stop 25D | 32.8% | 0.75x | `skew_idx=-2.34 (-0.130) ; sector_rs=0.07 (+0.078) ; slope_accel=0.75 (+0.037) ; vix_ts=0.95 (+0.028) ; slope_t_norm_40d=1.22 (+0.019)` |
| VRT | MEDIUM | 2025-05-13 | 2025-12-17 | 152 | $100.97 | $149.62 | $85.82 | +43.88% | +889 | +2.93R | Trail Stop Eod | 35.1% | 0.98x | `vix_ts=0.91 (+0.028) ; skew_idx=-0.25 (-0.010) ; sector_rs=0.09 (-0.008) ; slope_r2_20d=0.88 (-0.006) ; vxn_squeeze_vel=-1.22 (-0.004)` |
| GOOGL | HIGH | 2025-11-25 | 2025-12-31 | 25 | $325.59 | $312.17 | $292.61 | -4.12% | -700 | -0.41R | Time Stop 25D | 42.4% | 1.35x | `resid_mom_60=0.33 (+0.059) ; sector_rs=-0.03 (+0.034) ; resid_mom_20=0.19 (+0.011) ; vix_ts=0.94 (-0.007) ; slope_r2_20d=0.50 (-0.007)` |
| APP | HIGH | 2025-12-24 | 2026-01-02 | 6 | $728.36 | $628.82 | $629.26 | -13.67% | -353 | -1.00R | Stop | 39.7% | 1.24x | `vix_ts=0.78 (-0.064) ; skew_idx=2.44 (+0.031) ; rs_rank=1.00 (+0.026) ; resid_mom_20=0.21 (+0.009) ; slope_r2_20d=0.60 (-0.008)` |
| LRCX | LOW | 2026-01-05 | 2026-03-06 | 43 | $189.69 | $198.84 | $170.24 | +8.58% | +206 | +0.84R | Trail Stop Eod | 24.4% | 0.53x | `skew_idx=-0.98 (-0.065) ; vix_ts=0.81 (-0.041) ; vxn_squeeze_vel=0.75 (-0.034) ; slope_r2_20d=0.62 (-0.005) ; resid_mom_20=0.11 (+0.003)` |
| MU | HIGH | 2026-01-02 | 2026-03-30 | 60 | $295.12 | $321.47 | $254.16 | +13.04% | +2,182 | +0.94R | Trail Stop Eod | 46.9% | 1.45x | `rs_rank=0.98 (+0.033) ; vxn_squeeze_vel=0.62 (+0.032) ; resid_mom_60=0.33 (+0.027) ; sector_rs=0.00 (+0.014) ; slope_r2_20d=0.64 (-0.011)` |
| WDC | MEDIUM | 2025-05-13 | 2026-07-07 | 288 | $46.85 | $531.86 | $41.29 | +781.78% | +20,652 | +65.85R | Stop Gap | 35.5% | 1.01x | `vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.012) ; skew_idx=-0.25 (-0.010) ; rs_rank=0.96 (+0.010) ; slope_r2_20d=0.91 (-0.006)` |
| LITE | HIGH | 2025-09-03 | 2026-07-07 | 211 | $132.43 | $698.93 | $115.52 | +326.65% | +38,147 | +25.58R | Stop Gap | 42.7% | 1.37x | `resid_mom_60=0.29 (+0.077) ; ema50_slope=1.93 (-0.009) ; vxn_squeeze_vel=0.58 (+0.008) ; slope_r2_20d=0.79 (-0.008) ; sector_rs=-0.03 (+0.008)` |
| ARM | HIGH | 2026-04-01 | 2026-07-14 | 71 | $154.50 | $280.97 | $131.32 | +69.41% | +12,028 | +4.63R | Trail Stop Eod | 43.6% | 1.38x | `vix_ts=0.99 (+0.031) ; rs_rank=0.98 (+0.027) ; slope_r2_20d=0.73 (-0.011) ; skew_idx=0.04 (-0.008) ; slope_t_norm_10d=4.87 (+0.007)` |
| META | HIGH | 2026-07-14 | 2026-07-27 | 10 | $651.94 | $592.99 | $573.96 | -9.04% | -3,611 | -0.76R | Earnings Exit | 41.6% | 1.33x | `rs_rank=0.96 (+0.018) ; sector_rs=-0.06 (+0.012) ; vxn_squeeze_vel=0.12 (+0.006) ; vol_compress=1.43 (-0.004) ; slope_t_norm_10d=11.76 (-0.002)` |
| ANET | MEDIUM | 2026-07-15 | 2026-08-03 | 14 | $184.13 | $184.76 | $156.51 | +0.34% | +80 | +0.02R | Earnings Exit | 37.9% | 1.09x | `sector_rs=-0.05 (+0.015) ; vix_ts=0.85 (-0.006) ; vxn_squeeze_vel=-0.62 (-0.006) ; skew_idx=0.75 (-0.005) ; rs_rank=0.94 (+0.004)` |
| AAPL | MEDIUM | 2026-07-10 | 2026-08-13 | 25 | $314.67 | $305.05 | $289.65 | -3.06% | -1,183 | -0.38R | Time Stop 25D | 35.7% | 0.93x | `vix_ts=0.83 (-0.015) ; rs_rank=0.82 (+0.006) ; vxn_squeeze_vel=-0.33 (-0.004) ; slope_t_norm_10d=16.30 (-0.004) ; skew_idx=0.70 (-0.003)` |
| AMZN | MEDIUM | 2026-08-05 | 2026-08-20 | 12 | $281.79 | $259.93 | $252.32 | -7.76% | -2,657 | -0.74R | Time Stop 12D | 36.8% | 1.00x | `vxn_squeeze_vel=-1.14 (+0.061) ; sector_rs=-0.04 (+0.048) ; slope_t_norm_40d=0.85 (+0.024) ; slope_accel=0.48 (+0.015) ; skew_idx=-3.40 (-0.012)` |
| MRVL | HIGH | 2026-08-21 | 2026-08-25 | 3 | $252.51 | $240.16 | $214.63 | -4.89% | -2,198 | -0.33R | Earnings Exit | 47.0% | 1.46x | `resid_mom_60=0.29 (+0.043) ; vxn_squeeze_vel=0.67 (+0.036) ; slope_t_norm_40d=-1.45 (-0.029) ; sector_rs=-0.06 (+0.023) ; skew_idx=0.06 (-0.009)` |
| PLTR | MEDIUM | 2026-08-06 | 2026-09-10 | 25 | $155.98 | $165.74 | $132.58 | +6.26% | +1,452 | +0.42R | Time Stop 25D | 36.5% | 0.98x | `skew_idx=-1.91 (-0.053) ; vxn_squeeze_vel=-2.33 (+0.052) ; sector_rs=-0.07 (+0.041) ; slope_t_norm_40d=0.83 (+0.025) ; slope_accel=0.34 (+0.017)` |
| ORCL | LOW | 2026-08-14 | 2026-09-10 | 19 | $155.37 | $152.27 | $132.74 | -2.00% | -366 | -0.14R | Earnings Exit | 33.0% | 0.73x | `vix_ts=0.79 (-0.023) ; sector_rs=-0.00 (+0.018) ; skew_idx=-1.48 (-0.016) ; slope_t_norm_40d=-1.24 (+0.014) ; vxn_squeeze_vel=-0.96 (+0.008)` |
| SNDK | MEDIUM | 2026-08-26 | 2026-10-12 | 33 | $1456.59 | $1486.29 | $1238.10 | +2.04% | +477 | +0.14R | Time Stop 25D | 37.2% | 1.03x | `skew_idx=0.04 (-0.011) ; vix_ts=0.85 (-0.005) ; ema20_slope=0.20 (+0.004) ; vxn_squeeze_vel=-0.28 (+0.004) ; rs_rank=0.90 (+0.002)` |
| MU | HIGH | 2026-09-11 | 2026-10-15 | 25 | $993.74 | $930.59 | $844.68 | -6.35% | -2,568 | -0.42R | Time Stop 25D | 40.0% | 1.24x | `rs_rank=0.98 (+0.020) ; skew_idx=0.54 (-0.013) ; vix_ts=0.90 (-0.008) ; sector_rs=-0.02 (-0.005) ; vxn_squeeze_vel=1.06 (+0.005)` |
