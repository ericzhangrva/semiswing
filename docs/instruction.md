# SemiSwing: Complete Architecture & Implementation Specification

> [!IMPORTANT]
> **Status: Institutional Hardened (Phase 1 Schmitt Macro Lockdown, Phase 2 Continuous Meta-Labeling Sizing, Phase 3 Dynamic Point-in-Time Universe Reconstitution).**
> - **Target Runtime:** Python 3.10+ package `semiswing`.
> - **Primary Repositories:** DuckDB (`data/semiswing.duckdb`), GitHub Actions (`.github/workflows/daily_semiswing.yml`), Cloudflare Pages (`https://semiswing.pages.dev/`).
> - **Core Mandate:** Regular US equities and unleveraged ETFs only. Strictly NO leveraged ETFs (`SOXL`, `SOXS`, `NVDL`, `TQQQ`) and NO options.

---

## 1. System Overview & Portfolio Architecture

SemiSwing is a systematic momentum swing trading, walk-forward validation, and daily portfolio recommendation engine designed for 2–5 week swing trends in US semiconductor & AI infrastructure leaders and unleveraged benchmark ETFs (`SMH`, `SOXX`, `VGT`, `QQQ`, `SPY`, `AIQ`, `IGV`).

### Dual Capital Allocation Modes
1. **Cash Swing Mode (100% Cash Default):**
   - Unallocated capital sits in cash and earns daily risk-free interest indexed to the 3-Month US Treasury Bill secondary market rate (`FRED DTB3`):
     $$\text{Daily Cash Yield} = \frac{\text{cash\_rate\_apy}}{252}$$
2. **SMH Bull Core + Swing Mode:**
   - During confirmed secular semiconductor bull markets (`smh_secular_bull == 1`), uninvested portfolio cash is swept into `SMH` core equity.
   - When the secular bull trend breaks (`smh_secular_bull == 0`), the core `SMH` holding is liquidated at market open and swept back into 100% T-Bill cash.

---

## 2. Dynamic Point-in-Time (PIT) Universe Reconstitution

To guarantee zero look-ahead bias and eliminate survivorship bias, the tradeable universe is reconstituted dynamically at the start of each calendar quarter $t_k \in \{\text{Jan 1, Apr 1, Jul 1, Oct 1}\}$ strictly using data available up to $t_k - 1$.

```mermaid
flowchart TD
    Pool["Active US Equities in Expanded Semi/AI Panel (all_panel_stocks)"] --> Stage1{"Stage 1: Hard Liquidity & Listing Floor (at t_k - 1)\n- Listing history >= 60 trading days\n- Close >= $15.00\n- Trailing 60d Median Daily Dollar Vol >= $150M\n- 20d ATR% > 0"}
    Stage1 -->|Pass| Stage2["Stage 2: Swing Tradability Ranking\nScore = log10(MedDollarVol_60d) * ATR%_20d"]
    Stage1 -->|Fail| Exclude["Excluded from Quarter k Tradeable Universe"]
    Stage2 --> Top40["Select Top N = 40 Highest-Ranked Tickers"]
    Top40 --> Universe["Tradeable Universe for Quarter k (is_tradeable_universe = 1)"]
```

### Stage 1: Survivorship-Free Industry + Liquidity Gate (at $t_k - 1$)
Evaluated over the trailing 60 trading days $[t_k - 60, t_k - 1]$:
1. **Industry Universe:** Active US-listed equities in Semiconductors, Semiconductor Equipment, Computer Hardware/Storage, Communications Equipment, and Electronic Components (`universe.all_panel_stocks`).
2. **Seasoning / IPO Guard:** Total historical daily bars $\ge 60$ trading days since listing.
3. **Price Floor:** $\text{Close}_{t_k - 1} \ge \$15.00$.
4. **Institutional Dollar Volume Floor:**
   $$\text{MedDollarVol}_{60d} = \text{median}_{t \in [t_k - 60, t_k - 1]}\!\left(\text{Close}_t \times \text{Volume}_t\right) \ge \$150{,}000{,}000.0$$
