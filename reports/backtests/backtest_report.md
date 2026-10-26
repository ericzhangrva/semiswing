# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2402` -> Calibrated `0.2402` (Brier Skill Score: `0.0394`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.70 ; OOS: 3.47 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 37.52% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 37.52% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.41 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -19.8% ; DD: 20.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0394 ; SR Lift: +0.00 ; Sortino Lift: +0.04 ; CAGR Lift: +4.7% ; DD Red: -6.2% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.78 ; OOS: 3.52 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 36.41% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 36.41% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.40 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.9% ; DD: 20.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0394 ; SR Lift: +0.07 ; Sortino Lift: +0.12 ; CAGR Lift: +10.9% ; DD Red: -5.5% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 823.3 | 58.99 | 1.4 | 0.918 | 1.45 | 31.31 | 25.7 | 96 | 51.0 | 3.32 | 1.51 |
| ML (SMH Bull Core + Swing) | 922.46 | 62.41 | 1.41 | 0.925 | 1.49 | 37.52 | 25.7 | 94 | 47.9 | 3.47 | 1.61 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 372.16 | 38.24 | 1.02 | 0.712 | 1.02 | 38.53 | 27.6 | 89 | 52.8 | 2.75 | 1.16 |
| `Baseline (Adaptive `L_t`)` | 622.96 | 51.08 | 1.33 | 0.893 | 1.39 | 30.95 | 25.7 | 95 | 50.5 | 3.36 | 1.48 |
| ML (LightGBM + Platt) | 810.08 | 58.52 | 1.4 | 0.922 | 1.51 | 36.41 | 25.7 | 94 | 47.9 | 3.52 | 1.61 |
| Pure Pre-2022 Semi (Cash Swing) | 286.61 | 32.59 | 0.95 | 0.66 | 0.98 | 35.6 | 27.6 | 90 | 52.2 | 2.76 | 1.14 |
| Baseline (Fixed 20d) | 658.96 | 52.62 | 1.32 | 0.888 | 1.39 | 34.9 | 25.7 | 99 | 46.5 | 3.77 | 1.6 |
| SMH Buy & Hold | 253.82 | 30.16 | 0.79 | 0.524 | 0.78 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 178.79 | 23.85 | 0.64 | 0.395 | 0.63 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 116.26 | 17.46 | 0.59 | 0.357 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 82.73 | 13.4 | 0.49 | 0.274 | 0.48 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 99.8 | 15.53 | 0.52 | 0.302 | 0.51 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 41.67 | 7.54 | 0.26 | 0.136 | 0.26 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 70.69 | 11.8 | 0.5 | 0.285 | 0.5 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 21.0 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

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
| Baseline (SMH Bull Core + Swing) | 1061.4 | 90.74 | 1.76 | 0.959 | 1.77 | 31.31 | 9.0 | 81 | 60.5 | 3.56 | 1.91 |
| ML (SMH Bull Core + Swing) | 1174.55 | 95.46 | 1.76 | 0.961 | 1.81 | 37.52 | 8.9 | 77 | 58.4 | 3.7 | 2.09 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 498.1 | 60.16 | 1.34 | 0.821 | 1.32 | 38.53 | 11.3 | 75 | 62.7 | 3.14 | 1.5 |
| `Baseline (Adaptive `L_t`)` | 807.2 | 78.72 | 1.69 | 0.947 | 1.73 | 30.95 | 9.0 | 80 | 60.0 | 3.67 | 1.88 |
| ML (LightGBM + Platt) | 1035.9 | 89.62 | 1.76 | 0.961 | 1.85 | 36.41 | 8.9 | 77 | 58.4 | 3.78 | 2.09 |
| Pure Pre-2022 Semi (Cash Swing) | 388.55 | 51.85 | 1.28 | 0.79 | 1.3 | 35.6 | 11.3 | 76 | 61.8 | 3.21 | 1.47 |
| Baseline (Fixed 20d) | 800.36 | 78.37 | 1.63 | 0.932 | 1.68 | 34.9 | 9.2 | 86 | 53.5 | 4.08 | 1.92 |
| SMH Buy & Hold | 448.27 | 56.53 | 1.31 | 0.812 | 1.29 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 342.33 | 47.92 | 1.1 | 0.685 | 1.09 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 213.17 | 35.07 | 1.2 | 0.749 | 1.14 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 175.49 | 30.58 | 1.21 | 0.755 | 1.19 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 215.1 | 35.29 | 1.18 | 0.739 | 1.15 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 117.2 | 22.66 | 0.74 | 0.414 | 0.74 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 110.69 | 21.68 | 1.09 | 0.682 | 1.09 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.56 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.33% | +120.60% | 53.3% | 1.69 | 1.70 | -30.95% | 0.5% | 18 | 50.0% | 1.46 | +0.70R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.89% | -19.96% | 9.4% | -2.56 | -2.04 | -20.11% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +44.03% | +44.45% | 20.5% | 1.66 | 1.73 | -19.30% | 6.0% | 25 | 68.0% | 4.11 | +0.89R |
| 2024 | +85.83% | +85.83% | 31.4% | 1.98 | 2.22 | -23.38% | 7.5% | 22 | 59.1% | 5.27 | +1.18R |
| 2025 | +135.09% | +136.70% | 35.2% | 2.52 | 2.86 | -18.43% | 20.4% | 12 | 58.3% | 34.58 | +8.39R |
| 2026 | +74.28% | +97.95% | 59.4% | 1.39 | 1.40 | -36.41% | 0.0% | 18 | 44.4% | 1.17 | +0.68R |
