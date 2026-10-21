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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.81 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.968 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.75 ; OOS: 3.52 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.53% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.53% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.45 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -18.9% ; DD: 19.3% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.00 ; Sortino Lift: +0.05 ; CAGR Lift: +4.7% ; DD Red: -5.2% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.77 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.964 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.83 ; OOS: 3.57 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.99% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.99% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.41 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.0% ; DD: 19.4% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0393 ; SR Lift: +0.06 ; Sortino Lift: +0.09 ; CAGR Lift: +10.3% ; DD Red: -5.0% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 855.86 | 60.34 | 1.44 | 0.929 | 1.25 | 30.38 | 25.7 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 957.31 | 63.75 | 1.45 | 0.935 | 1.29 | 35.53 | 25.7 | 92 | 47.8 | 3.52 | 1.64 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 381.45 | 38.91 | 1.05 | 0.733 | 0.9 | 37.84 | 27.4 | 88 | 53.4 | 3.03 | 1.18 |
| `Baseline (Adaptive `L_t`)` | 626.57 | 51.4 | 1.35 | 0.9 | 1.19 | 30.96 | 25.7 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 803.49 | 58.46 | 1.41 | 0.925 | 1.27 | 35.99 | 25.7 | 92 | 47.8 | 3.57 | 1.64 |
| Pure Pre-2022 Semi (Cash Swing) | 290.65 | 32.97 | 0.98 | 0.678 | 0.84 | 35.54 | 27.4 | 89 | 52.8 | 3.01 | 1.16 |
| Baseline (Fixed 20d) | 659.66 | 52.81 | 1.34 | 0.894 | 1.19 | 34.91 | 25.8 | 98 | 46.9 | 3.84 | 1.62 |
| SMH Buy & Hold | 261.98 | 30.87 | 0.82 | 0.548 | 0.81 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 187.31 | 24.7 | 0.67 | 0.42 | 0.67 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 118.4 | 17.75 | 0.62 | 0.379 | 0.6 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 86.12 | 13.87 | 0.53 | 0.303 | 0.51 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 103.0 | 15.96 | 0.56 | 0.326 | 0.55 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 39.18 | 7.16 | 0.26 | 0.138 | 0.26 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 72.53 | 12.08 | 0.54 | 0.317 | 0.54 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.2 | 3.56 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -19.57 | -19.64 | -2.71 | 0.0 | -0.84 | 19.79 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -18.86 | -18.93 | -2.57 | 0.0 | -0.8 | 19.33 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -20.13 | -20.21 | -2.65 | 0.0 | -0.82 | 20.36 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -19.37 | -19.44 | -2.73 | 0.0 | -0.84 | 19.6 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -18.96 | -19.03 | -2.59 | 0.0 | -0.81 | 19.44 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (Cash Swing) | -19.94 | -20.01 | -2.66 | 0.0 | -0.82 | 20.16 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| Baseline (Fixed 20d) | -14.72 | -14.77 | -2.44 | 0.0 | -0.79 | 14.96 | 88.8 | 13 | 0.0 | 0.0 | -0.56 |
| SMH Buy & Hold | -34.97 | -35.08 | -0.89 | 0.0 | -0.9 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | -36.35 | -36.47 | -0.91 | 0.0 | -0.92 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | -30.28 | -30.38 | -1.0 | 0.0 | -1.03 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | -33.22 | -33.33 | -1.21 | 0.0 | -1.23 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | -36.62 | -36.74 | -1.24 | 0.0 | -1.28 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | -34.91 | -35.02 | -1.04 | 0.0 | -1.06 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | -18.65 | -18.71 | -0.88 | 0.0 | -0.91 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 3.53 | 3.55 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 5. View B — Modern AI Cycle (`2023–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 1088.29 | 92.28 | 1.81 | 0.966 | 1.72 | 30.38 | 8.9 | 78 | 60.3 | 3.59 | 1.98 |
| ML (SMH Bull Core + Swing) | 1202.86 | 97.02 | 1.81 | 0.968 | 1.77 | 35.53 | 8.9 | 75 | 58.7 | 3.75 | 2.15 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 502.74 | 60.72 | 1.37 | 0.839 | 1.3 | 37.84 | 11.0 | 74 | 63.5 | 3.5 | 1.53 |
| `Baseline (Adaptive `L_t`)` | 800.99 | 78.73 | 1.71 | 0.952 | 1.66 | 30.96 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 1014.74 | 89.07 | 1.77 | 0.964 | 1.75 | 35.99 | 8.9 | 75 | 58.7 | 3.83 | 2.15 |
| Pure Pre-2022 Semi (Cash Swing) | 387.85 | 51.99 | 1.31 | 0.806 | 1.24 | 35.54 | 11.0 | 75 | 62.7 | 3.57 | 1.5 |
| Baseline (Fixed 20d) | 790.61 | 78.18 | 1.65 | 0.936 | 1.61 | 34.91 | 9.2 | 85 | 54.1 | 4.16 | 1.95 |
| SMH Buy & Hold | 460.91 | 57.7 | 1.36 | 0.838 | 1.35 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 355.83 | 49.29 | 1.15 | 0.719 | 1.14 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 216.27 | 35.55 | 1.26 | 0.782 | 1.2 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 180.6 | 31.33 | 1.29 | 0.8 | 1.27 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 220.15 | 35.98 | 1.25 | 0.776 | 1.22 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 113.37 | 22.16 | 0.76 | 0.429 | 0.76 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 112.98 | 22.1 | 1.18 | 0.741 | 1.18 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 14.15 | 3.56 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.37% | -19.44% | 9.1% | -2.73 | -0.84 | -19.60% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +38.78% | +39.14% | 20.3% | 1.56 | 1.57 | -20.15% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.40% | +86.40% | 32.4% | 1.98 | 2.09 | -22.01% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +76.62% | +77.42% | 32.2% | 1.84 | 1.58 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.63% | +123.63% | 53.7% | 1.71 | 1.71 | -30.96% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -18.96% | -19.03% | 9.4% | -2.59 | -0.81 | -19.44% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +43.33% | +43.74% | 20.4% | 1.71 | 1.76 | -19.43% | 6.0% | 25 | 68.0% | 4.09 | +0.89R |
| 2024 | +84.82% | +84.82% | 31.4% | 2.01 | 2.11 | -23.47% | 7.5% | 22 | 59.1% | 5.23 | +1.18R |
| 2025 | +132.46% | +134.03% | 35.1% | 2.51 | 2.41 | -18.81% | 20.4% | 12 | 58.3% | 33.02 | +8.39R |
| 2026 | +74.76% | +100.66% | 59.8% | 1.41 | 1.42 | -35.99% | 0.0% | 16 | 43.8% | 1.19 | +0.79R |
