# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2404` -> Calibrated `0.2404`

## 1. Visual Benchmark Comparison Charts (`S&P 500`, `QQQ`, `VGT`, `SMH`, `SOXX`, `AIQ`, `IGV`, `T-Bills`)

### 1.1 Full Out-of-Sample Growth of `$10,000` (`2022–2026`, Includes 2022 Bear Market)
![Full OOS Equity Curve](charts/equity_2022_2026.png)

### 1.2 Modern AI Cycle Growth of `$10,000` (`2023–2026`, Rebased Jan 1, 2023)
![Modern AI Cycle Equity Curve](charts/equity_2023_2026_ai_era.png)

### 1.3 Underwater Drawdown Comparison (`2022–2026`)
![Underwater Drawdowns](charts/drawdown_comparison.png)

### 1.4 Calendar Year Returns & Risk-Return Efficiency (`2022–2026`)
![Annual Returns and Risk-Return Scatter](charts/annual_returns_and_risk_scatter.png)

## 2. Validation Gates Summary (§9)

| Gate | Value | Status |
| --- | --- | --- |
| OOS Sharpe >= 1.0 (2022-2026 Overall or 2023-2026 AI Era) | Overall: 1.22 ; AI-Era: 1.59 | PASS |
| Deflated Sharpe Probability >= 0.95 | 0.923 | REVIEW |
| Profit Factor >= 1.50 | Overall: 3.23 ; AI-Era: 3.61 | PASS |
| Max Drawdown <= 25.5% (vs SMH 45.1%) | 38.73% (vs SMH 45.14%) | REVIEW |
| 2022 Bear Stress Gate (DD <= 12% & Cash Days >= 75%) | 2022 DD: 22.67% (SMH: 45.14%) ; Cash: 89.6% | FAIL |
| ML vs Baseline Comparison | ML SR: 1.22 (PF 3.23, DD 38.7%) vs Baseline SR: 1.18 | ENSEMBLE (ML + Baseline) |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 719.34 | 55.42 | 1.24 | 0.843 | 1.23 | 39.12 | 25.8 | 85 | 50.6 | 2.89 | 1.9 |
| ML (SMH Bull Core + Swing) | 599.58 | 50.36 | 1.2 | 0.829 | 1.23 | 37.97 | 26.2 | 91 | 46.2 | 2.57 | 1.68 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 353.46 | 37.29 | 0.94 | 0.652 | 0.96 | 39.77 | 28.1 | 91 | 51.6 | 2.16 | 1.01 |
| Baseline (Adaptive L_t) | 541.51 | 47.65 | 1.18 | 0.811 | 1.17 | 43.4 | 25.8 | 84 | 50.0 | 3.09 | 1.87 |
| ML (LightGBM + Platt) | 512.65 | 46.23 | 1.22 | 0.842 | 1.27 | 38.73 | 26.0 | 90 | 46.7 | 3.23 | 1.71 |
| Pure Pre-2022 Semi (Cash Swing) | 235.21 | 28.86 | 0.83 | 0.556 | 0.86 | 44.02 | 28.1 | 92 | 51.1 | 2.29 | 0.99 |
| Baseline (Fixed 20d) | 571.16 | 49.05 | 1.24 | 0.852 | 1.31 | 32.33 | 26.4 | 94 | 47.9 | 4.03 | 1.64 |
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
| Baseline (Adaptive L_t) | -22.13 | -22.21 | -2.68 | 0.0 | -2.08 | 22.39 | 89.6 | 14 | 0.0 | 0.0 | -0.64 |
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
| Baseline (SMH Bull Core + Swing) | 1214.2 | 97.89 | 1.72 | 0.944 | 1.68 | 39.12 | 8.9 | 71 | 60.6 | 3.13 | 2.4 |
| ML (SMH Bull Core + Swing) | 1025.68 | 89.94 | 1.7 | 0.948 | 1.72 | 36.16 | 9.5 | 75 | 56.0 | 2.79 | 2.18 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 634.26 | 69.6 | 1.4 | 0.853 | 1.41 | 39.77 | 11.9 | 78 | 60.3 | 2.41 | 1.29 |
| Baseline (Adaptive L_t) | 723.66 | 74.85 | 1.52 | 0.891 | 1.48 | 43.4 | 8.9 | 70 | 60.0 | 3.41 | 2.37 |
| ML (LightGBM + Platt) | 689.95 | 72.92 | 1.59 | 0.923 | 1.63 | 38.73 | 9.3 | 74 | 56.8 | 3.61 | 2.22 |
| Pure Pre-2022 Semi (Cash Swing) | 329.35 | 47.12 | 1.14 | 0.704 | 1.17 | 44.02 | 11.9 | 79 | 59.5 | 2.64 | 1.26 |
| Baseline (Fixed 20d) | 700.44 | 73.53 | 1.54 | 0.907 | 1.59 | 32.33 | 9.9 | 81 | 55.6 | 4.46 | 1.99 |
| SMH Buy & Hold | 462.58 | 58.12 | 1.34 | 0.826 | 1.33 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 359.21 | 49.83 | 1.14 | 0.707 | 1.13 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 216.2 | 35.71 | 1.22 | 0.759 | 1.17 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 181.17 | 31.55 | 1.25 | 0.776 | 1.23 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 220.35 | 36.18 | 1.21 | 0.754 | 1.19 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 113.8 | 22.33 | 0.73 | 0.405 | 0.73 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 112.48 | 22.13 | 1.12 | 0.696 | 1.11 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.45 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive L_t, Cash + T-Bill Interest)