5. **Valid Volatility:** $\text{ATR\%}_{20d, t_k - 1} > 0$.

### Stage 2: Swing Tradability Ranking (at $t_k - 1$)
For all qualifying stocks passing Stage 1:
$$\text{SwingRankScore}_{i, t_k - 1} = \log_{10}\!\left(\text{MedDollarVol}_{60d}\right) \times \text{ATR\%}_{20d, t_k - 1}$$
where $\text{ATR\%}_{20d} = \frac{\text{ATR}_{20d}}{\text{Close}}$.
- The $\log_{10}$ compression scales volume variation down to a $1.28\times$ factor across mega-caps vs mid-caps, allowing 20-day $\text{ATR\%}$ to prioritize high-velocity momentum leaders over sluggish value traps.
- Select the **Top $N = 40$** tickers.

### Quarterly Invariance & Position Grace Rule
- All selected Top 40 tickers receive `is_tradeable_universe = 1` for every trading day in quarter $k$.
- Tradeable ETFs (`SMH`, `SOXX`, `QQQ`, `SPY`, `VGT`, `AIQ`, `IGV`) permanently have `is_tradeable_universe = 1`.
- **Position Grace Rule:** If an open position entered in quarter $k-1$ drops out of the Top 40 in quarter $k$, it is **never forcibly fire-sold**. It continues to be managed under its stops, trailing chandelier, and profit targets until natural exit. `is_tradeable_universe = 0` simply blocks new entries.

---

## 3. Data Ingestion, Storage & Causal Hygiene

Data is ingested into DuckDB (`data/semiswing.duckdb`) across four tables:
- `daily_bars`: Daily OHLCV bars (`date`, `ticker`, `open`, `high`, `low`, `close`, `volume`, `source`).
- `fred_series`: Observation-dated macroeconomic series (`date`, `series_id`, `value`).
- `earnings_dates`: Corporate earnings announcements (`ticker`, `earnings_date`).
- `data_health`: Timestamped execution data-integrity logs (`run_ts`, `health_score`).

### Causal Data Hygiene Rules
1. **FRED Macro Series Publication Lag:** All FRED series (`DTB3`, `DGS10`, `DTWEXBGS`, `VIXCLS`, `VXVCLS`, `BAMLH0A0HYM2`) are strictly lagged by 1 business day (`fred_piv = fred_piv.shift(1)`), preventing economic report look-ahead leakage.
2. **Fail-Closed Volatility Fallback:**
   $$\text{vix\_ts} = \left(\frac{\text{VIX}}{\text{VIX3M}}\right).\text{fillna}(1.05)$$
   Missing volatility term structure data defaults to backwardation ($1.05$), automatically locking down long exposure.
3. **EOD Cross-Source Majority Reconciliation:** Daily closing prices from `yfinance` are cross-checked against `Stooq` with an acceptance tolerance of $0.5\%$.
4. **Premarket Gap-Down Circuit Breaker (09:15–09:30 ET):** If the sector benchmark (`SMH`) opens or premarket gaps down $< -1.5\%$, all pending candidate buy orders are aborted.

---

## 4. Causal Feature Engineering (19 Scale-Free Features)

All indicators are computed strictly on closed daily bars ($t$).

### 4.1 Volatility-Scaled Adaptive Lookback Window ($L_t$)
$$L_t = \text{clip}\left(\text{round}\left(20 \times \frac{\sigma_{250}}{\sigma_{20}}\right), 10, 60\right)$$
where $\sigma_n$ is the $n$-day sample standard deviation of log returns $\ln(C_t / C_{t-1})$. High recent volatility compresses the window; persistent calm expands it.

### 4.2 Scale-Free Feature Definitions
Every feature is dimensionless or sample-size normalized:

