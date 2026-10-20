# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2401` -> Calibrated `0.2401` (Brier Skill Score: `0.0397`)

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
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.965 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.70 ; OOS: 3.46 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.38% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.38% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.43 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -20.9% ; DD: 21.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0397 ; SR Lift: +0.01 ; Sortino Lift: +0.06 ; CAGR Lift: +5.6% ; DD Red: -5.0% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.960 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.78 ; OOS: 3.51 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 35.75% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 35.75% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.39 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -21.0% ; DD: 21.2% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0397 ; SR Lift: +0.07 ; Sortino Lift: +0.09 ; CAGR Lift: +10.2% ; DD Red: -5.0% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 839.5 | 59.88 | 1.42 | 0.922 | 1.46 | 30.38 | 25.8 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 942.05 | 63.39 | 1.43 | 0.929 | 1.51 | 35.38 | 25.8 | 92 | 47.8 | 3.46 | 1.64 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 370.17 | 38.3 | 1.02 | 0.712 | 1.03 | 37.84 | 27.4 | 87 | 54.0 | 3.19 | 1.2 |
| `Baseline (Adaptive `L_t`)` | 623.3 | 51.36 | 1.33 | 0.893 | 1.4 | 30.79 | 25.8 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 783.8 | 57.85 | 1.39 | 0.917 | 1.48 | 35.75 | 25.8 | 91 | 47.3 | 3.51 | 1.65 |
| Pure Pre-2022 Semi (Cash Swing) | 288.01 | 32.85 | 0.96 | 0.662 | 0.98 | 35.52 | 27.4 | 88 | 53.4 | 3.14 | 1.18 |
| Baseline (Fixed 20d) | 654.27 | 52.69 | 1.32 | 0.887 | 1.39 | 34.9 | 25.9 | 96 | 45.8 | 3.79 | 1.64 |
| SMH Buy & Hold | 256.31 | 30.5 | 0.8 | 0.529 | 0.79 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 182.25 | 24.28 | 0.65 | 0.402 | 0.64 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 114.76 | 17.36 | 0.59 | 0.353 | 0.57 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 84.03 | 13.63 | 0.5 | 0.28 | 0.49 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 99.55 | 15.57 | 0.53 | 0.302 | 0.52 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 34.86 | 6.47 | 0.22 | 0.12 | 0.22 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 70.95 | 11.89 | 0.51 | 0.288 | 0.5 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.9 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -20.87 | -20.95 | -2.54 | 0.0 | -2.01 | 21.09 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -20.96 | -21.03 | -2.56 | 0.0 | -2.02 | 21.17 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
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
| Baseline (SMH Bull Core + Swing) | 1081.78 | 92.27 | 1.78 | 0.961 | 1.79 | 30.38 | 8.9 | 78 | 60.3 | 3.59 | 1.98 |
| ML (SMH Bull Core + Swing) | 1216.73 | 97.85 | 1.79 | 0.965 | 1.85 | 35.38 | 8.9 | 75 | 58.7 | 3.7 | 2.15 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 495.58 | 60.37 | 1.34 | 0.822 | 1.33 | 37.84 | 11.0 | 73 | 64.4 | 3.71 | 1.56 |
| `Baseline (Adaptive `L_t`)` | 807.63 | 79.29 | 1.69 | 0.947 | 1.74 | 30.79 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 1017.96 | 89.46 | 1.76 | 0.96 | 1.83 | 35.75 | 8.9 | 74 | 58.1 | 3.78 | 2.18 |
| Pure Pre-2022 Semi (Cash Swing) | 390.32 | 52.33 | 1.28 | 0.792 | 1.31 | 35.52 | 11.0 | 74 | 63.5 | 3.75 | 1.53 |
| Baseline (Fixed 20d) | 794.79 | 78.62 | 1.63 | 0.931 | 1.68 | 34.9 | 9.2 | 83 | 53.0 | 4.11 | 1.99 |
| SMH Buy & Hold | 452.13 | 57.19 | 1.33 | 0.818 | 1.31 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 347.8 | 48.71 | 1.12 | 0.694 | 1.11 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 211.0 | 35.03 | 1.2 | 0.746 | 1.15 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 177.45 | 31.01 | 1.22 | 0.764 | 1.21 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 214.71 | 35.46 | 1.19 | 0.74 | 1.16 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 106.76 | 21.2 | 0.7 | 0.377 | 0.69 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 111.02 | 21.86 | 1.1 | 0.686 | 1.1 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.47 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.93% | +86.93% | 32.4% | 1.95 | 2.15 | -21.93% | 7.5% | 22 | 63.6% | 5.06 | +1.25R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.42% | +125.14% | 53.9% | 1.71 | 1.71 | -30.79% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.96% | -21.03% | 9.9% | -2.56 | -2.02 | -21.17% | 89.6% | 17 | 0.0% | 0.00 | -0.62R |
| 2023 | +47.15% | +47.61% | 20.8% | 1.74 | 1.84 | -19.19% | 6.0% | 25 | 68.0% | 4.30 | +0.89R |
| 2024 | +85.72% | +85.72% | 32.0% | 1.95 | 2.17 | -23.59% | 7.5% | 22 | 59.1% | 5.07 | +1.18R |
| 2025 | +124.09% | +125.54% | 34.1% | 2.45 | 2.72 | -18.02% | 20.4% | 12 | 58.3% | 32.52 | +8.39R |
| 2026 | +76.13% | +104.06% | 60.0% | 1.43 | 1.44 | -35.75% | 0.0% | 15 | 40.0% | 1.14 | +0.81R |