| year | total_return_pct | cagr_pct | sharpe | deflated_sharpe_prob | sortino | max_dd_pct | cash_days_pct | trades | win_rate_pct | profit_factor | avg_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.0 | -22.13 | -22.21 | -2.68 | 0.0 | -2.08 | 22.39 | 89.6 | 14.0 | 0.0 | 0.0 | -0.64 |
| 2023.0 | 40.11 | 40.49 | 1.52 | 0.439 | 1.57 | 19.99 | 6.0 | 24.0 | 70.8 | 3.6 | 1.04 |
| 2024.0 | 87.36 | 87.36 | 1.95 | 0.613 | 2.15 | 21.91 | 7.5 | 22.0 | 63.6 | 4.82 | 1.25 |
| 2025.0 | 96.02 | 97.08 | 2.05 | 0.642 | 2.1 | 16.46 | 20.4 | 14.0 | 50.0 | 11.16 | 8.36 |
| 2026.0 | 57.29 | 77.45 | 1.18 | 0.276 | 1.09 | 43.4 | 0.0 | 10.0 | 40.0 | 0.27 | -0.31 |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| year | total_return_pct | cagr_pct | sharpe | deflated_sharpe_prob | sortino | max_dd_pct | cash_days_pct | trades | win_rate_pct | profit_factor | avg_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.0 | -22.46 | -22.54 | -2.64 | 0.0 | -2.06 | 22.67 | 89.6 | 16.0 | 0.0 | 0.0 | -0.66 |
| 2023.0 | 47.55 | 48.01 | 1.75 | 0.53 | 1.85 | 19.27 | 6.0 | 25.0 | 68.0 | 4.37 | 0.89 |
| 2024.0 | 80.05 | 80.05 | 1.83 | 0.565 | 2.02 | 24.46 | 7.5 | 23.0 | 52.2 | 4.13 | 1.05 |
| 2025.0 | 71.38 | 72.12 | 1.76 | 0.535 | 1.83 | 18.8 | 20.4 | 14.0 | 50.0 | 8.26 | 8.36 |
| 2026.0 | 74.36 | 102.18 | 1.5 | 0.371 | 1.48 | 38.73 | 1.5 | 12.0 | 50.0 | 1.17 | 0.09 |

## 8. Recent 25 OOS Trades (ML (LightGBM + Platt))