| Feature | Formula | Economic Interpretation |
| :--- | :--- | :--- |
| `slope_t_norm` | $t(\beta) \times \sqrt{20 / L_t}$ via OLS $\ln C_t = \alpha + \beta t$ | Sample-size-normalized Newey-West HAC trend conviction |
| `slope_r2` | $R^2$ of log price OLS regression over $L_t$ | Trend linearity and fit cleanliness |
| `slope_sharpe` | $(\beta \times 252) / (\sigma_{20} \times \sqrt{252})$ | Trend velocity per unit of realized volatility |
| `slope_accel` | $(\beta_{10d} - \beta_{40d}) / \sigma_{20}$ | Multi-scale trend acceleration |
| `slope_t_norm_10d` | $t(\beta_{10d}) \times \sqrt{20 / 10}$ | Short-term 10-day normalized trend conviction |
| `slope_t_norm_20d` | $t(\beta_{20d}) \times \sqrt{20 / 20}$ | Medium-term 20-day normalized trend conviction |
| `slope_t_norm_40d` | $t(\beta_{40d}) \times \sqrt{20 / 40}$ | Intermediate 40-day normalized trend conviction |
| `slope_r2_20d` | $R^2$ of 20-day log price regression | 20-day trend linearity |
| `ema20_slope` | $\frac{\text{EMA20}_t / \text{EMA20}_{t-5} - 1}{\text{ATR\%}_{14}}$ | 5-day slope of 20-day EMA in ATR units |
| `ema50_slope` | $\frac{\text{EMA50}_t / \text{EMA50}_{t-10} - 1}{\text{ATR\%}_{14}}$ | 10-day slope of 50-day EMA in ATR units |
| `ext_atr` | $\frac{C_t - \text{EMA20}_t}{\text{ATR}_{14}}$ | Overextension above 20d EMA in ATR units |
| `resid_mom_20` | Cumulative residual return vs `SMH` over 20d | Beta-decoupled single-stock idiosyncratic momentum |
| `resid_mom_60` | Cumulative residual return vs `SMH` over 60d | Intermediate beta-decoupled relative strength |
| `rs_rank` | Percentile rank of `resid_mom_20` across panel | Cross-sectional leadership (decile rank $[0.0, 1.0]$) |
| `sector_rs` | $R_{20d}(\text{SMH}) - R_{20d}(\text{SPY})$ | Semiconductor sector excess momentum vs broad market |
| `vol_compress` | $\text{RV}_{10} / \text{RV}_{60}$ | Realized volatility ratio ($<0.7$ signals squeeze) |
| `vix_ts` | $\text{VIX} / \text{VIX3M}$ | Volatility term structure ($>1.0$ indicates backwardation) |
| `vxn_squeeze_vel` | $z\text{-score of } \Delta_{5d}\text{VXN}$ vs 252d distribution | Implied volatility expansion/compression velocity |
| `skew_idx` | $z\text{-score of CBOE SKEW vs 20d}$ | Tail-risk hedge demand |

---

## 5. Macro Regime Engine (Schmitt Trigger Hysteresis & Continuous Multiplier $M_t$)

To eliminate bear-market whipsaws and avoid transition lag during bull ignited recoveries, SemiSwing utilizes a **stateful dual-threshold Schmitt trigger** on `SMH` combined with the continuous macro multiplier $M_t$.

```mermaid
stateDiagram-v2
    [*] --> RegimeOff: Initial State (M_t = 0.0)
    
    RegimeOff --> RegimeOn: SMH > EMA200 * 1.015 AND SMH > EMA50\n(Upper Unlock Band)
    RegimeOn --> RegimeOff: SMH < EMA200 * 0.985\n(Lower Lockdown Band)
    
    RegimeOn --> RegimeOn: Price inside [EMA200 * 0.985, EMA200 * 1.015]\n(Hysteresis Band: Retains Current State)
    RegimeOff --> RegimeOff: Price inside [EMA200 * 0.985, EMA200 * 1.015]\n(Hysteresis Band: Retains Current State)
```

