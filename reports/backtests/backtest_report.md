# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2391` -> Calibrated `0.2391`

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
| OOS Sharpe >= 1.0 (2022-2026 Overall or 2023-2026 AI Era) | Overall: 1.18 ; AI-Era: 1.44 | PASS |
| Deflated Sharpe Probability >= 0.95 | 0.864 | REVIEW |
| Profit Factor >= 1.50 | Overall: 3.43 ; AI-Era: 3.71 | PASS |
| Max Drawdown <= 25.5% (vs SMH 45.1%) | 24.89% (vs SMH 45.14%) | PASS |
| 2022 Bear Stress Gate (DD <= 12% & Cash Days >= 75%) | 2022 DD: 11.35% (SMH: 45.14%) ; Cash: 92.0% | PASS |
| ML vs Baseline Comparison | ML SR: 1.18 (PF 3.43, DD 24.9%) vs Baseline SR: 1.09 | ENSEMBLE (ML + Baseline) |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 773.5 | 57.52 | 1.28 | 0.869 | 1.31 | 35.0 | 35.3 | 119 | 45.4 | 2.28 | 0.6 |
| ML (SMH Bull Core + Swing) | 722.25 | 55.54 | 1.25 | 0.852 | 1.27 | 30.93 | 47.8 | 66 | 50.0 | 3.23 | 0.99 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 218.05 | 27.45 | 0.77 | 0.508 | 0.77 | 45.56 | 37.0 | 99 | 42.4 | 1.33 | 0.47 |
| Baseline (Adaptive L_t) | 463.22 | 43.67 | 1.09 | 0.764 | 1.14 | 34.78 | 35.3 | 119 | 45.4 | 2.4 | 0.6 |
| ML (LightGBM + Platt) | 455.91 | 43.28 | 1.18 | 0.815 | 1.21 | 24.89 | 47.8 | 65 | 50.8 | 3.43 | 1.01 |
| Pure Pre-2022 Semi (Cash Swing) | 114.33 | 17.33 | 0.55 | 0.324 | 0.57 | 46.74 | 37.0 | 99 | 42.4 | 1.52 | 0.44 |
| Baseline (Fixed 20d) | 344.54 | 36.72 | 0.97 | 0.669 | 1.0 | 33.74 | 35.4 | 114 | 50.9 | 2.59 | 0.71 |
| SMH Buy & Hold | 263.05 | 31.07 | 0.81 | 0.539 | 0.8 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 189.43 | 24.98 | 0.66 | 0.414 | 0.66 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 118.35 | 17.8 | 0.6 | 0.365 | 0.59 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 86.5 | 13.97 | 0.51 | 0.289 | 0.5 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 103.13 | 16.03 | 0.54 | 0.313 | 0.53 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 39.46 | 7.23 | 0.25 | 0.13 | 0.25 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 72.13 | 12.07 | 0.52 | 0.294 | 0.51 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.9 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -24.51 | -24.6 | -1.68 | 0.0 | -1.51 | 24.58 | 83.3 | 15 | 33.3 | 0.05 | -0.38 |
| ML (SMH Bull Core + Swing) | -28.61 | -28.71 | -1.96 | 0.0 | -1.82 | 28.67 | 92.0 | 10 | 20.0 | 0.03 | -0.55 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -25.71 | -25.8 | -1.65 | 0.0 | -1.51 | 25.77 | 86.1 | 10 | 10.0 | 0.01 | -0.57 |
| Baseline (Adaptive L_t) | -16.55 | -16.61 | -1.48 | 0.0 | -1.36 | 17.14 | 83.3 | 15 | 33.3 | 0.05 | -0.38 |
| ML (LightGBM + Platt) | -11.24 | -11.28 | -2.34 | 0.0 | -1.86 | 11.35 | 92.0 | 9 | 22.2 | 0.03 | -0.54 |
| Pure Pre-2022 Semi (Cash Swing) | -16.1 | -16.16 | -1.39 | 0.0 | -1.27 | 16.38 | 86.1 | 10 | 10.0 | 0.01 | -0.57 |
| Baseline (Fixed 20d) | -14.91 | -14.96 | -1.32 | 0.0 | -1.26 | 15.2 | 83.3 | 14 | 35.7 | 0.05 | -0.38 |
| SMH Buy & Hold | -34.97 | -35.08 | -0.85 | 0.0 | -0.87 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | -36.35 | -36.47 | -0.88 | 0.0 | -0.89 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | -30.28 | -30.38 | -0.96 | 0.0 | -0.98 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | -33.22 | -33.33 | -1.17 | 0.0 | -1.19 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | -36.62 | -36.74 | -1.2 | 0.0 | -1.24 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | -34.91 | -35.02 | -1.0 | 0.0 | -1.02 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | -18.65 | -18.71 | -0.82 | 0.0 | -0.85 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 2.05 | 2.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 5. View B — Modern AI Cycle (`2023–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 1056.92 | 91.32 | 1.65 | 0.937 | 1.67 | 35.0 | 22.6 | 104 | 47.1 | 2.39 | 0.74 |
| ML (SMH Bull Core + Swing) | 1051.57 | 91.08 | 1.66 | 0.935 | 1.66 | 30.93 | 36.1 | 56 | 55.4 | 3.42 | 1.26 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 328.04 | 47.01 | 1.12 | 0.69 | 1.1 | 45.56 | 24.1 | 89 | 46.1 | 1.43 | 0.58 |
| Baseline (Adaptive L_t) | 574.83 | 65.85 | 1.38 | 0.843 | 1.42 | 34.78 | 22.6 | 104 | 47.1 | 2.55 | 0.74 |
| ML (LightGBM + Platt) | 526.2 | 62.6 | 1.44 | 0.864 | 1.45 | 24.89 | 36.1 | 56 | 55.4 | 3.71 | 1.26 |
| Pure Pre-2022 Semi (Cash Swing) | 155.42 | 28.21 | 0.79 | 0.446 | 0.8 | 46.74 | 24.1 | 89 | 46.1 | 1.66 | 0.55 |
| Baseline (Fixed 20d) | 422.34 | 54.97 | 1.22 | 0.758 | 1.25 | 33.74 | 22.7 | 100 | 53.0 | 2.81 | 0.86 |
| SMH Buy & Hold | 462.58 | 58.12 | 1.34 | 0.826 | 1.33 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 359.21 | 49.83 | 1.14 | 0.707 | 1.13 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 216.2 | 35.71 | 1.22 | 0.76 | 1.17 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 181.17 | 31.55 | 1.25 | 0.776 | 1.23 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 220.35 | 36.18 | 1.21 | 0.754 | 1.19 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 113.8 | 22.33 | 0.73 | 0.405 | 0.73 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 112.48 | 22.13 | 1.12 | 0.696 | 1.11 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.45 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive L_t, Cash + T-Bill Interest)

| year | total_return_pct | cagr_pct | sharpe | deflated_sharpe_prob | sortino | max_dd_pct | cash_days_pct | trades | win_rate_pct | profit_factor | avg_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.0 | -16.55 | -16.61 | -1.48 | 0.0 | -1.36 | 17.14 | 83.3 | 15.0 | 33.3 | 0.05 | -0.38 |
| 2023.0 | 71.32 | 72.06 | 1.97 | 0.617 | 2.23 | 18.36 | 17.2 | 27.0 | 51.9 | 3.37 | 0.57 |
| 2024.0 | 89.58 | 89.58 | 1.97 | 0.619 | 2.16 | 21.52 | 24.2 | 31.0 | 48.4 | 3.11 | 1.0 |
| 2025.0 | 50.87 | 51.37 | 1.26 | 0.347 | 1.22 | 21.8 | 29.6 | 22.0 | 36.4 | 3.16 | 1.18 |
| 2026.0 | 33.74 | 44.51 | 0.86 | 0.184 | 0.87 | 34.78 | 18.6 | 24.0 | 50.0 | 1.64 | 0.17 |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| year | total_return_pct | cagr_pct | sharpe | deflated_sharpe_prob | sortino | max_dd_pct | cash_days_pct | trades | win_rate_pct | profit_factor | avg_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.0 | -11.24 | -11.28 | -2.34 | 0.0 | -1.86 | 11.35 | 92.0 | 9.0 | 22.2 | 0.03 | -0.54 |
| 2023.0 | 37.3 | 37.65 | 1.77 | 0.54 | 2.27 | 10.82 | 46.8 | 7.0 | 57.1 | 4.04 | 1.16 |
| 2024.0 | 56.32 | 56.32 | 1.6 | 0.474 | 1.78 | 17.45 | 29.8 | 22.0 | 59.1 | 3.96 | 1.0 |
| 2025.0 | 70.09 | 70.81 | 1.49 | 0.434 | 1.41 | 19.9 | 39.6 | 16.0 | 62.5 | 7.85 | 2.1 |
| 2026.0 | 64.4 | 87.68 | 1.4 | 0.339 | 1.38 | 24.89 | 26.1 | 11.0 | 36.4 | 2.09 | 0.65 |

## 8. Recent 25 OOS Trades (ML (LightGBM + Platt))

| ticker | tier | entry_date | exit_date | days_held | entry_price | exit_price | initial_stop | tp1_hit | net_pnl | return_pct | r_multiple | exit_reason | entry_prob | shap_summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GEV | MEDIUM | 2025-01-10 00:00:00 | 2025-01-27 00:00:00 | 11 | 362.2 | 338.19 | 318.24 | True | 25.82 | 0.57 | 0.05 | STOP_GAP | 0.446 | resid_mom_60=0.32 (+0.073) ; slope_t_norm_40d=1.32 (-0.028) ; slope_accel=0.32 (+0.024) ; vix_ts=0.92 (+0.022) ; skew_idx=-0.44 (-0.014) |
| CLS | MEDIUM | 2025-01-10 00:00:00 | 2025-01-27 00:00:00 | 11 | 102.04 | 89.07 | 89.14 | True | -163.47 | -3.76 | -0.3 | STOP | 0.456 | resid_mom_60=0.50 (+0.121) ; skew_idx=-0.44 (-0.020) ; vix_ts=0.92 (+0.012) ; slope_r2=0.30 (+0.010) ; slope_t_norm_40d=6.72 (-0.009) |
| NBIS | MEDIUM | 2025-01-16 00:00:00 | 2025-01-27 00:00:00 | 7 | 37.13 | 31.53 | 31.56 | False | -578.13 | -15.06 | -1.0 | STOP | 0.458 | resid_mom_60=0.62 (+0.077) ; ema20_slope=0.99 (-0.016) ; rs_rank=0.98 (+0.014) ; vxn_squeeze_vel=-0.56 (+0.008) ; vix_ts=0.88 (+0.005) |
| APP | MEDIUM | 2025-02-19 00:00:00 | 2025-02-20 00:00:00 | 2 | 503.09 | 427.33 | 427.63 | False | -500.29 | -15.06 | -1.0 | STOP | 0.449 | sector_rs=-0.03 (-0.071) ; resid_mom_60=0.46 (+0.049) ; skew_idx=2.40 (+0.028) ; ema20_slope=1.61 (-0.022) ; vol_compress=1.46 (+0.018) |
| NBIS | HIGH | 2025-06-16 00:00:00 | 2025-07-22 00:00:00 | 25 | 48.03 | 50.97 | 40.83 | False | 266.6 | 6.12 | 0.41 | TIME_STOP_25D | 0.514 | skew_idx=2.22 (+0.096) ; vix_ts=0.92 (+0.085) ; ema20_slope=1.85 (-0.021) ; resid_mom_60=0.42 (+0.016) ; slope_accel=0.28 (+0.014) |
| VST | MEDIUM | 2025-06-23 00:00:00 | 2025-08-19 00:00:00 | 41 | 183.11 | 192.06 | 163.46 | False | 108.11 | 4.89 | 0.46 | TIME_STOP_25D | 0.451 | skew_idx=1.73 (+0.087) ; vix_ts=0.92 (+0.052) ; vxn_squeeze_vel=0.38 (+0.032) ; slope_r2_20d=0.74 (-0.014) ; sector_rs=0.06 (+0.007) |
| STX | HIGH | 2025-06-16 00:00:00 | 2025-10-10 00:00:00 | 82 | 126.96 | 212.97 | 116.34 | True | 2943.67 | 54.63 | 6.53 | TRAIL_STOP_EOD | 0.521 | skew_idx=2.22 (+0.127) ; vix_ts=0.92 (+0.063) ; ema50_slope=3.60 (+0.025) ; vxn_squeeze_vel=0.67 (+0.021) ; slope_accel=-0.50 (+0.020) |
| CRDO | HIGH | 2025-06-16 00:00:00 | 2025-10-14 00:00:00 | 84 | 75.56 | 129.66 | 64.22 | True | 2717.03 | 62.39 | 4.16 | TRAIL_STOP_EOD | 0.51 | skew_idx=2.22 (+0.104) ; vix_ts=0.92 (+0.068) ; resid_mom_60=0.29 (+0.036) ; vxn_squeeze_vel=0.67 (+0.020) ; slope_r2_20d=0.72 (-0.014) |
| NBIS | MEDIUM | 2025-10-15 00:00:00 | 2025-10-17 00:00:00 | 3 | 131.99 | 112.11 | 112.19 | False | -718.44 | -15.06 | -1.0 | STOP | 0.445 | sector_rs=0.08 (+0.036) ; resid_mom_20=0.25 (+0.035) ; vxn_squeeze_vel=1.03 (+0.015) ; vix_ts=0.94 (-0.012) ; resid_mom_60=0.71 (+0.010) |
| SNDK | MEDIUM | 2025-10-16 00:00:00 | 2025-11-20 00:00:00 | 26 | 146.1 | 195.82 | 124.19 | True | 1716.88 | 35.24 | 2.35 | TRAIL_STOP_EOD | 0.445 | sector_rs=0.11 (+0.055) ; skew_idx=-0.87 (-0.047) ; resid_mom_60=1.01 (+0.044) ; resid_mom_20=0.27 (+0.039) ; vix_ts=0.94 (-0.029) |
| CLS | HIGH | 2025-08-04 00:00:00 | 2026-03-02 00:00:00 | 145 | 199.19 | 266.4 | 169.31 | True | 1707.94 | 32.24 | 2.15 | STOP_GAP | 0.481 | skew_idx=1.58 (+0.072) ; vxn_squeeze_vel=1.20 (+0.033) ; resid_mom_60=0.30 (+0.024) ; vix_ts=0.96 (+0.011) ; sector_rs=0.01 (-0.006) |
| TER | MEDIUM | 2025-12-16 00:00:00 | 2026-03-06 00:00:00 | 55 | 194.31 | 272.65 | 170.8 | True | 2639.71 | 35.76 | 2.96 | TRAIL_STOP_EOD | 0.444 | skew_idx=3.67 (+0.046) ; vix_ts=0.84 (-0.008) ; slope_r2_20d=0.80 (-0.007) ; slope_t_norm_10d=0.77 (-0.005) ; resid_mom_20=0.11 (+0.005) |
| LITE | MEDIUM | 2025-09-24 00:00:00 | 2026-03-30 00:00:00 | 129 | 162.59 | 654.33 | 142.12 | True | 14180.29 | 232.58 | 18.48 | REGIME_OFF | 0.441 | slope_accel=-0.37 (+0.064) ; resid_mom_60=0.35 (+0.059) ; slope_r2=0.92 (+0.023) ; vxn_squeeze_vel=0.18 (+0.021) ; skew_idx=-0.50 (-0.018) |
| COHR | HIGH | 2025-12-16 00:00:00 | 2026-03-30 00:00:00 | 71 | 177.67 | 219.5 | 151.02 | True | 2203.51 | 26.86 | 1.79 | REGIME_OFF | 0.461 | skew_idx=3.67 (+0.047) ; rs_rank=0.96 (+0.011) ; slope_sharpe=6.44 (+0.011) ; slope_r2_20d=0.87 (-0.009) ; vix_ts=0.84 (-0.008) |
| VRT | MEDIUM | 2026-03-06 00:00:00 | 2026-03-30 00:00:00 | 17 | 241.0 | 233.95 | 204.85 | False | -259.11 | -2.93 | -0.2 | REGIME_OFF | 0.454 | vix_ts=1.00 (+0.036) ; skew_idx=1.02 (-0.027) ; rs_rank=0.98 (+0.023) ; vol_compress=0.61 (-0.022) ; sector_rs=0.04 (-0.021) |
| LITE | HIGH | 2026-04-14 00:00:00 | 2026-05-18 00:00:00 | 25 | 901.78 | 884.36 | 766.51 | False | -227.0 | -1.93 | -0.13 | TIME_STOP_25D | 0.49 | vix_ts=0.90 (+0.048) ; skew_idx=2.23 (+0.036) ; resid_mom_60=0.73 (+0.034) ; ema20_slope=1.10 (-0.021) ; vxn_squeeze_vel=-1.64 (+0.015) |
| ALAB | HIGH | 2026-06-03 00:00:00 | 2026-06-09 00:00:00 | 5 | 363.81 | 309.02 | 309.24 | False | -2953.38 | -15.06 | -1.0 | STOP | 0.486 | ema50_slope=4.04 (+0.094) ; resid_mom_60=0.38 (+0.043) ; sector_rs=0.16 (-0.031) ; resid_mom_20=0.26 (+0.024) ; ema20_slope=2.56 (+0.019) |
| STX | HIGH | 2026-04-14 00:00:00 | 2026-07-08 00:00:00 | 59 | 519.58 | 810.05 | 441.64 | True | 5796.78 | 49.33 | 3.29 | STOP_GAP | 0.489 | vix_ts=0.90 (+0.048) ; skew_idx=2.23 (+0.043) ; resid_mom_60=0.31 (+0.026) ; ema20_slope=1.66 (-0.023) ; vxn_squeeze_vel=-1.64 (+0.015) |
| MRVL | MEDIUM | 2026-05-01 00:00:00 | 2026-07-13 00:00:00 | 49 | 162.39 | 217.33 | 138.85 | True | 3345.53 | 32.86 | 2.27 | TRAIL_STOP_EOD | 0.445 | ema50_slope=4.00 (+0.104) ; resid_mom_60=0.53 (+0.050) ; skew_idx=-0.15 (-0.024) ; sector_rs=0.20 (-0.022) ; ema20_slope=1.97 (-0.017) |
| ALAB | MEDIUM | 2026-06-12 00:00:00 | 2026-07-13 00:00:00 | 20 | 380.01 | 361.8 | 323.0 | False | -621.31 | -4.79 | -0.32 | TRAIL_STOP_EOD | 0.456 | resid_mom_60=0.45 (+0.050) ; rs_rank=0.98 (+0.027) ; vix_ts=0.91 (-0.025) ; sector_rs=0.07 (+0.014) ; slope_r2_20d=0.69 (-0.008) |
| DELL | HIGH | 2026-04-14 00:00:00 | 2026-07-29 00:00:00 | 74 | 184.8 | 369.38 | 159.18 | True | 10327.6 | 81.24 | 5.86 | REGIME_OFF | 0.483 | vix_ts=0.90 (+0.048) ; skew_idx=2.23 (+0.034) ; resid_mom_60=0.38 (+0.030) ; ema20_slope=1.13 (-0.022) ; vxn_squeeze_vel=-1.64 (+0.015) |
| CLS | MEDIUM | 2026-10-02 00:00:00 | 2026-10-13 00:00:00 | 8 | 384.53 | 326.62 | 326.85 | False | -1844.4 | -15.06 | -1.0 | STOP | 0.441 | rs_rank=0.98 (+0.038) ; vxn_squeeze_vel=0.42 (+0.021) ; vol_compress=0.48 (+0.020) ; sector_rs=0.13 (+0.017) ; skew_idx=-0.27 (+0.006) |
| AMD | MEDIUM | 2026-09-28 00:00:00 | 2026-10-15 00:00:00 | 14 | 625.34 | 539.62 | 551.2 | False | -2102.26 | -13.71 | -1.16 | STOP_GAP | 0.44 | ema20_slope=2.42 (+0.050) ; vix_ts=0.83 (-0.024) ; vxn_squeeze_vel=0.53 (+0.024) ; sector_rs=0.09 (+0.011) ; rs_rank=0.96 (+0.007) |
| DELL | MEDIUM | 2026-09-24 00:00:00 | 2026-10-15 00:00:00 | 16 | 536.35 | 455.57 | 455.89 | False | -1814.63 | -15.06 | -1.0 | STOP | 0.441 | resid_mom_60=0.29 (+0.068) ; vix_ts=0.84 (-0.018) ; sector_rs=0.08 (+0.008) ; vxn_squeeze_vel=-0.58 (-0.005) ; rs_rank=0.90 (+0.003) |
| PLTR | HIGH | 2026-10-01 00:00:00 | 2026-10-15 00:00:00 | 11 | 190.22 | 200.36 | 171.22 | False | 1056.41 | 5.33 | 0.53 | REGIME_OFF | 0.493 | resid_mom_60=0.32 (+0.074) ; sector_rs=0.11 (+0.045) ; vxn_squeeze_vel=0.56 (+0.024) ; vol_compress=0.36 (+0.004) ; rs_rank=0.80 (+0.003) |
