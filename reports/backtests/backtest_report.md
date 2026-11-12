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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.72 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.956 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.63 ; OOS: 3.41 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 38.0% (vs SMH 35.7%)` | 38.59% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 38.59% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.38 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -19.8% ; DD: 20.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.00 ; Sortino Lift: +0.04 ; CAGR Lift: +4.4% ; DD Red: -5.4% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.74 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.71 ; OOS: 3.46 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 38.0% (vs SMH 35.7%)` | 36.41% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 36.41% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.39 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.9% ; DD: 20.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.06 ; Sortino Lift: +0.10 ; CAGR Lift: +10.2% ; DD Red: -5.5% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 795.06 | 57.2 | 1.37 | 0.909 | 1.41 | 33.17 | 26.5 | 96 | 51.0 | 3.33 | 1.51 |
| ML (SMH Bull Core + Swing) | 888.3 | 60.45 | 1.38 | 0.917 | 1.46 | 38.59 | 26.1 | 95 | 47.4 | 3.41 | 1.58 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 353.62 | 36.63 | 0.98 | 0.69 | 0.99 | 38.63 | 28.3 | 89 | 52.8 | 2.75 | 1.16 |
| `Baseline (Adaptive `L_t`)` | 627.54 | 50.62 | 1.32 | 0.894 | 1.39 | 30.95 | 26.5 | 95 | 50.5 | 3.37 | 1.48 |
| ML (LightGBM + Platt) | 807.0 | 57.63 | 1.39 | 0.921 | 1.49 | 36.41 | 26.1 | 95 | 47.4 | 3.46 | 1.58 |
| Pure Pre-2022 Semi (Cash Swing) | 287.42 | 32.25 | 0.95 | 0.66 | 0.97 | 35.6 | 28.3 | 90 | 52.2 | 2.76 | 1.14 |
| Baseline (Fixed 20d) | 636.47 | 51.0 | 1.29 | 0.879 | 1.36 | 34.9 | 26.1 | 103 | 45.6 | 3.5 | 1.52 |
| SMH Buy & Hold | 227.97 | 27.78 | 0.73 | 0.479 | 0.72 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 163.09 | 22.1 | 0.6 | 0.365 | 0.59 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 102.93 | 15.73 | 0.53 | 0.312 | 0.51 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 77.37 | 12.56 | 0.45 | 0.252 | 0.44 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 89.66 | 14.12 | 0.48 | 0.269 | 0.46 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 30.05 | 5.57 | 0.19 | 0.108 | 0.19 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 69.88 | 11.56 | 0.49 | 0.277 | 0.48 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 21.25 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -19.79 | -19.86 | -2.54 | 0.0 | -2.03 | 20.0 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -19.89 | -19.96 | -2.56 | 0.0 | -2.04 | 20.1 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
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
| Baseline (SMH Bull Core + Swing) | 1025.87 | 87.57 | 1.72 | 0.953 | 1.73 | 33.17 | 10.2 | 81 | 60.5 | 3.58 | 1.91 |
| ML (SMH Bull Core + Swing) | 1131.91 | 92.01 | 1.72 | 0.956 | 1.77 | 38.59 | 9.7 | 78 | 57.7 | 3.63 | 2.06 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 474.62 | 57.5 | 1.29 | 0.803 | 1.27 | 38.63 | 12.5 | 75 | 62.7 | 3.14 | 1.5 |
| `Baseline (Adaptive `L_t`)` | 812.95 | 77.63 | 1.68 | 0.948 | 1.73 | 30.95 | 10.2 | 80 | 60.0 | 3.68 | 1.88 |
| ML (LightGBM + Platt) | 1031.99 | 87.84 | 1.74 | 0.961 | 1.83 | 36.41 | 9.7 | 78 | 57.7 | 3.71 | 2.06 |
| Pure Pre-2022 Semi (Cash Swing) | 389.57 | 51.08 | 1.27 | 0.79 | 1.29 | 35.6 | 12.5 | 76 | 61.8 | 3.21 | 1.47 |
| Baseline (Fixed 20d) | 773.67 | 75.61 | 1.59 | 0.926 | 1.65 | 34.9 | 9.9 | 90 | 52.2 | 3.77 | 1.82 |
| SMH Buy & Hold | 408.21 | 52.56 | 1.22 | 0.766 | 1.19 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 317.41 | 44.95 | 1.03 | 0.64 | 1.0 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 193.87 | 32.32 | 1.1 | 0.685 | 1.03 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 167.41 | 29.12 | 1.13 | 0.711 | 1.1 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 199.11 | 32.93 | 1.1 | 0.688 | 1.06 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 99.39 | 19.64 | 0.65 | 0.344 | 0.63 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 109.7 | 21.21 | 1.06 | 0.66 | 1.04 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.81 | 4.58 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +91.54% | +111.97% | 51.7% | 1.65 | 1.66 | -30.95% | 6.4% | 18 | 50.0% | 1.48 | +0.71R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.89% | -19.96% | 9.4% | -2.56 | -2.04 | -20.10% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +43.79% | +44.21% | 20.4% | 1.65 | 1.72 | -19.35% | 6.0% | 25 | 68.0% | 4.08 | +0.89R |
| 2024 | +85.51% | +85.51% | 31.4% | 1.97 | 2.21 | -23.37% | 7.5% | 22 | 59.1% | 5.24 | +1.18R |
| 2025 | +134.68% | +136.29% | 35.1% | 2.52 | 2.86 | -18.36% | 20.4% | 12 | 58.3% | 34.56 | +8.39R |
| 2026 | +74.56% | +90.40% | 57.6% | 1.35 | 1.37 | -36.41% | 4.1% | 19 | 42.1% | 1.15 | +0.62R |