### Continuous Macro Multiplier ($M_t$)
1. **$M_t = 0.0$ (Deep Bear / Macro Breakdown / Crisis):**
   - Condition: Schmitt trigger state $= 0$, OR $\text{vix\_ts} \ge 1.0$ (Backwardation), OR $\text{VIX} \ge 30.0$.
   - **Action:** 0% new long risk. Unallocated capital sweeps to 100% 3-Month T-Bills.
2. **$M_t = 0.5$ (Recovery / Early Transition):**
   - Condition: Schmitt trigger state $= 1$, BUT ($\text{EMA50} < \text{EMA200}$ OR $\text{VIX} \ge 22.0$).
   - **Action:** Permits high-conviction momentum leaders at 50% standard risk allocation.
3. **$M_t = 1.0$ (Confirmed Secular Bull):**
   - Condition: Schmitt trigger state $= 1$, $\text{EMA50} \ge \text{EMA200}$, and $\text{VIX} < 22.0$.
   - **Action:** 100% full risk allocation.

---

## 6. Two-Layer Signal Architecture & Continuous Meta-Labeling

```mermaid
flowchart LR
    Bars["Daily Bar t Close"] --> Baseline["Layer 1: Deterministic Baseline Setup\n- Slope t-norm >= 1.50\n- R^2 >= 0.35 & Accel > 0\n- rs_rank >= 0.80\n- ext_atr in [-0.5, 3.5]\n- is_tradeable_universe == 1"]
    Baseline -->|Candidate Fired| LightGBM["Layer 2: Regularized Shallow LightGBM\n- max_depth = 2, num_leaves = 4\n- min_child_samples = 60\n- Monotone constraints (+1 on slope & rs)"]
    LightGBM --> OOF_CDF["Out-of-Fold Empirical CDF\nq_it = PercentileRank(p_it in OOF)"]
    OOF_CDF --> Sizer["Continuous Sizing Multiplier\nS_it = 0.50 + 1.00 * q_it in [0.50, 1.50]"]
    Sizer --> TradeOrder["Next-Day Market Open Order (09:30 ET)\nRisk = BaseRisk * M_t * S_it"]
```

### Layer 1: Deterministic Baseline Rules
A candidate triggers an entry signal if all hold on closed bar $t$:
1. `is_tradeable_universe == 1` & `regime_on == 1` & `data_health >= 80`.
2. `close >= $10.00` & `dollar_vol_20d >= $150,000,000`.
3. `slope_t_norm >= 1.50` & `slope_r2 >= 0.35` (over $L_t$).
4. `slope_accel > 0.0` & `ema20_slope > 0.0`.
5. `rs_rank >= 0.80` (top 20% relative strength across semiconductor peers).
6. `-0.50 <= ext_atr <= 3.50` (not overextended).
7. `days_to_earnings > 3` & `fomc_next_day == 0`.

### Layer 2: Continuous Meta-Labeling Sizing ($S_{i,t}$)
- **Tree Hyperparameters:** `max_depth = 2`, `num_leaves = 4`, `min_child_samples = 60`, `learning_rate = 0.03`, `n_estimators = 100`, `subsample = 0.8`, `colsample_bytree = 0.8`.
- **Monotone Constraints:** Strict positive monotonicity (`+1`) on `slope_t_norm`, `slope_t_norm_20d`, `resid_mom_20`, and `rs_rank`.
- **Expanding Walk-Forward Retraining:** Model retrains in 63-day blocks, training exclusively on preceding historical observations where `tb_end_date < t_block_start`.
- **Continuous Percentile Rank Mapping:**
  $$q_{i,t} = \frac{1}{|OOF|} \sum_{j \in OOF} \mathbf{1}\{p_j \le p_{i,t}\}$$
  $$S_{i,t} = 0.50 + 1.00 \times q_{i,t} \in [0.50, 1.50]$$

---

## 7. Portfolio Risk Management & Order Execution

