# SemiSwing Walk-Forward Backtest Report (2022–2026 Out-of-Sample)

- **Data Health Score:** `100.0/100`
- **Warmup Training Period:** `2018-01-01` to `2021-12-31`
- **Out-of-Sample Walk-Forward Period:** `2022-01-01` to Present
- **Platt Calibration OOF Brier Score:** Raw `0.2408` -> Calibrated `0.2408` (Brier Skill Score: `0.0368`)

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
| `Gate 1: Modern AI Era Sharpe >= 1.60 (2023-2026)` | 1.82 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.969 | PASS |
| `Gate 3: Profit Factor >= 2.00 (Gross Payoff Asymmetry)` | AI: 3.70 ; OOS: 3.46 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 40.25% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 40.25% | FAIL |
| `Gate 5: Full OOS Sharpe >= 1.20 (2022-2026 Full Cycle)` | 1.46 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -40%, DD <= 40%, Cash >= 80%)` | Ret: -21.4% ; DD: 21.6% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0368 ; SR Lift: +0.07 ; Sortino Lift: +0.08 ; CAGR Lift: +8.6% ; DD Red: -9.2% | PASS |

### 2.2 Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Institutional Gate | Realized Metric | Gate Status |
| --- | --- | --- |
| `Gate 1: Modern AI Era Sharpe >= 1.50 (2023-2026)` | 1.76 | PASS |
| `Gate 2: Deflated Sharpe Probability >= 0.95 (K=14 trials)` | 0.961 | PASS |
| `Gate 3: Profit Factor >= 1.50 (Gross Payoff Asymmetry)` | AI: 3.82 ; OOS: 3.53 | PASS |
| `Gate 4a: Modern AI Era Max DD <= 36.0% (vs SMH 35.7%)` | 39.77% | FAIL |
| `Gate 4b: Full OOS Max DD <= 40.0% (vs SMH 45.1%)` | 39.77% | PASS |
| `Gate 5: Full OOS Sharpe >= 1.00 (2022-2026 Full Cycle)` | 1.39 | PASS |
| `Gate 6: 2022 Bear Stress (Ret >= -25%, DD <= 25%, Cash >= 80%)` | Ret: -21.5% ; DD: 21.7% ; Cash: 89.6% | PASS |
| `Gate 7: ML Alpha Dominance & Calibration (BSS > 0.02 & SR Lift >= +0.05 or Sortino Lift >= +0.02 or CAGR Lift >= +3.0% or DD Red >= 1.5%)` | BSS: 0.0368 ; SR Lift: +0.08 ; Sortino Lift: +0.09 ; CAGR Lift: +8.4% ; DD Red: -8.8% | PASS |

## 3. Full Out-of-Sample Walk-Forward (`2022–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | 821.23 | 59.04 | 1.4 | 0.917 | 1.44 | 31.08 | 25.7 | 93 | 50.5 | 3.34 | 1.56 |
| ML (SMH Bull Core + Swing) | 977.28 | 64.33 | 1.46 | 0.935 | 1.51 | 40.25 | 25.7 | 92 | 46.7 | 3.46 | 1.81 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 357.11 | 37.38 | 1.0 | 0.698 | 1.01 | 38.07 | 27.4 | 89 | 52.8 | 2.77 | 1.16 |
| `Baseline (Adaptive `L_t`)` | 622.4 | 51.16 | 1.32 | 0.891 | 1.39 | 30.95 | 25.7 | 92 | 50.0 | 3.38 | 1.53 |
| ML (LightGBM + Platt) | 747.51 | 56.29 | 1.39 | 0.916 | 1.46 | 39.77 | 25.7 | 91 | 46.2 | 3.53 | 1.83 |
| Pure Pre-2022 Semi (Cash Swing) | 287.27 | 32.7 | 0.95 | 0.661 | 0.98 | 35.52 | 27.4 | 90 | 52.2 | 2.77 | 1.14 |
| Baseline (Fixed 20d) | 688.84 | 53.97 | 1.35 | 0.903 | 1.43 | 33.73 | 25.8 | 98 | 48.0 | 4.14 | 1.63 |
| SMH Buy & Hold | 242.74 | 29.35 | 0.77 | 0.509 | 0.77 | 45.14 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 169.89 | 23.05 | 0.62 | 0.381 | 0.62 | 45.52 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 112.04 | 17.01 | 0.58 | 0.344 | 0.56 | 34.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 80.97 | 13.2 | 0.48 | 0.268 | 0.47 | 34.83 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 97.19 | 15.24 | 0.51 | 0.295 | 0.51 | 42.02 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 38.41 | 7.03 | 0.24 | 0.128 | 0.24 | 38.49 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 70.29 | 11.77 | 0.5 | 0.284 | 0.5 | 24.5 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 20.96 | 4.06 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. View A — 2022 Bear Market Stress Test (`2022`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (SMH Bull Core + Swing) | -20.51 | -20.59 | -2.68 | 0.0 | -2.12 | 20.77 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (SMH Bull Core + Swing) | -21.36 | -21.43 | -2.54 | 0.0 | -2.0 | 21.57 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | -21.07 | -21.14 | -2.63 | 0.0 | -2.07 | 21.33 | 89.6 | 14 | 0.0 | 0.0 | -0.68 |
| `Baseline (Adaptive `L_t`)` | -20.32 | -20.39 | -2.7 | 0.0 | -2.13 | 20.59 | 89.6 | 15 | 0.0 | 0.0 | -0.62 |
| ML (LightGBM + Platt) | -21.47 | -21.55 | -2.56 | 0.0 | -2.01 | 21.68 | 89.6 | 17 | 0.0 | 0.0 | -0.62 |
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
| Baseline (SMH Bull Core + Swing) | 1058.79 | 90.88 | 1.75 | 0.958 | 1.77 | 31.08 | 8.9 | 78 | 60.3 | 3.58 | 1.98 |
| ML (SMH Bull Core + Swing) | 1269.61 | 99.49 | 1.82 | 0.969 | 1.85 | 40.25 | 8.9 | 75 | 57.3 | 3.7 | 2.37 |
| Pure Pre-2022 Semi (SMH Bull Core + Swing) | 479.04 | 58.95 | 1.32 | 0.811 | 1.3 | 38.07 | 11.1 | 75 | 62.7 | 3.16 | 1.5 |
| `Baseline (Adaptive `L_t`)` | 806.5 | 78.91 | 1.68 | 0.946 | 1.73 | 30.95 | 8.9 | 77 | 59.7 | 3.69 | 1.95 |
| ML (LightGBM + Platt) | 979.04 | 87.32 | 1.76 | 0.961 | 1.82 | 39.77 | 8.9 | 74 | 56.8 | 3.82 | 2.4 |
| Pure Pre-2022 Semi (Cash Swing) | 389.39 | 52.05 | 1.28 | 0.791 | 1.3 | 35.52 | 11.1 | 76 | 61.8 | 3.23 | 1.47 |
| Baseline (Fixed 20d) | 835.8 | 80.41 | 1.67 | 0.943 | 1.73 | 33.73 | 9.2 | 85 | 55.3 | 4.5 | 1.97 |
| SMH Buy & Hold | 431.09 | 55.37 | 1.29 | 0.801 | 1.28 | 35.74 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| SOXX Buy & Hold | 328.2 | 46.78 | 1.08 | 0.67 | 1.07 | 41.36 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| VGT Buy & Hold | 207.06 | 34.45 | 1.18 | 0.735 | 1.13 | 27.23 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| QQQ Buy & Hold | 172.84 | 30.32 | 1.2 | 0.748 | 1.18 | 22.77 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| AIQ Buy & Hold | 210.98 | 34.9 | 1.17 | 0.731 | 1.14 | 26.35 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| IGV Buy & Hold | 112.19 | 21.96 | 0.72 | 0.396 | 0.71 | 36.61 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| S&P 500 (SPY) Buy & Hold | 110.2 | 21.66 | 1.09 | 0.68 | 1.08 | 18.76 | 0.0 | 0 | 0.0 | 0.0 | 0.0 |
| 3M T-Bill Cash (DTB3) | 18.53 | 4.59 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0 | 0.0 | 0.0 | 0.0 |

## 6. Yearly Breakdown — Baseline (Adaptive `L_t`, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -20.32% | -20.39% | 9.1% | -2.70 | -2.13 | -20.59% | 89.6% | 15 | 0.0% | 0.00 | -0.62R |
| 2023 | +39.21% | +39.58% | 20.3% | 1.50 | 1.53 | -20.05% | 6.0% | 24 | 70.8% | 3.47 | +1.04R |
| 2024 | +86.75% | +86.75% | 33.0% | 1.91 | 2.09 | -23.09% | 7.5% | 22 | 63.6% | 5.03 | +1.24R |
| 2025 | +77.04% | +77.85% | 32.2% | 1.83 | 1.84 | -16.39% | 20.4% | 16 | 50.0% | 9.77 | +5.31R |
| 2026 | +90.37% | +122.37% | 53.5% | 1.70 | 1.70 | -30.95% | 0.0% | 15 | 46.7% | 1.45 | +0.84R |

## 7. Yearly Breakdown — ML (LightGBM + Platt, Cash + T-Bill Interest)

| Year | Total Return (%) | CAGR (%) | Ann. Vol (%) | Sharpe | Sortino | Max Drawdown (%) | 100% Cash Days (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | -21.47% | -21.55% | 10.1% | -2.56 | -2.01 | -21.68% | 89.6% | 17 | 0.0% | 0.00 | -0.62R |
| 2023 | +43.30% | +43.71% | 20.5% | 1.63 | 1.70 | -19.37% | 6.0% | 25 | 68.0% | 4.15 | +0.88R |
| 2024 | +99.93% | +99.93% | 31.8% | 2.19 | 2.40 | -23.42% | 7.5% | 21 | 61.9% | 5.48 | +1.54R |
| 2025 | +110.26% | +111.52% | 31.8% | 2.40 | 2.72 | -18.58% | 20.4% | 12 | 58.3% | 24.21 | +8.39R |
| 2026 | +72.87% | +97.29% | 58.5% | 1.40 | 1.37 | -39.77% | 0.0% | 16 | 31.2% | 1.36 | +1.40R |
