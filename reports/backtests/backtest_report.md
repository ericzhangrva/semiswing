# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2404` -> Calibrated `0.2404` (Brier Skill Score: `0.0382`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.70 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.949 | FAIL |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.18 ; OOS: 2.99 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 41.62% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 41.62% | FAIL |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.36 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -20.9% ; DD: 21.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0382 ; SR Lift: -0.07 ; Sortino Lift: -0.03 ; CAGR Lift: +1.4% ; DD Red: -11.5% | FAIL |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.66 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.942 | FAIL |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.31 ; OOS: 3.09 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 41.54% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 41.54% | FAIL |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.32 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -21.0% ; DD: 21.2% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0382 ; SR Lift: -0.02 ; Sortino Lift: +0.01 ; CAGR Lift: +6.9% ; DD Red: -10.6% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 835.39 | 59.67 | 1.41 | 0.92 | 1.45 | 30.09 | 25.7 | 93 | 50.5 | 3.33 | 1.56 |
| ML (SMH Bull Core + Swing) | 859.43 | 60.52 | 1.36 | 0.903 | 1.43 | 41.62 | 25.7 | 95 | 44.2 | 2.99 | 1.66 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 286.81 | 32.73 | 0.89 | 0.613 | 0.9 | 37.6 | 28.2 | 99 | 51.5 | 2.27 | 0.92 |
| `Baseline (Adaptive `L_t`)` | 618.93 | 51.11 | 1.32 | 0.89 | 1.39 | 30.9 | 25.7 | 92 | 50.0 | 3.37 | 1.53 |
| ML (LightGBM + Platt) | 724.05 | 55.49 | 1.32 | 0.888 | 1.4 | 41.54 | 25.7 | 95 | 45.3 | 3.09 | 1.68 |
| Pure Pre-2022 Semi (Cash Swing) | 203.8 | 26.18 | 0.78 | 0.518 | 0.8 | 36.35 | 28.2 | 101 | 50.5 | 2.28 | 0.89 |
| Baseline (Fixed 20d) | 661.7 | 52.95 | 1.32 | 0.886 | 1.38 | 34.9 | 25.8 | 97 | 44.3 | 3.88 | 1.61 |
| SMH Buy & Hold | 257.33 | 30.54 | 0.8 | 0.53 | 0.79 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 183.9 | 24.41 | 0.65 | 0.405 | 0.65 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 115.37 | 17.42 | 0.59 | 0.355 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 84.42 | 13.67 | 0.5 | 0.281 | 0.49 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 100.94 | 15.73 | 0.53 | 0.306 | 0.52 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 36.5 | 6.73 | 0.23 | 0.123 | 0.23 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 71.73 | 11.98 | 0.51 | 0.292 | 0.51 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.92 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.68 | -20.76 | -2.64 | 0.0 | -2.08 | 20.94 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -20.91 | -20.98 | -2.46 | 0.0 | -1.93 | 21.12 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -20.34 | -20.42 | -2.57 | 0.0 | -2.02 | 20.6 | 89.6 | 13 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.49 | -20.56 | -2.65 | 0.0 | -2.08 | 20.75 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -21.03 | -21.1 | -2.48 | 0.0 | -1.95 | 21.24 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (Cash Swing) | -20.18 | -20.26 | -2.58 | 0.0 | -2.03 | 20.45 | 89.6 | 13 | 0.0 | 0.0 | -0.68 |
| Baseline (Fixed 20d) | -15.71 | -15.77 | -2.35 | 0.0 | -1.89 | 15.99 | 88.8 | 13 | 0.0 | 0.0 | -0.56 |
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
| Baseline (SMH Bull Core + Swing) | 1079.12 | 92.02 | 1.77 | 0.96 | 1.78 | 30.09 | 8.9 | 78 | 60.3 | 3.58 | 1.98 |
| ML (SMH Bull Core + Swing) | 1112.85 | 93.46 | 1.7 | 0.949 | 1.75 | 41.62 | 8.9 | 78 | 53.8 | 3.18 | 2.16 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 385.52 | 51.86 | 1.19 | 0.737 | 1.17 | 37.6 | 12.1 | 86 | 59.3 | 2.56 | 1.16 |
| `Baseline (Adaptive `L_t`)` | 804.07 | 79.0 | 1.68 | 0.946 | 1.73 | 30.9 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 943.27 | 85.91 | 1.66 | 0.942 | 1.74 | 41.54 | 8.9 | 78 | 55.1 | 3.31 | 2.18 |
| Pure Pre-2022 Semi (Cash Swing) | 280.56 | 42.39 | 1.08 | 0.664 | 1.09 | 36.35 | 12.1 | 88 | 58.0 | 2.64 | 1.12 |
| Baseline (Fixed 20d) | 803.54 | 78.97 | 1.63 | 0.93 | 1.67 | 34.9 | 9.2 | 84 | 51.2 | 4.21 | 1.94 |
| SMH Buy & Hold | 453.71 | 57.23 | 1.33 | 0.819 | 1.31 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 350.44 | 48.88 | 1.12 | 0.697 | 1.11 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 211.88 | 35.09 | 1.2 | 0.748 | 1.15 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 178.05 | 31.05 | 1.23 | 0.765 | 1.21 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 216.9 | 35.66 | 1.2 | 0.745 | 1.17 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 109.28 | 21.56 | 0.71 | 0.386 | 0.7 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 111.99 | 21.98 | 1.11 | 0.692 | 1.1 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.49 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.49% | -20.56% | 9.3% | -2.65 | -2.08 | -20.75% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.75% | +86.75% | 33.0% | 1.91 | 2.09 | -23.09% | 7.5% | 22 | 63.6% | 5.03 | +1.24R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +89.86% | +123.39% | 53.8% | 1.70 | 1.72 | -30.90% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -21.03% | -21.10% | 10.2% | -2.48 | -1.95 | -21.24% | 89.6% | 17 | 0.0% | 0.00 | -0.62R |
| 2023 | +45.39% | +45.83% | 20.7% | 1.69 | 1.78 | -19.82% | 6.0% | 25 | 68.0% | 4.07 | +0.89R |
| 2024 | +84.53% | +84.53% | 32.6% | 1.90 | 2.08 | -22.88% | 7.5% | 24 | 54.2% | 4.26 | +1.03R |
| 2025 | +129.09% | +130.61% | 36.4% | 2.38 | 2.61 | -19.12% | 20.4% | 12 | 58.3% | 33.28 | +8.39R |
| 2026 | +63.91% | +85.81% | 61.6% | 1.26 | 1.30 | -41.54% | 0.0% | 17 | 35.3% | 0.93 | +1.29R |
