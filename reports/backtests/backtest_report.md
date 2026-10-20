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
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.966 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.74 ; OOS: 3.51 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.57% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.57% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.44 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -19.8% ; DD: 20.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.01 ; Sortino Lift: +0.06 ; CAGR Lift: +5.9% ; DD Red: -5.2% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.81 ; OOS: 3.55 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.92% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.92% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.40 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.9% ; DD: 20.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.07 ; Sortino Lift: +0.11 ; CAGR Lift: +10.9% ; DD Red: -5.1% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 838.23 | 59.77 | 1.42 | 0.922 | 1.46 | 30.38 | 25.7 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 962.55 | 63.99 | 1.44 | 0.932 | 1.53 | 35.57 | 25.7 | 92 | 47.8 | 3.51 | 1.64 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 370.94 | 38.31 | 1.02 | 0.713 | 1.03 | 37.84 | 27.4 | 88 | 53.4 | 3.02 | 1.18 |
| `Baseline (Adaptive `L_t`)` | 621.9 | 51.25 | 1.33 | 0.893 | 1.39 | 30.83 | 25.7 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 807.82 | 58.68 | 1.4 | 0.921 | 1.51 | 35.92 | 25.7 | 91 | 47.3 | 3.55 | 1.66 |
| Pure Pre-2022 Semi (Cash Swing) | 288.53 | 32.85 | 0.96 | 0.663 | 0.98 | 35.52 | 27.4 | 89 | 52.8 | 3.01 | 1.16 |
| Baseline (Fixed 20d) | 650.19 | 52.47 | 1.31 | 0.885 | 1.38 | 34.9 | 25.8 | 97 | 46.4 | 3.8 | 1.63 |
| SMH Buy & Hold | 256.8 | 30.5 | 0.8 | 0.53 | 0.79 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 183.34 | 24.36 | 0.65 | 0.404 | 0.65 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 115.31 | 17.41 | 0.59 | 0.355 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 84.32 | 13.65 | 0.5 | 0.281 | 0.49 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 100.78 | 15.71 | 0.53 | 0.306 | 0.52 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 36.4 | 6.71 | 0.23 | 0.123 | 0.23 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 71.69 | 11.98 | 0.51 | 0.292 | 0.51 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.92 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -19.78 | -19.85 | -2.54 | 0.0 | -2.02 | 20.0 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -19.88 | -19.95 | -2.56 | 0.0 | -2.04 | 20.1 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
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
| Baseline (SMH Bull Core + Swing) | 1080.18 | 92.07 | 1.78 | 0.961 | 1.79 | 30.38 | 8.9 | 78 | 60.3 | 3.59 | 1.98 |
| ML (SMH Bull Core + Swing) | 1224.3 | 98.01 | 1.79 | 0.966 | 1.85 | 35.57 | 8.9 | 75 | 58.7 | 3.74 | 2.15 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 496.55 | 60.36 | 1.34 | 0.823 | 1.32 | 37.84 | 11.0 | 74 | 63.5 | 3.5 | 1.53 |
| `Baseline (Adaptive `L_t`)` | 805.87 | 79.09 | 1.69 | 0.947 | 1.74 | 30.83 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 1032.89 | 90.0 | 1.76 | 0.961 | 1.85 | 35.92 | 8.9 | 74 | 58.1 | 3.81 | 2.18 |
| Pure Pre-2022 Semi (Cash Swing) | 390.98 | 52.31 | 1.28 | 0.793 | 1.31 | 35.52 | 11.0 | 75 | 62.7 | 3.57 | 1.5 |
| Baseline (Fixed 20d) | 789.95 | 78.25 | 1.62 | 0.93 | 1.68 | 34.9 | 9.2 | 84 | 53.6 | 4.12 | 1.97 |
| SMH Buy & Hold | 452.89 | 57.17 | 1.33 | 0.819 | 1.31 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 349.55 | 48.8 | 1.12 | 0.696 | 1.11 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 211.8 | 35.08 | 1.2 | 0.748 | 1.15 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 177.9 | 31.03 | 1.22 | 0.765 | 1.21 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 216.65 | 35.63 | 1.2 | 0.744 | 1.17 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 109.11 | 21.54 | 0.71 | 0.386 | 0.7 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 111.93 | 21.97 | 1.11 | 0.691 | 1.1 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.49 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.05% | +123.69% | 53.8% | 1.70 | 1.71 | -30.83% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.88% | -19.95% | 9.4% | -2.56 | -2.04 | -20.10% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +43.89% | +44.31% | 20.4% | 1.66 | 1.72 | -19.29% | 6.0% | 25 | 68.0% | 4.10 | +0.89R |
| 2024 | +85.33% | +85.33% | 31.4% | 1.97 | 2.21 | -23.38% | 7.5% | 22 | 59.1% | 5.22 | +1.18R |
| 2025 | +133.95% | +135.55% | 35.2% | 2.51 | 2.84 | -18.80% | 20.4% | 12 | 58.3% | 33.27 | +8.39R |
| 2026 | +75.27% | +102.09% | 60.0% | 1.42 | 1.43 | -35.92% | 0.0% | 15 | 40.0% | 1.16 | +0.81R |