| ticker | tier | entry_date | exit_date | days_held | entry_price | exit_price | initial_stop | tp1_hit | net_pnl | return_pct | r_multiple | exit_reason | entry_prob | size_scalar | shap_summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STX | MEDIUM | 2025-01-31 00:00:00 | 2025-02-28 00:00:00 | 20 | 95.99 | 99.58 | 85.96 | False | 228.1 | 3.74 | 0.36 | REGIME_OFF | 0.366 | 1.06 | vol_compress=1.65 (+0.010) ; vix_ts=0.88 (+0.009) ; sector_rs=-0.03 (-0.009) ; skew_idx=-0.52 (-0.006) ; vxn_squeeze_vel=0.49 (-0.004) |
| META | MEDIUM | 2025-01-31 00:00:00 | 2025-02-28 00:00:00 | 20 | 687.54 | 663.92 | 627.77 | False | -149.94 | -3.43 | -0.4 | REGIME_OFF | 0.346 | 0.91 | sector_rs=-0.03 (-0.009) ; vix_ts=0.88 (+0.008) ; slope_r2_20d=0.71 (-0.007) ; skew_idx=-0.52 (-0.006) ; resid_mom_60=0.19 (-0.006) |
| INTC | HIGH | 2025-02-24 00:00:00 | 2025-02-28 00:00:00 | 5 | 24.57 | 23.71 | 20.88 | False | -237.99 | -3.48 | -0.23 | REGIME_OFF | 0.382 | 1.17 | sector_rs=-0.05 (+0.030) ; vxn_squeeze_vel=0.92 (-0.030) ; rs_rank=0.96 (+0.010) ; vol_compress=1.77 (+0.009) ; vix_ts=0.93 (-0.008) |
| CEG | MEDIUM | 2025-05-13 00:00:00 | 2025-09-02 00:00:00 | 77 | 278.39 | 298.61 | 237.89 | True | 266.94 | 12.09 | 0.83 | STOP_GAP | 0.354 | 1.0 | vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.011) ; skew_idx=-0.25 (-0.010) ; slope_r2_20d=0.89 (-0.006) ; rs_rank=0.86 (+0.005) |
| APP | MEDIUM | 2025-09-03 00:00:00 | 2025-10-06 00:00:00 | 24 | 488.03 | 586.59 | 418.67 | True | 1299.71 | 21.7 | 1.53 | TRAIL_STOP_EOD | 0.367 | 1.1 | sector_rs=-0.03 (-0.026) ; rs_rank=0.96 (+0.017) ; vxn_squeeze_vel=0.58 (+0.008) ; vix_ts=0.89 (+0.002) ; slope_accel=0.28 (+0.002) |
| NBIS | LOW | 2025-10-07 00:00:00 | 2025-10-20 00:00:00 | 10 | 127.91 | 108.65 | 108.73 | False | -709.59 | -15.06 | -1.0 | STOP | 0.319 | 0.78 | skew_idx=-1.65 (-0.088) ; resid_mom_60=0.80 (+0.044) ; slope_t_norm_40d=7.05 (-0.013) ; vix_ts=0.86 (-0.011) ; sector_rs=0.12 (+0.010) |
| ARM | MEDIUM | 2025-10-21 00:00:00 | 2025-11-03 00:00:00 | 10 | 170.65 | 168.56 | 146.3 | False | -79.48 | -1.22 | -0.09 | EARNINGS_EXIT | 0.369 | 1.05 | slope_r2_20d=0.84 (-0.008) ; resid_mom_60=-0.19 (+0.005) ; sector_rs=0.07 (-0.004) ; rs_rank=0.92 (+0.002) ; vix_ts=0.90 (+0.002) |
| CLS | HIGH | 2025-11-05 00:00:00 | 2025-11-13 00:00:00 | 7 | 335.23 | 284.75 | 284.95 | False | -1552.76 | -15.06 | -1.0 | STOP | 0.39 | 1.2 | skew_idx=-0.86 (-0.036) ; vxn_squeeze_vel=0.58 (+0.015) ; slope_r2_20d=0.87 (-0.013) ; rs_rank=0.98 (+0.009) ; resid_mom_20=0.29 (+0.007) |
| VRT | MEDIUM | 2025-05-13 00:00:00 | 2025-12-17 00:00:00 | 152 | 100.97 | 149.62 | 85.82 | True | 920.92 | 43.88 | 2.93 | TRAIL_STOP_EOD | 0.351 | 0.98 | vix_ts=0.91 (+0.028) ; skew_idx=-0.25 (-0.010) ; sector_rs=0.09 (-0.008) ; slope_r2_20d=0.88 (-0.006) ; vxn_squeeze_vel=-1.22 (-0.004) |
| APP | HIGH | 2025-12-24 00:00:00 | 2026-01-02 00:00:00 | 6 | 728.36 | 628.82 | 629.26 | False | -1821.69 | -13.67 | -1.0 | STOP | 0.397 | 1.24 | vix_ts=0.78 (-0.064) ; skew_idx=2.44 (+0.031) ; rs_rank=1.00 (+0.026) ; resid_mom_20=0.21 (+0.009) ; slope_r2_20d=0.60 (-0.008) |
| MU | LOW | 2026-01-05 00:00:00 | 2026-03-30 00:00:00 | 59 | 325.12 | 321.47 | 280.62 | True | 273.48 | 5.41 | 0.4 | TRAIL_STOP_EOD | 0.306 | 0.65 | vix_ts=0.81 (-0.052) ; skew_idx=-0.98 (-0.044) ; resid_mom_60=0.37 (+0.039) ; vxn_squeeze_vel=0.75 (-0.038) ; rs_rank=0.98 (+0.020) |
| WDC | MEDIUM | 2025-05-13 00:00:00 | 2026-07-07 00:00:00 | 288 | 46.85 | 531.86 | 41.29 | True | 21396.66 | 781.78 | 65.85 | STOP_GAP | 0.355 | 1.01 | vix_ts=0.91 (+0.028) ; sector_rs=0.09 (-0.012) ; skew_idx=-0.25 (-0.010) ; rs_rank=0.96 (+0.010) ; slope_r2_20d=0.91 (-0.006) |
| LITE | MEDIUM | 2025-05-13 00:00:00 | 2026-07-07 00:00:00 | 288 | 71.85 | 698.93 | 61.07 | True | 14664.92 | 663.16 | 44.21 | STOP_GAP | 0.358 | 1.03 | vix_ts=0.91 (+0.028) ; skew_idx=-0.25 (-0.010) ; ema50_slope=0.11 (+0.008) ; slope_sharpe=5.57 (-0.006) ; vxn_squeeze_vel=-1.22 (-0.006) |
| ARM | HIGH | 2026-04-01 00:00:00 | 2026-07-14 00:00:00 | 71 | 154.5 | 280.97 | 131.32 | True | 10312.7 | 69.41 | 4.63 | TRAIL_STOP_EOD | 0.436 | 1.38 | vix_ts=0.99 (+0.031) ; rs_rank=0.98 (+0.027) ; slope_r2_20d=0.73 (-0.011) ; skew_idx=0.04 (-0.008) ; slope_t_norm_10d=4.87 (+0.007) |
| COHR | LOW | 2025-11-17 00:00:00 | 2026-07-16 00:00:00 | 165 | 138.14 | 285.89 | 117.42 | True | 2891.67 | 90.44 | 6.03 | STOP_GAP | 0.212 | 0.52 | skew_idx=-1.97 (-0.170) ; slope_t_norm_40d=5.86 (-0.016) ; vxn_squeeze_vel=0.43 (-0.009) ; sector_rs=-0.01 (+0.007) ; slope_r2_20d=0.62 (-0.004) |
| NOW | HIGH | 2026-07-14 00:00:00 | 2026-07-20 00:00:00 | 5 | 103.81 | 104.63 | 88.24 | False | 194.57 | 0.78 | 0.05 | EARNINGS_EXIT | 0.406 | 1.28 | sector_rs=-0.06 (+0.014) ; rs_rank=0.84 (+0.006) ; vxn_squeeze_vel=0.12 (+0.006) ; slope_t_norm_10d=5.79 (-0.002) ; slope_sharpe=4.60 (-0.002) |
| ANET | HIGH | 2026-07-14 00:00:00 | 2026-07-29 00:00:00 | 12 | 184.03 | 157.86 | 156.42 | False | -2780.17 | -14.22 | -0.95 | TIME_STOP_12D | 0.437 | 1.4 | rs_rank=1.00 (+0.036) ; sector_rs=-0.06 (+0.017) ; vxn_squeeze_vel=0.12 (+0.005) ; skew_idx=0.90 (-0.004) ; resid_mom_20=0.18 (+0.001) |
| PLTR | MEDIUM | 2026-07-21 00:00:00 | 2026-08-03 00:00:00 | 10 | 133.92 | 125.56 | 113.84 | False | -973.21 | -6.24 | -0.42 | EARNINGS_EXIT | 0.385 | 1.13 | vxn_squeeze_vel=0.37 (+0.015) ; sector_rs=-0.15 (-0.010) ; vix_ts=0.91 (-0.006) ; skew_idx=0.84 (-0.005) ; rs_rank=0.86 (+0.004) |
| TER | MEDIUM | 2026-08-10 00:00:00 | 2026-09-01 00:00:00 | 17 | 386.78 | 328.53 | 328.76 | False | -1951.54 | -15.06 | -1.0 | STOP | 0.363 | 0.96 | sector_rs=-0.07 (+0.064) ; vxn_squeeze_vel=-1.11 (+0.052) ; slope_t_norm_40d=-2.42 (+0.033) ; skew_idx=-1.91 (-0.031) ; slope_accel=0.49 (+0.020) |
| PLTR | MEDIUM | 2026-08-06 00:00:00 | 2026-09-10 00:00:00 | 25 | 155.98 | 165.74 | 132.58 | False | 810.5 | 6.26 | 0.42 | TIME_STOP_25D | 0.365 | 0.98 | skew_idx=-1.91 (-0.053) ; vxn_squeeze_vel=-2.33 (+0.052) ; sector_rs=-0.07 (+0.041) ; slope_t_norm_40d=0.83 (+0.025) ; slope_accel=0.34 (+0.017) |
| ORCL | MEDIUM | 2026-08-11 00:00:00 | 2026-09-10 00:00:00 | 22 | 150.75 | 152.27 | 128.55 | False | 130.36 | 1.01 | 0.07 | EARNINGS_EXIT | 0.361 | 0.94 | sector_rs=-0.06 (+0.050) ; skew_idx=-1.04 (-0.021) ; vix_ts=0.81 (-0.015) ; slope_t_norm_40d=-2.40 (+0.014) ; slope_accel=0.87 (+0.011) |
| CEG | MEDIUM | 2026-09-03 00:00:00 | 2026-09-14 00:00:00 | 7 | 292.6 | 264.36 | 264.54 | False | -1871.53 | -9.65 | -1.01 | STOP | 0.358 | 0.92 | skew_idx=0.15 (-0.011) ; vix_ts=0.86 (-0.005) ; rs_rank=0.90 (+0.003) ; sector_rs=-0.03 (-0.002) ; slope_t_norm_40d=5.66 (+0.001) |
| NOW | MEDIUM | 2026-08-10 00:00:00 | 2026-09-28 00:00:00 | 35 | 124.81 | 131.36 | 106.09 | False | 756.78 | 5.25 | 0.35 | TIME_STOP_25D | 0.377 | 1.07 | skew_idx=-1.91 (-0.078) ; sector_rs=-0.07 (+0.072) ; resid_mom_60=0.33 (+0.070) ; vxn_squeeze_vel=-1.11 (+0.048) ; vix_ts=0.80 (-0.010) |
| MPWR | LOW | 2026-10-08 00:00:00 | 2026-10-14 00:00:00 | 5 | 1406.97 | 1245.88 | 1246.76 | False | -1669.77 | -11.45 | -1.01 | STOP | 0.349 | 0.85 | skew_idx=-0.40 (-0.015) ; vix_ts=0.85 (-0.014) ; vxn_squeeze_vel=-0.50 (-0.005) ; slope_r2_20d=0.82 (-0.002) ; rs_rank=0.84 (+0.002) |
| MU | HIGH | 2026-09-11 00:00:00 | 2026-10-15 00:00:00 | 25 | 993.74 | 930.59 | 844.68 | False | -1387.14 | -6.35 | -0.42 | TIME_STOP_25D | 0.4 | 1.24 | rs_rank=0.98 (+0.020) ; skew_idx=0.54 (-0.013) ; vix_ts=0.90 (-0.008) ; sector_rs=-0.02 (-0.005) ; vxn_squeeze_vel=1.06 (+0.005) |
