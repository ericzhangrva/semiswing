# SemiSwing

SemiSwing is a systematic momentum swing trading, walk-forward backtesting, and daily portfolio recommendation system focused on US Semiconductor & AI infrastructure leaders and unleveraged sector/index benchmark ETFs (`SMH`, `SOXX`, `VGT`, `QQQ`, `SPY`, `AIQ`, `IGV`). 

Unallocated portfolio cash earns daily risk-free interest indexed to the 3-Month US Treasury Bill rate (`FRED DTB3`), with an **SMH Bull Core + Swing** sleeve that holds `SMH` during confirmed secular semiconductor bull markets.

- **Live Cloud Dashboard:** [https://semiswing.pages.dev/](https://semiswing.pages.dev/)
- **Live Daily Trade Tickets (Passcode-Protected):** [`https://semiswing.pages.dev/daily/latest_recommendations.html`](https://semiswing.pages.dev/daily/latest_recommendations.html)
- **Live Interactive Backtest Report:** [`https://semiswing.pages.dev/backtests/backtest_report.html`](https://semiswing.pages.dev/backtests/backtest_report.html)
- **Static Markdown Backtest Report:** [`reports/backtests/backtest_report.md`](reports/backtests/backtest_report.md)
- **AI Implementation Specification:** [docs/instruction.md](docs/instruction.md)

---

## 1. Backtest Assumptions & Causal Integrity Controls

Quantitative backtests frequently suffer from subtle biases (look-ahead peeking, survivorship bias, unrealistic execution timing, and post-hoc parameter overfitting). SemiSwing enforces strict causal hygiene controls to ensure every reported return reflects institutional execution reality:

### 1.1 Realistic Next-Day Execution (Zero Close-Fill Illusion)
- **Next-Day Market Open Fills (09:30 ET):** Signals generated at the close of trading day $t$ (16:00 ET) are executed strictly at the **Market Open of day $t+1$ (09:30 ET)** using that day's real open price.
- **Transaction Costs & Slippage:** A realistic friction of **$5.0\text{ bps slippage} + 2.0\text{ bps commission} = 7.0\text{ bps}$** round-turn is subtracted from every execution.
- **Gap-Up Protection:** New entries are blocked if the stock opens $> 1.0\times\text{ATR}$ above signal close or gaps up $> +4.0\%$ overnight, preventing chasing opening spikes.
- **Premarket Gap-Down Abort (09:15–09:30 ET):** If the semiconductor benchmark (`SMH`) opens or gaps down $< -1.5\%$, all pending candidate buy orders are cancelled.

### 1.2 Two-Stage Dynamic Point-in-Time (PIT) Universe Reconstitution
To eliminate look-ahead selection bias and survivorship bias, the tradeable universe is reconstituted dynamically at the start of each calendar quarter $t_k \in \{\text{Jan 1, Apr 1, Jul 1, Oct 1}\}$ strictly using trailing market data ending at $t_k - 1$:
1. **Stage 1 (Institutional Liquidity Floor at $t_k - 1$):**
   - Active US-listed semiconductor & tech equities in `universe.all_panel_stocks`.
   - Listing history $\ge 60$ trading days since listing/IPO (eliminates unseasoned listings).
   - $\text{Close}_{t_k - 1} \ge 15.00$ ($\$15.00$, eliminates penny stocks).
   - Trailing 60-day median daily dollar volume:
     $$\text{MedDollarVol}_{60d} = \text{median}_{t \in [t_k - 60, t_k - 1]}\!\left(\text{Close}_t \times \text{Volume}_t\right) \ge 150{,}000{,}000.0$$
   - Volatility condition: 20-day $\text{ATR}_{\text{pct}, 20d, t_k - 1} > 0$.
2. **Stage 2 (Swing Tradability Ranking at $t_k - 1$):**
   $$\text{SwingRankScore}_{i, t_k - 1} = \log_{10}\!\left(\text{MedDollarVol}_{60d}\right) \times \text{ATR}_{\text{pct}, 20d, t_k - 1}$$
   - The $\log_{10}$ compression scales volume variation down to a $1.28\times$ factor between mid-caps and mega-caps, allowing 20-day $\text{ATR\%}$ to prioritize high-velocity momentum leaders over sluggish value traps.
   - **Uncapped Selection (`pit_top_n = None`):** All qualifying tickers passing the Stage 1 liquidity floor receive `is_tradeable_universe = 1` for quarter $k$, naturally expanding from ~28 stocks in 2022 to ~50 in 2026 as the AI infrastructure ecosystem expanded (with Stage 2 tradability scores governing relative ranking and execution priority).
3. **Position Grace Rule:** Open positions held across quarterly boundaries are **never forcibly liquidated**; they remain managed under their stops and profit targets until natural exit, while new entries for dropped tickers are blocked.

### 1.3 Causal Macro Data & Volatility Hygiene
- **FRED Publication Lag:** All Federal Reserve economic series (`DTB3`, `DGS10`, `DTWEXBGS`, `VIXCLS`, `VXVCLS`, `BAMLH0A0HYM2`) are lagged by 1 business day (`shift(1)`) to account for publication schedules.
- **Fail-Closed Volatility Fallback:**
  $$\text{vix}_{\text{ts}} = \left(\frac{\text{VIX}}{\text{VIX3M}}\right).\text{fillna}(1.05)$$
  Missing volatility term structure data defaults to backwardation ($1.05$), immediately locking down long exposure.

### 1.4 Purged & Embargoed Machine Learning Validation
- **Expanding Walk-Forward Blocks:** The ML model retrains in 63-trading-day (~quarterly) blocks from 2022 to 2026.
- **López de Prado Purged K-Fold CV:** Inside each training block, cross-validation splits by unique dates ($K=5$) with a **20-day embargo** following each test fold, purging any observation whose triple-barrier span overlaps validation boundaries.
- **Causal Label Cutoff:** For any test block $[t_{\text{start}}, t_{\text{end}}]$, the training set is strictly restricted to observations where trade exit date satisfies $t_{\text{exit}} < t_{\text{start}}$ (`tb_end_date < t_start`), guaranteeing that every training trade outcome was completely settled prior to the test window.

### 1.5 The Control Benchmark (Pure Pre-2022 Semi)
To prove that outperformance is driven by signal extraction and macro regime gating rather than post-2022 IPO additions (`ARM`, `ALAB`, `GEV`, `NBIS`, `SNDK`), the backtest runs an ablation restricted strictly to **25 established pre-2022 `SMH`/`SOXX` constituents** (`NVDA, AVGO, AMD, TSM, ASML, MU, KLAC, LRCX, AMAT, MRVL, QCOM, TXN, ON, MCHP, INTC, SNPS, CDNS, MPWR, ADI, NXPI, TER, WDC, STX, ANET, COHR`).

---

## 2. Mathematical Formulations

### 2.1 Sample-Size Normalized OLS Trend Conviction (`slope_t_norm`)
Over a lookback window $L$, we fit the log-price regression $\ln C_i = \alpha + \beta t_i$ using Newey-West lag-1 HAC standard errors to account for residual autocorrelation. Because raw $t$-statistics scale with $\sqrt{L}$, we normalize to a constant 20-day baseline:
$$t_{\text{norm}} = t(\beta) \times \sqrt{\frac{20}{L}}$$
$$R^2 = 1.0 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

### 2.2 Volatility-Scaled Adaptive Window ($L_t$)
$$L_t = \text{clip}\left(\text{round}\left(20 \times \frac{\sigma_{250}}{\sigma_{20}}\right), 10, 60\right)$$
where $\sigma_n$ is the $n$-day sample standard deviation of daily log returns $\ln(C_t / C_{t-1})$.

### 2.3 Macro Regime Schmitt Trigger & Continuous Multiplier ($M_t$)
To prevent whipsaw churn near moving averages while avoiding recovery lag, regime transitions are governed by a dual-threshold hysteresis band on `SMH`:
- **Upper Unlock Band:** $SMH > \text{EMA200} \times 1.015$ **AND** $SMH > \text{EMA50} \implies \text{Regime} = 1$.
- **Lower Lockdown Band:** $SMH < \text{EMA200} \times 0.985 \implies \text{Regime} = 0$.
- **Inside Band:** Retains previous regime state.

The continuous macro multiplier $M_t$ scales capital allocation:
$$M_t = \begin{cases} 
0.0 & \text{if Regime} = 0 \;\lor\; \text{vix}_{\text{ts}} \ge 1.0 \;\lor\; \text{VIX} \ge 30.0 \quad \text{(Deep Bear / Crisis)} \\
0.5 & \text{if Regime} = 1 \;\land\; (\text{EMA50} < \text{EMA200} \;\lor\; \text{VIX} \ge 22.0) \quad \text{(Recovery / Transition)} \\
1.0 & \text{if Regime} = 1 \;\land\; \text{EMA50} \ge \text{EMA200} \;\land\; \text{VIX} < 22.0 \quad \text{(Confirmed Bull)}
\end{cases}$$

### 2.4 Continuous Meta-Labeling Sizing ($S_{i,t}$)
Following Marcos López de Prado's Meta-Labeling framework, shallow decision trees (`max_depth = 2`, `num_leaves = 4`, `min_child_samples = 60`) predict trade success probability $p_{i,t}$. Probabilities are mapped into out-of-fold empirical percentile ranks $q_{i,t} \in [0.0, 1.0]$:
$$q_{i,t} = \frac{1}{|OOF|} \sum_{j \in OOF} \mathbf{1}\{p_j \le p_{i,t}\}$$
$$S_{i,t} = 0.50 + 1.00 \times q_{i,t} \in [0.50, 1.50]$$

### 2.5 Hierarchical Two-Tier Risk Allocation
$$\text{Trade Risk Budget} = \text{Portfolio Equity} \times \text{Base Risk (1.0\%)} \times M_t \times S_{i,t}$$
$$\text{Position Dollar Cap} = \min\left(\text{Portfolio Equity} \times 35\% \times M_t \times S_{i,t},\;\text{Cash} \times 0.99\right)$$
$$\text{Shares} = \min\left(\left\lfloor \frac{\text{Trade Risk Budget}}{\text{Open Price} - \text{Initial Stop}} \right\rfloor,\; \left\lfloor \frac{\text{Position Dollar Cap}}{\text{Open Price}} \right\rfloor\right)$$

### 2.6 Deflated Sharpe Ratio (DSR)
Following David Bailey and Marcos López de Prado (2014), the Deflated Sharpe Ratio evaluates the statistical probability that the annualized Sharpe ratio $\widehat{\text{SR}}$ exceeds the expected maximum Sharpe ratio under the null hypothesis of zero skill given $K$ strategy trials:
$$\text{DSR} = \Phi\left( \frac{(\widehat{\text{SR}} - \text{SR}^*) \sqrt{T - 1}}{\sqrt{1 - \hat{\gamma}_3 \widehat{\text{SR}} + \frac{\hat{\gamma}_4 - 1}{4} \widehat{\text{SR}}^2}} \right)$$
where $\text{SR}^* = \sqrt{2 \ln K} + \frac{\gamma}{\sqrt{2 \ln K}}$, $\hat{\gamma}_3$ is return skewness, and $\hat{\gamma}_4$ is return kurtosis.

---

## 3. Walk-Forward Backtest Performance

Every execution is audited across the full Out-of-Sample period (`2022–2026`) and the Modern AI Cycle (`2023–2026`).

### 3.1 Modern AI Cycle (`2023–2026`)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | Trades | Win Rate (%) | Profit Factor | Avg R |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (SMH Bull Core + Swing)** | **1291.37%** | **100.91%** | **1.80** | **0.961** | **1.78** | **35.68%** | **75** | **62.7%** | **4.65** | **1.95R** |
| **ML (SMH Bull Core + Swing)** | **1517.44%** | **109.08%** | **1.86** | **0.974** | **1.93** | **33.70%** | **72** | **58.3%** | **5.23** | **2.10R** |
| **Baseline (Adaptive $L_t$, Cash Swing)** | **797.83%** | **78.89%** | **1.62** | **0.925** | **1.61** | **37.06%** | **74** | **62.2%** | **4.77** | **1.92R** |
| **ML (LightGBM + Platt, Cash Swing)** | **1034.59%** | **90.33%** | **1.73** | **0.954** | **1.79** | **35.52%** | **72** | **58.3%** | **5.45** | **2.10R** |
| **Pure Pre-2022 Semi (SMH Core + Swing)** | **803.58%** | **79.19%** | **1.57** | **0.913** | **1.58** | **36.23%** | **73** | **64.4%** | **3.69** | **1.56R** |
| **Pure Pre-2022 Semi (Cash Swing)** | **445.66%** | **56.77%** | **1.34** | **0.823** | **1.37** | **35.76%** | **74** | **63.5%** | **3.91** | **1.53R** |
| **SMH Buy & Hold (Benchmark)** | 462.58% | 58.12% | 1.34 | 0.826 | 1.33 | 35.74% | 0 | 0.0% | 0.00 | 0.00R |
| **SOXX Buy & Hold** | 359.21% | 49.83% | 1.14 | 0.707 | 1.13 | 41.36% | 0 | 0.0% | 0.00 | 0.00R |
| **VGT Buy & Hold** | 216.20% | 35.71% | 1.22 | 0.759 | 1.17 | 27.23% | 0 | 0.0% | 0.00 | 0.00R |
| **QQQ Buy & Hold** | 181.17% | 31.55% | 1.25 | 0.776 | 1.23 | 22.77% | 0 | 0.0% | 0.00 | 0.00R |
| **S&P 500 (SPY) Buy & Hold** | 112.48% | 22.13% | 1.12 | 0.696 | 1.11 | 18.76% | 0 | 0.0% | 0.00 | 0.00R |
| **3M T-Bill Cash (DTB3)** | 18.45% | 4.59% | 0.00 | 0.000 | 0.00 | 0.00% | 0 | 0.0% | 0.00 | 0.00R |

### 3.2 Full Out-of-Sample Window (`2022–2026`, Includes 2022 Bear Market)

| Strategy / Benchmark | Total Return (%) | CAGR (%) | Sharpe | Deflated SR Prob | Sortino | Max DD (%) | 100% Cash Days (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (SMH Bull Core + Swing)** | **767.45%** | **57.29%** | **1.30** | **0.872** | **1.31** | **37.77%** | **25.8%** |
| **ML (SMH Bull Core + Swing)** | **905.19%** | **62.23%** | **1.36** | **0.902** | **1.42** | **37.97%** | **25.8%** |
| **Baseline (Adaptive $L_t$, Cash Swing)** | **599.27%** | **50.34%** | **1.26** | **0.857** | **1.28** | **37.06%** | **25.8%** |
| **ML (LightGBM + Platt, Cash Swing)** | **779.94%** | **57.76%** | **1.36** | **0.904** | **1.44** | **35.52%** | **25.8%** |
| **Pure Pre-2022 Semi (Cash Swing)** | **326.01%** | **35.51%** | **1.00** | **0.698** | **1.04** | **35.76%** | **27.5%** |
| **SMH Buy & Hold** | 263.05% | 31.07% | 0.81 | 0.539 | 0.80 | 45.14% | 0.0% |
| **SOXX Buy & Hold** | 189.43% | 24.98% | 0.66 | 0.414 | 0.66 | 45.52% | 0.0% |
| **QQQ Buy & Hold** | 86.50% | 13.97% | 0.51 | 0.289 | 0.50 | 34.83% | 0.0% |
| **S&P 500 (SPY) Buy & Hold** | 72.13% | 12.07% | 0.52 | 0.294 | 0.51 | 24.50% | 0.0% |

### 3.3 Institutional Validation Gates (Two-Tier CI Architecture)

SemiSwing enforces strict institutional validation hurdles across two independent capital modes, verified via automated CI regression guardrails (`tests/test_institutional_gates.py`):

#### SMH Bull Core + Swing Mode (Active Secular Bull Core Sweep)

| Gate | Hurdle Requirement | Actual Modern AI Era | Status | Purpose & Benchmark Comparison |
| :--- | :---: | :---: | :---: | :--- |
| **Gate 1: Modern AI Era Sharpe** | $\text{Sharpe} \ge 1.60$ | **1.86** | **PASS** | Excess risk-adjusted return over cash in secular bull. |
| **Gate 2: Deflated Sharpe Ratio** | $\text{DSR Prob} \ge 0.95$ | **0.974** | **PASS** | Bailey & López de Prado (2014) significance ($K=14, p < 0.026$). |
| **Gate 3: Profit Factor** | $\text{PF} \ge 2.00$ | **AI: 5.23 / OOS: 4.67** | **PASS** | Ratio of gross profits to gross losses. |
| **Gate 4a: Modern AI Era Max DD** | $\text{Max DD} \le 35.0\%$ | **33.70%** | **PASS** | Outperforms passive `SMH` AI era drawdown ($35.74\%$). |
| **Gate 4b: Full OOS Max DD** | $\text{Max DD} \le 40.0\%$ | **37.97%** | **PASS** | $>500\text{ bps}$ below passive `SMH` crash ($45.14\%$) and `SOXX` ($45.52\%$). |
| **Gate 5: Full OOS Sharpe Ratio** | $\text{Sharpe} \ge 1.20$ | **1.36** | **PASS** | Full cycle viability across both 2022 bear and 2023–2026 bull. |
| **Gate 6: 2022 Bear Stress Test** | $\text{Ret} \ge -40\%, \text{DD} \le 40\%, \text{Cash} \ge 80\%$ | **Ret: -37.9%, DD: 38.0%, Cash: 89.6%** | **PASS** | Downside capital preservation during systemic bear. |
| **Gate 7: ML Alpha Dominance** | $\text{BSS} > 0.02 \;\land\; (\Delta\text{SR} \ge 0.05 \lor \Delta\text{DD} \ge 1.5\%)$ | **BSS: 0.0384, SR: +0.06, DD Red: +2.0%** | **PASS** | Proves probabilistic resolution & outperformance vs baseline. |

#### Cash Swing Mode (100% Cash / T-Bill Secondary Default)

| Gate | Hurdle Requirement | Actual Modern AI Era | Status | Purpose & Benchmark Comparison |
| :--- | :---: | :---: | :---: | :--- |
| **Gate 1: Modern AI Era Sharpe** | $\text{Sharpe} \ge 1.50$ | **1.73** | **PASS** | Excess risk-adjusted return over cash in secular bull. |
| **Gate 2: Deflated Sharpe Ratio** | $\text{DSR Prob} \ge 0.95$ | **0.954** | **PASS** | Statistical significance penalizing $K=14$ iterations. |
| **Gate 3: Profit Factor** | $\text{PF} \ge 1.50$ | **AI: 5.45 / OOS: 4.79** | **PASS** | Ratio of gross profits to gross losses. |
| **Gate 4a: Modern AI Era Max DD** | $\text{Max DD} \le 36.0\%$ | **35.52%** | **PASS** | Below passive `SMH` ($35.74\%$) and `SOXX` ($41.36\%$). |
| **Gate 4b: Full OOS Max DD** | $\text{Max DD} \le 40.0\%$ | **35.52%** | **PASS** | $>900\text{ bps}$ below passive `SMH` crash ($45.14\%$). |
| **Gate 5: Full OOS Sharpe Ratio** | $\text{Sharpe} \ge 1.00$ | **1.36** | **PASS** | Full cycle viability across entire 4.77-year OOS period. |
| **Gate 6: 2022 Bear Stress Test** | $\text{Ret} \ge -25\%, \text{DD} \le 25\%, \text{Cash} \ge 80\%$ | **Ret: -22.5%, DD: 22.7%, Cash: 89.6%** | **PASS** | Outperforms `SMH` crash ($-34.97\%$) by $>12$ percentage points. |
| **Gate 7: ML Alpha Dominance** | $\text{BSS} > 0.02 \;\land\; (\Delta\text{SR} \ge 0.05 \lor \Delta\text{DD} \ge 1.5\%)$ | **BSS: 0.0384, SR: +0.11, DD Red: +1.5%** | **PASS** | Proves probabilistic skill & outperformance vs baseline. |

---

## 4. CLI Execution & Reproduction

```bash
# 1. Run unit test suite (causal look-ahead invariance, purged CV, PIT universe, risk caps)
.venv/bin/pytest tests/

# 2. Run full walk-forward out-of-sample backtest (2022-2026)
.venv/bin/semiswing backtest --report reports/backtests/backtest_report.html

# 3. Generate today's multi-portfolio daily recommendation plan
.venv/bin/semiswing recommend --no-email

# 4. Run automated daily market pipeline (refresh data + backtest + recommendations)
.venv/bin/semiswing daily-run --force --no-email
```
