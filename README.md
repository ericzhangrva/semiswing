# SemiSwing

SemiSwing is a systematic momentum swing trading, walk-forward backtesting, and daily portfolio recommendation system focused on US Semiconductor & AI infrastructure leaders and unleveraged sector/index benchmark ETFs (`SMH`, `SOXX`, `VGT`, `QQQ`, `SPY`, `AIQ`, `IGV`). 

Unallocated portfolio cash earns daily risk-free interest indexed to the 3-Month US Treasury Bill rate (`FRED DTB3`), with an **SMH Bull Core + Swing** sleeve that holds `SMH` during confirmed secular semiconductor bull markets.

- **Live Cloud Dashboard:** [https://semiswing.pages.dev/](https://semiswing.pages.dev/)
- **1. Walk-Forward Backtest Report & Performance Tearsheet ($10K):** [https://semiswing.pages.dev/backtests/backtest_report.html](https://semiswing.pages.dev/backtests/backtest_report.html)
- **2. Active Open Positions (Daily MTM) & Recent 25 Closed Trades:** [https://semiswing.pages.dev/backtests/recent_trades_and_open_positions.html](https://semiswing.pages.dev/backtests/recent_trades_and_open_positions.html)
- **3. $10,000 Starter Portfolio & Daily Allocation Guide:** [https://semiswing.pages.dev/daily/starter_10k.html](https://semiswing.pages.dev/daily/starter_10k.html)
- **4. Personal Daily Trade Tickets (Passcode-Protected):** [https://semiswing.pages.dev/daily/family_recommendations.html](https://semiswing.pages.dev/daily/family_recommendations.html)
- **5. Customer IZ Daily Trade Tickets (Passcode-Protected):** [https://semiswing.pages.dev/daily/isabel_recommendations.html](https://semiswing.pages.dev/daily/isabel_recommendations.html)
- **Static Markdown Backtest Report:** [`reports/backtests/backtest_report.md`](reports/backtests/backtest_report.md)

---

## 1. System Architecture & Core Trading Desk Principles

The platform is engineered around six institutional quantitative trading and software principles:

### 1.1 Clean Universe & Zero Leverage Decay (Clean Universe)
- **High-Quality Asset Universe:** Focuses exclusively on ~50 liquid US-listed AI compute, advanced semiconductor fabrication, memory, networking, and datacenter infrastructure leaders (e.g., `NVDA`, `AVGO`, `TSM`, `ASML`, `MU`, `P`, `VST`), alongside unleveraged sector and broad-market benchmark ETFs (`SMH`, `QQQ`, `SPY`).
- **Zero Options, Zero 3x Leveraged ETFs:** Eliminates complex derivatives and structural volatility drag. The system strictly avoids leveraged ETFs like `SOXL`/`SOXS`/`NVDL` that suffer severe compounding loss and volatility decay during choppy regimes. Returns are generated purely through underlying equity momentum and systematic position sizing.

### 1.2 Dual-Regime Gating, Premarket Circuit Breaker & Dual Cash Allocation (Regime-Gated Risk Control)
- **Macro Regime Filter:** Monitors semiconductor secular trend health (using `SMH` relative to EMA100/EMA200 and 200-day moving average slope) and market-wide volatility term structure (`VIX`/`VIX3M`, `VXN`).
- **Premarket Circuit Breaker (09:15–09:30 ET):** If `SMH` opens or trades down $< -1.5\%$ in premarket hours, all pending candidate buy orders are automatically cancelled to protect capital from opening cascades and liquidity shocks.
- **Regime ON vs. Regime OFF Dynamics:**
  - **Regime ON (Secular Bull):** Actively allocates capital to high-conviction breakout and pullback setups.
  - **Regime OFF (Defensive Lockdown):** Automatically tightens trailing stops, freezes all new buying, and preserves principal during prolonged drawdowns (e.g., 2022 bear market).
- **Dual Strategy Paths for Unallocated Cash:**
  - **Pathway 1 (Secular Growth Core / SMH):** Sweeps idle cash into `SMH` during confirmed secular bull regimes, aligning uncommitted funds with structural semiconductor growth.
  - **Pathway 2 (Zero-Risk Treasury Cash / T-Bills):** Parks unallocated cash in ultra-short US Treasury Bills (`SGOV`, `BIL`, or 3M T-Bills via FRED `DTB3`), yielding ~4.1%–4.6% annualized with 0% drawdown.

### 1.3 Institutional-Grade Causal Backtesting & Next-Day Open Execution
- **Realistic Next-Day Market Open Fills (09:30 ET):** Completely eliminates the classic "close-fill illusion" (generating signals at 16:00 and unrealistically assuming fill at the same close). Daily orders are computed by 09:00 ET and filled strictly at the **09:30 ET Market Open** of day $t+1$ with realistic friction ($5.0\text{ bps slippage} + 2.0\text{ bps commission} = 7.0\text{ bps}$ round-turn).
- **Anti-Chase Gap Filter (Max Chase Price):** If a candidate stock gaps up $> 1.0\times\text{ATR}$ or $> +4.0\%$ overnight, the buy order is discarded, preventing emotional FOMO entries.
- **Expanding Walk-Forward Validation:** Utilizes Marcos López de Prado's Triple-Barrier labeling with quarterly (63-day) rolling retraining and strict purged & embargoed cross-validation splits to guarantee zero look-ahead bias.

### 1.4 Machine Learning Alpha & White-Box Attribution (LightGBM + Platt Scaling + Continuous Sizing + SHAP)
- **19 Scale-Free Causal Features:** Inputs capture trend linearity ($R^2$), residual momentum (`resid_mom_60`), sector relative strength (`sector_rs`), ATR extension, volume compression (`vol_compress`), and VXN squeeze velocity (`vxn_squeeze_vel`).
- **Calibrated Probabilities & Continuous Sizing ($S_{i,t}$):** Raw tree predictions are probability-calibrated using Platt Sigmoid scaling. Rather than binary all-or-nothing trade vetoes, a continuous meta-labeling position sizing multiplier ($S_{i,t} \in [0.50, 1.50]$) scales risk dynamically with model conviction.
- **Explainable Model Attribution (SHAP):** Every recommended trade ticket includes feature attribution summaries, explicitly detailing the positive and negative drivers behind each signal.

### 1.5 Automated Morning Workflow & Five-Scorecard Cloud Trading Desk
- **Zero-Overhead Cloud Automation:** Runs every trading day at 09:00 AM ET via GitHub Actions, publishing refreshed reports before 09:02 AM ET with precise generation timestamp footers (`Report Created: YYYY-MM-DD HH:MM:SS EDT`).
- **Five-Scorecard Cloudflare Pages Delivery:**
  - **[Card 1 (Public): Walk-Forward Backtest Tearsheet & Equity Curves ($10K)](https://semiswing.pages.dev/backtests/backtest_report.html):** Comprehensive institutional backtest report displaying audited equity curves, Sharpe/Sortino ratios, drawdowns, and complete out-of-sample trade logs against benchmarks (`SMH`, `QQQ`, `SPY`, `T-Bills`).
  - **[Card 2 (Public): Active Open Positions (Daily MTM) & Recent 25 Closed Trades](https://semiswing.pages.dev/backtests/recent_trades_and_open_positions.html):** Real-time Mark-to-Market paper P&L for all active swing positions alongside recent closed trade logs and SHAP drivers.
  - **[Card 3 (Public): $10,000 Starter Portfolio & Allocation Guide](https://semiswing.pages.dev/daily/starter_10k.html):** Designed for independent cash accounts starting at $10,000. Provides exact dollar-budgeted buy tickets, defensive stops, and dual parking options (SMH Bull Core vs. T-Bills) for unallocated cash.
  - **[Card 4 (Protected): Personal Daily Trade Tickets](https://semiswing.pages.dev/daily/family_recommendations.html):** Delivers a two-step execution guide (Step 1: existing holding stop ratchets + Step 2: exact $ new buy tickets) for personal and retirement investment accounts.
  - **[Card 5 (Protected): Customer IZ Daily Trade Tickets](https://semiswing.pages.dev/daily/isabel_recommendations.html):** Dedicated execution tickets and trade allocations for customer IZ accounts.

### 1.6 Client-Side Zero-Knowledge Encryption & Multi-Portfolio Privacy
- **Multi-Portfolio Isolation:** Supports centralized management of multiple distinct accounts with varying cash balances, tax requirements, and risk preferences.
- **Client-Side Cryptographic Hardening:**
  - Private portfolio holdings, balances, and account names are encrypted into `encrypted_portfolios.json` using **PBKDF2-HMAC-SHA256 (150,000 hash iterations) + SHA256 Counter-Mode (CTR) stream cipher + HMAC-SHA256 (Encrypt-then-MAC authentication)**.
  - The secret encryption key resides exclusively within repository CI secrets (`PORTFOLIO_PASSCODE`).
  - Decryption occurs strictly in-memory within the client's browser (`window.crypto.subtle`) upon passcode entry. Neither GitHub nor Cloudflare servers ever store or see plaintext financial data.

---

## 2. Institutional Causal Hygiene & Validation Controls

Quantitative backtests frequently suffer from subtle biases (look-ahead peeking, survivorship bias, unrealistic execution timing, and post-hoc parameter overfitting). SemiSwing enforces strict causal hygiene controls to ensure every reported return reflects institutional execution reality:

### 2.1 Realistic Next-Day Execution (Zero Close-Fill Illusion)
- **Next-Day Market Open Fills (09:30 ET):** Signals generated at the close of trading day $t$ (16:00 ET) are executed strictly at the **Market Open of day $t+1$ (09:30 ET)** using that day's real open price.
- **Transaction Costs & Slippage:** A realistic friction of **$5.0\text{ bps slippage} + 2.0\text{ bps commission} = 7.0\text{ bps}$** round-turn is subtracted from every execution.
- **Gap-Up Protection:** New entries are blocked if the stock opens $> 1.0\times\text{ATR}$ above signal close or gaps up $> +4.0\%$ overnight, preventing chasing opening spikes. In live execution, each daily recommendation ticket specifies the exact **Max Chasing Limit Price** ($\min(\text{Close} + 1.0\times\text{ATR}_{14}, \text{Close} \times 1.04)$). Place orders as Limit-on-Open (LOO) or limit orders capped at this price; if the market opens above this level, the order is unexecuted.
- **Premarket Gap-Down Abort (09:15–09:30 ET):** If the semiconductor benchmark (`SMH`) opens or gaps down $< -1.5\%$, all pending candidate buy orders are cancelled. The daily recommendation report displays the exact **SMH Premarket Circuit Breaker Level** ($\text{Prior Close} \times 0.985$). Between 09:15 and 09:30 ET, check SMH premarket quotes; if trading below this threshold, cancel all pending buy orders prior to 09:30 ET.

### 2.2 Two-Stage Dynamic Point-in-Time (PIT) Universe Reconstitution
To eliminate look-ahead selection bias and survivorship bias, the tradeable universe is reconstituted dynamically at the start of each calendar quarter $t_k \in \{\text{Jan 1, Apr 1, Jul 1, Oct 1}\}$ strictly using trailing market data ending at $t_k - 1$:
1. **Stage 1 (Institutional Liquidity Floor at $t_k - 1$):**
   - Active US-listed semiconductor & tech equities in `universe.all_panel_stocks`.
   - Listing history $\ge 60$ trading days since listing/IPO (eliminates unseasoned listings).
   - $\text{Close}_{t_k - 1} \ge 15.00\text{ USD}$ (eliminates penny stocks below 15 USD).
   - Trailing 60-day median daily dollar volume:

$$
\text{MedDollarVol}_{60\text{d}} = \text{median}_{t \in [t_k - 60, t_k - 1]} \left(\text{Close}_t \times \text{Volume}_t\right) \ge 150{,}000{,}000\text{ USD}
$$

   - Volatility condition: 20-day $\text{ATR}_{\text{pct}, 20\text{d}, t_k - 1} > 0$.
2. **Stage 2 (Swing Tradability Ranking at $t_k - 1$):**

$$
\text{SwingRankScore}_{i, t_k - 1} = \log_{10}\left(\text{MedDollarVol}_{60\text{d}}\right) \times \text{ATR}_{\text{pct}, 20\text{d}, t_k - 1}
$$

   - The $\log_{10}$ compression scales volume variation down to a $1.28\times$ factor between mid-caps and mega-caps, allowing 20-day $\text{ATR\%}$ to prioritize high-velocity momentum leaders over sluggish value traps.
   - **Uncapped Selection (`pit_top_n = None`):** All qualifying tickers passing the Stage 1 liquidity floor receive `is_tradeable_universe = 1` for quarter $k$, naturally expanding from ~28 stocks in 2022 to ~50 in 2026 as the AI infrastructure ecosystem expanded (with Stage 2 tradability scores governing relative ranking and execution priority).
3. **Position Grace Rule:** Open positions held across quarterly boundaries are **never forcibly liquidated**; they remain managed under their stops and profit targets until natural exit, while new entries for dropped tickers are blocked.

### 2.3 Causal Macro Data & Volatility Hygiene
- **FRED Publication Lag:** All Federal Reserve economic series (`DTB3`, `DGS10`, `DTWEXBGS`, `VIXCLS`, `VXVCLS`, `BAMLH0A0HYM2`) are lagged by 1 business day (`shift(1)`) to account for publication schedules.
- **Fail-Closed Volatility Fallback:**

$$
\text{vix}_{\text{ts}} = \left(\frac{\text{VIX}}{\text{VIX3M}}\right).\text{fillna}(1.05)
$$

  Missing volatility term structure data defaults to backwardation ($1.05$), immediately locking down long exposure.

### 2.4 Purged & Embargoed Machine Learning Validation
- **Expanding Walk-Forward Blocks:** The ML model retrains in 63-trading-day (~quarterly) blocks from 2022 to 2026.
- **López de Prado Purged K-Fold CV:** Inside each training block, cross-validation splits by unique dates ($K=5$) with a **20-day embargo** following each test fold, purging any observation whose triple-barrier span overlaps validation boundaries.
- **Causal Label Cutoff:** For any test block $[t_{\text{start}}, t_{\text{end}}]$, the training set is strictly restricted to observations where trade exit date satisfies $t_{\text{exit}} < t_{\text{start}}$ (`tb_end_date < t_start`), guaranteeing that every training trade outcome was completely settled prior to the test window.

### 2.5 The Control Benchmark (Pure Pre-2022 Semi)
To prove that outperformance is driven by signal extraction and macro regime gating rather than post-2022 IPO additions (`ARM`, `ALAB`, `GEV`, `NBIS`, `SNDK`), the backtest runs an ablation restricted strictly to **25 established pre-2022 `SMH`/`SOXX` constituents** (`NVDA, AVGO, AMD, TSM, ASML, MU, KLAC, LRCX, AMAT, MRVL, QCOM, TXN, ON, MCHP, INTC, SNPS, CDNS, MPWR, ADI, NXPI, TER, WDC, STX, ANET, COHR`).

---

## 3. Mathematical Formulations

### 3.1 Sample-Size Normalized OLS Trend Conviction (`slope_t_norm`)
Over a lookback window $L$, we fit the log-price regression $\ln C_i = \alpha + \beta t_i$ using Newey-West lag-1 HAC standard errors to account for residual autocorrelation. Because raw $t$-statistics scale with $\sqrt{L}$, we normalize to a constant 20-day baseline:

$$
t_{\text{norm}} = t(\beta) \times \sqrt{\frac{20}{L}}
$$

$$
R^2 = 1.0 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}
$$

### 3.2 Volatility-Scaled Adaptive Window ($L_t$)

$$
L_t = \text{clip}\left(\text{round}\left(20 \times \frac{\sigma_{250}}{\sigma_{20}}\right), 10, 60\right)
$$

where $\sigma_n$ is the $n$-day sample standard deviation of daily log returns $\ln(C_t / C_{t-1})$.

### 3.3 Macro Regime Schmitt Trigger & Continuous Multiplier ($M_t$)
To prevent whipsaw churn near moving averages while avoiding recovery lag, regime transitions are governed by a dual-threshold hysteresis band on `SMH`:
- **Upper Unlock Band:** $SMH > \text{EMA200} \times 1.015$ **AND** $SMH > \text{EMA50} \implies \text{Regime} = 1$.
- **Lower Lockdown Band:** $SMH < \text{EMA200} \times 0.985 \implies \text{Regime} = 0$.
- **Inside Band:** Retains previous regime state.

The continuous macro multiplier $M_t$ scales capital allocation:

$$
M_t = \begin{cases} 
0.0 & \text{if } \text{Regime} = 0 \lor \text{vix}_{\text{ts}} \ge 1.0 \lor \text{VIX} \ge 30.0 \quad \text{(Deep Bear / Crisis)} \\
0.5 & \text{if } \text{Regime} = 1 \land (\text{EMA50} < \text{EMA200} \lor \text{VIX} \ge 22.0) \quad \text{(Recovery / Transition)} \\
1.0 & \text{if } \text{Regime} = 1 \land \text{EMA50} \ge \text{EMA200} \land \text{VIX} < 22.0 \quad \text{(Confirmed Bull)}
\end{cases}
$$

### 3.4 Continuous Meta-Labeling Sizing ($S_{i,t}$)
Following Marcos López de Prado's Meta-Labeling framework, shallow decision trees (`max_depth = 2`, `num_leaves = 4`, `min_child_samples = 60`) predict trade success probability $p_{i,t}$. Probabilities are mapped into out-of-fold empirical percentile ranks $q_{i,t} \in [0.0, 1.0]$:

$$
q_{i,t} = \frac{1}{|OOF|} \sum_{j \in OOF} \mathbf{1}\{p_j \le p_{i,t}\}
$$

$$
S_{i,t} = 0.50 + 1.00 \times q_{i,t} \in [0.50, 1.50]
$$

### 3.5 Hierarchical Conviction Tier Risk Allocation
Signals receive an initial conviction tier determining their baseline risk fraction (`BaseRisk`: $1.0\%$ for `CONSENSUS`/`HIGH`, $0.75\%$ for `MEDIUM`, $0.50\%$ for `LOW`):

$$
\text{RiskBudget} = \text{Equity} \times \text{BaseRisk} \times M_t \times S_{i,t}
$$

$$
\text{PositionCap} = \min\left(\text{Equity} \times 0.35 \times M_t \times S_{i,t},\; \text{Cash} \times 0.99\right)
$$

$$
\text{Shares} = \min\left(\left\lfloor \frac{\text{RiskBudget}}{\text{OpenPrice} - \text{InitialStop}} \right\rfloor,\; \left\lfloor \frac{\text{PositionCap}}{\text{OpenPrice}} \right\rfloor\right)
$$

### 3.6 Deflated Sharpe Ratio (DSR)
Following David Bailey and Marcos López de Prado (2014), the Deflated Sharpe Ratio evaluates the statistical probability that the annualized Sharpe ratio $\widehat{\text{SR}}$ exceeds the expected maximum Sharpe ratio under the null hypothesis of zero skill given $K$ strategy trials:

$$
\text{DSR} = \Phi\left( \frac{(\widehat{\text{SR}} - \text{SR}^*) \sqrt{T - 1}}{\sqrt{1 - \hat{\gamma}_3 \widehat{\text{SR}} + \frac{\hat{\gamma}_4 - 1}{4} \widehat{\text{SR}}^2}} \right)
$$

where the expected maximum Sharpe ratio under the null across $K$ trials scales with sample size $T$ via the two-point Euler-Mascheroni extreme-value quantile:

$$
\text{SR}^* = \sqrt{\frac{1}{T}} \left( (1 - \gamma) Z\left(1 - \frac{1}{K}\right) + \gamma Z\left(1 - \frac{1}{K \cdot e}\right) \right) \times \sqrt{252}
$$

where $\gamma \approx 0.5772$ is the Euler-Mascheroni constant, $Z(p) = \Phi^{-1}(p)$ is the standard normal quantile function, $\hat{\gamma}_3$ is excess return skewness, and $\hat{\gamma}_4$ is return kurtosis.

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

---

## 5. License & Usage Rights

This software is licensed under the **SemiSwing Source-Available Non-Commercial Research License** ([`LICENSE`](LICENSE)). 

- **Permitted Use:** Academic research, personal education, statistical inquiry, backtesting, and private non-commercial source code modification.
- **Strict Commercial Prohibitions:** Live trading in commercial or institutional accounts, third-party capital management for fees/profit, commercial signal or trade alert services, sublicensing, or commercial redistribution.
- **Legal Remedies:** Unauthorized commercial or for-profit exploitation constitutes willful copyright infringement and intentional trade secret misappropriation, subject to statutory damages up to $150,000 per violation, immediate injunctive relief, disgorgement of profits, and prosecution to the fullest extent permitted by law.
