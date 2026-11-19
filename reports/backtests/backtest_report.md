# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2402` -> Calibrated `0.2402` (Brier Skill Score: `0.0392`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.73 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.958 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.80 ; OOS: 3.56 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 38.0% (vs SMH 35.7%)` | 37.46% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 37.46% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.39 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -19.8% ; DD: 20.0% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0392 ; SR Lift: +0.05 ; Sortino Lift: +0.10 ; CAGR Lift: +7.3% ; DD Red: -1.8% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.74 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.89 ; OOS: 3.62 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 38.0% (vs SMH 35.7%)` | 36.16% | PASS |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 36.16% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.39 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -19.9% ; DD: 20.1% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0392 ; SR Lift: +0.13 ; Sortino Lift: +0.16 ; CAGR Lift: +13.5% ; DD Red: -0.4% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 761.47 | 55.68 | 1.34 | 0.899 | 1.37 | 35.7 | 26.8 | 97 | 49.5 | 2.79 | 1.47 |
| ML (SMH Bull Core + Swing) | 910.01 | 60.86 | 1.39 | 0.92 | 1.46 | 37.46 | 26.8 | 95 | 46.3 | 3.56 | 1.58 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 354.0 | 36.48 | 0.98 | 0.69 | 0.98 | 38.63 | 28.6 | 89 | 52.8 | 2.75 | 1.16 |
| `Baseline (Adaptive `L_t`)` | 575.35 | 48.08 | 1.27 | 0.87 | 1.32 | 35.77 | 26.8 | 96 | 49.0 | 2.87 | 1.45 |
| ML (LightGBM + Platt) | 805.85 | 57.3 | 1.39 | 0.921 | 1.48 | 36.16 | 26.8 | 95 | 46.3 | 3.62 | 1.58 |
| Pure Pre-2022 Semi (Cash Swing) | 287.74 | 32.12 | 0.94 | 0.66 | 0.97 | 35.6 | 28.6 | 90 | 52.2 | 2.76 | 1.14 |
| Baseline (Fixed 20d) | 762.35 | 55.71 | 1.45 | 0.939 | 1.57 | 26.36 | 26.5 | 97 | 49.5 | 4.45 | 1.46 |
| SMH Buy & Hold | 194.05 | 24.82 | 0.67 | 0.426 | 0.66 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 135.31 | 19.23 | 0.54 | 0.318 | 0.53 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 88.81 | 13.96 | 0.48 | 0.269 | 0.45 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 66.45 | 11.04 | 0.39 | 0.213 | 0.38 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 73.9 | 12.04 | 0.41 | 0.223 | 0.4 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 23.0 | 4.35 | 0.15 | 0.093 | 0.15 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 60.66 | 10.24 | 0.42 | 0.229 | 0.41 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 21.35 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -19.81 | -19.88 | -2.55 | 0.0 | -2.03 | 20.03 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -19.92 | -19.99 | -2.57 | 0.0 | -2.04 | 20.13 | 89.6 | 17 | 0.0 | 0.0 | -0.6 |
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
| Baseline (SMH Bull Core + Swing) | 983.63 | 85.13 | 1.68 | 0.947 | 1.68 | 35.7 | 10.7 | 82 | 58.5 | 2.96 | 1.86 |
| ML (SMH Bull Core + Swing) | 1159.36 | 92.46 | 1.73 | 0.958 | 1.78 | 37.46 | 10.7 | 78 | 56.4 | 3.8 | 2.06 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 475.09 | 57.17 | 1.29 | 0.803 | 1.27 | 38.63 | 12.9 | 75 | 62.7 | 3.14 | 1.5 |
| `Baseline (Adaptive `L_t`)` | 747.45 | 73.73 | 1.61 | 0.933 | 1.65 | 35.77 | 10.7 | 81 | 58.0 | 3.09 | 1.83 |
| ML (LightGBM + Platt) | 1030.95 | 87.19 | 1.74 | 0.961 | 1.81 | 36.16 | 10.7 | 78 | 56.4 | 3.89 | 2.06 |
| Pure Pre-2022 Semi (Cash Swing) | 389.98 | 50.79 | 1.26 | 0.79 | 1.28 | 35.6 | 12.9 | 76 | 61.8 | 3.21 | 1.47 |
| Baseline (Fixed 20d) | 923.01 | 82.4 | 1.79 | 0.967 | 1.9 | 26.36 | 10.5 | 84 | 57.1 | 4.84 | 1.78 |
| SMH Buy & Hold | 355.65 | 47.99 | 1.14 | 0.714 | 1.11 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 273.34 | 40.56 | 0.95 | 0.582 | 0.92 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 173.42 | 29.69 | 1.01 | 0.627 | 0.95 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 150.95 | 26.85 | 1.04 | 0.651 | 1.01 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 174.25 | 29.79 | 1.0 | 0.619 | 0.96 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 88.58 | 17.82 | 0.59 | 0.304 | 0.58 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 98.32 | 19.36 | 0.95 | 0.583 | 0.94 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.91 | 4.58 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.75% | +86.75% | 33.0% | 1.91 | 2.09 | -23.09% | 7.5% | 22 | 63.6% | 5.03 | +1.24R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +77.97% | +91.82% | 51.3% | 1.46 | 1.45 | -35.77% | 8.5% | 19 | 42.1% | 1.10 | +0.56R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -19.92% | -19.99% | 9.3% | -2.57 | -2.04 | -20.13% | 89.6% | 17 | 0.0% | 0.00 | -0.60R |
| 2023 | +44.25% | +44.68% | 20.3% | 1.68 | 1.76 | -18.76% | 6.0% | 25 | 68.0% | 4.23 | +0.89R |
| 2024 | +81.83% | +81.83% | 32.0% | 1.88 | 2.04 | -24.16% | 7.5% | 23 | 56.5% | 4.89 | +1.10R |
| 2025 | +136.42% | +138.05% | 35.2% | 2.54 | 2.87 | -18.32% | 20.4% | 12 | 58.3% | 35.36 | +8.39R |
| 2026 | +76.11% | +89.56% | 56.6% | 1.35 | 1.36 | -36.16% | 8.5% | 18 | 38.9% | 1.17 | +0.68R |