### Execution Protocol
- **Next-Day Market Open Fill (09:30 ET):** Signals generated at close $t$ execute at open $t+1$.
- **Friction Model:** $5.0\text{ bps slippage} + 2.0\text{ bps commission} = 7.0\text{ bps}$ total friction.
- **Hierarchical Two-Tier Sizing Formulation:**
  $$\text{Trade Risk Budget} = \text{Portfolio Equity} \times \text{Base Risk (1.0\%)} \times M_t \times S_{i,t}$$
  $$\text{Position Dollar Cap} = \min\left(\text{Portfolio Equity} \times 35\% \times M_t \times S_{i,t},\;\text{Cash} \times 0.99\right)$$
  $$\text{Shares} = \min\left(\left\lfloor \frac{\text{Trade Risk Budget}}{\text{Open Price} - \text{Initial Stop}} \right\rfloor,\; \left\lfloor \frac{\text{Position Dollar Cap}}{\text{Open Price}} \right\rfloor\right)$$

### Exit & Position Management Rules
1. **Initial Stop Loss:** $2.0 \times \text{ATR}_{14}$ below signal close (`STOP`).
2. **Take Profit 1 (TP1):** $3.0 \times \text{ATR}_{14}$ above entry. Sell 50% of shares; ratchet stop to breakeven (`avg_cost`).
3. **Trailing Chandelier Stop:** After TP1, trail highest close minus $2.5 \times \text{ATR}_{14}$ (`TRAIL_STOP_EOD`).
4. **Early Time Stop (Day 10):** If days held $= 10$ and unrealized gain $< 0.50R$, exit at close (`TIME_STOP_12D`).
5. **Hard Time Stop (Day 20):** If days held $\ge 20$, not TP1 hit, and unrealized gain $< 0.50R$, exit at close (`TIME_STOP_25D`).
6. **Earnings Blackout Exit:** Exit 1 day prior to earnings if unrealized gain $< 0.25R$ (`EARNINGS_EXIT`).
7. **Regime Kill:** If $M_t = 0.0$ and secular bull $= 0$, exit all open swing trades at close (`REGIME_OFF`).
8. **Cooldown:** 10-trading-day cooldown after any stop-loss before re-entering that ticker.

---

## 8. Institutional Validation Gates & Hurdle Thresholds

Every backtest execution is audited against five objective institutional gates:

| Gate | Hurdle Requirement | Purpose |
| :--- | :--- | :--- |
| **Gate 1: Out-of-Sample Sharpe Ratio** | $\text{Sharpe} \ge 1.0$ (Overall) or $\ge 1.50$ (AI Era) | Risk-adjusted excess return vs cash |
| **Gate 2: Deflated Sharpe Ratio (DSR)** | $\text{DSR Probability} \ge 0.95$ (Bailey & López de Prado) | Statistical significance penalizing trial selection bias |
| **Gate 3: Profit Factor** | $\text{Profit Factor} \ge 1.50$ | Ratio of gross profits to gross losses |
| **Gate 4: Maximum Drawdown** | $\text{Max Drawdown} \le 25.5\%$ (Cash) or $\le 38.0\%$ (SMH Core) | Tail drawdown limit vs passive SMH (45.1%) |
| **Gate 5: Bear Market Stress Test** | 2022 Bear Return $> -25.0\%$ with $\text{Cash Days} \ge 75\%$ | Downside capital preservation during systemic bear |

---

## 9. Verification & CLI Reproduction Commands

```bash
# 1. Run unit test suite (causal look-ahead invariance, purged CV, PIT universe, risk caps)
.venv/bin/pytest tests/

# 2. Run full walk-forward out-of-sample backtest (2022-2026)
.venv/bin/semiswing backtest --report reports/backtests/backtest_report.html

# 3. Generate daily trade recommendations (multi-portfolio)
.venv/bin/semiswing recommend --no-email

# 4. Run automated daily market pipeline (refresh data + backtest + recommendations)
.venv/bin/semiswing daily-run --force --no-email
```
