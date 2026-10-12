# Volatility Forecasting & Risk-Managed Equity Strategies on NIFTY

An empirical study of **volatility forecasting, Value-at-Risk calibration, and risk-managed equity allocation** on the NIFTY 50.

> **Central question:** Does a more accurate volatility forecast necessarily lead to a better investment strategy?

This project compares Rolling, EWMA, and GARCH(1,1) volatility forecasts out-of-sample, evaluates their risk forecasts, and uses them to construct long-only volatility-managed equity strategies with transaction costs and realistic execution delays.

---

## Project Overview

The analysis uses daily NIFTY 50 data from approximately **September 2007 to October 2026**.

The project has four components:

1. **Volatility modelling**
   - 20-day Rolling variance
   - EWMA with λ = 0.94
   - GARCH(1,1)

2. **Out-of-sample forecast evaluation**
   - QLIKE
   - Mean Squared Error
   - Mean Absolute Error
   - Calendar-year model comparisons

3. **Risk modelling**
   - 95% and 99% one-day Normal VaR
   - Exception-rate analysis
   - Kupiec unconditional coverage test

4. **Portfolio construction**
   - Buy & Hold
   - Moving-average trend strategy
   - Volatility-managed strategy
   - Trend + volatility strategy
   - Exposure-matched constant-allocation benchmark

Transaction costs, execution lags, portfolio-weight drift, bootstrap uncertainty, and robustness checks are explicitly incorporated.

---

## Research Questions

1. Which simple volatility model provides the strongest out-of-sample forecast of next-day NIFTY variance?
2. Are Normal VaR forecasts appropriately calibrated?
3. Does volatility targeting improve portfolio risk-adjusted performance?
4. Are the conclusions robust to reasonable choices of costs, execution lags, volatility targets, trend windows, and bootstrap assumptions?

---

# 1. Volatility Forecasting

Let **r<sub>t</sub>** denote the daily NIFTY log return observed on day *t*.

Three one-day-ahead variance forecasts are compared.

### Rolling 20-Day Variance

<div align="center">

**σ̂²<sub>t+1|t</sub> = (1 / 20) × Σ<sup>19</sup><sub>i=0</sub> r²<sub>t−i</sub>**

</div>

Every observation receives equal weight until it leaves the 20-day window.

### EWMA

<div align="center">

**σ̂²<sub>t+1|t</sub> = 0.94 σ̂²<sub>t|t−1</sub> + 0.06 r²<sub>t</sub>**

</div>

Recent shocks receive more weight and their influence decays exponentially.

The fixed decay parameter is **λ = 0.94**.

### GARCH(1,1)

<div align="center">

**σ̂²<sub>t+1|t</sub> = ω + αr²<sub>t</sub> + βσ̂²<sub>t|t−1</sub>**

</div>

GARCH parameters are estimated using an expanding window and refitted monthly. Conditional variance continues to update daily between parameter refits.

Average estimated persistence was approximately:

<div align="center">

**α + β ≈ 0.994**

</div>

indicating highly persistent volatility dynamics.

![One-day volatility forecasts](results/figures/01_volatility_forecasts.png)

---

# 2. Out-of-Sample Forecast Evaluation

All three models are evaluated on a common out-of-sample period beginning in 2015.

The primary forecasting loss is **QLIKE**, with MSE and MAE used as secondary metrics.

For realized variance proxy **RV<sub>t</sub> = r²<sub>t</sub>** and forecast variance **h<sub>t</sub>**:

<div align="center">

**QLIKE<sub>t</sub> = log(h<sub>t</sub>) + RV<sub>t</sub> / h<sub>t</sub>**

</div>

Lower forecast loss is better.

## Forecast Results

| Model | MAE × 1e4 | MSE × 1e8 | QLIKE |
|---|---:|---:|---:|
| **GARCH(1,1)** | 1.1701 | **20.5962** | **-8.4767** |
| **EWMA(0.94)** | **1.1473** | 20.9658 | -8.4586 |
| **Rolling 20** | 1.1667 | 21.8084 | -8.4391 |

GARCH produced the lowest **QLIKE** and **MSE**, while EWMA produced the lowest **MAE**.

Across the 11 complete calendar years from 2015–2025:

- **GARCH:** 8 yearly QLIKE wins
- **EWMA:** 3 wins
- **Rolling:** 0 wins

GARCH therefore produced the strongest overall variance forecasts, although its advantage over EWMA was modest.

![Yearly QLIKE](results/figures/02_yearly_qlike.png)

---

# 3. Value-at-Risk

The volatility forecasts are converted into one-day Normal VaR estimates.

### 95% VaR

<div align="center">

**VaR<sub>95,t</sub> = 1.645 × σ̂<sub>t+1|t</sub>**

</div>

### 99% VaR

<div align="center">

**VaR<sub>99,t</sub> = 2.326 × σ̂<sub>t+1|t</sub>**

</div>

A VaR violation occurs when:

<div align="center">

**r<sub>t+1</sub> < −VaR<sub>t</sub>**

</div>

Coverage is evaluated using:

- expected versus observed exception rates,
- the **Kupiec unconditional coverage test**,
- calendar-year exception counts.

Volatility-forecast accuracy and tail-risk calibration are treated separately because good conditional-variance forecasts do not automatically imply accurate modelling of extreme losses.

![GARCH VaR during COVID](results/figures/03_garch_var_covid.png)

Detailed VaR outputs are available in [`results/tables/`](results/tables/).

---

# 4. Portfolio Construction

Each portfolio allocates capital between NIFTY equity and cash.

For equity weight **w<sub>t</sub>**, the daily portfolio return is:

<div align="center">

**R<sub>p,t</sub> = w<sub>t</sub>R<sub>equity,t</sub> + (1 − w<sub>t</sub>)R<sub>f,t</sub> − c × |w<sub>t</sub> − w<sub>t−1</sub>|**

</div>

where:

- **R<sub>equity,t</sub>** = NIFTY daily simple return
- **R<sub>f,t</sub>** = daily cash/risk-free return
- **c** = one-way transaction-cost rate

Primary implementation:

- Long-only
- Maximum equity exposure: 100%
- Volatility target: 12%
- Weekly rebalance for volatility-managed strategies
- Transaction cost: 5 bps one-way
- Execution lag: 1 trading day
- Natural portfolio-weight drift between rebalances

---

# 5. Trading Strategies

### Buy & Hold

<div align="center">

**w<sub>t</sub> = 1**

</div>

The portfolio remains fully invested in NIFTY.

### MA200 Trend

<div align="center">

**w<sub>t</sub> = 1 if Price<sub>t</sub> > MA200<sub>t</sub>, otherwise 0**

</div>

### EWMA Volatility Managed

<div align="center">

**w<sub>t</sub> = min(1, 0.12 / σ̂<sub>t+1|t</sub>)**

</div>

Equity exposure falls when forecast volatility rises.

### MA200 + EWMA Volatility Managed

<div align="center">

**w<sub>t</sub> = Trend<sub>t</sub> × min(1, 0.12 / σ̂<sub>t+1|t</sub>)**

</div>

### Exposure-Matched Constant Mix

A constant equity allocation equal to the realized average equity exposure of the EWMA strategy.

This is an **ex-post diagnostic benchmark**, not a proposed ex-ante trading strategy.

Its purpose is to separate:

- the effect of dynamically timing risk, from
- the simpler effect of holding less equity overall.

---

# 6. Main Portfolio Results

| Strategy | CAGR | Annual Vol | Sharpe | Max Drawdown | Avg. Equity Exposure |
|---|---:|---:|---:|---:|---:|
| **Buy & Hold** | **10.10%** | 19.50% | **0.292** | -45.37% | 100.00% |
| **MA200 Trend** | 8.24% | 12.92% | 0.226 | -20.04% | 71.37% |
| **EWMA Vol Managed** | 8.12% | 11.95% | 0.226 | -19.64% | 78.79% |
| **MA200 + EWMA Vol** | 7.43% | **9.74%** | 0.186 | **-15.73%** | 60.33% |
| **Exposure-Matched Mix** | 9.54% | 15.35% | 0.291 | -37.39% | 78.79% |

The result is **not** that volatility management beat Buy & Hold.

Instead, volatility management substantially reduced portfolio risk and drawdowns while sacrificing some return.

![Strategy wealth](results/figures/04_strategy_wealth.png)

---

# 7. Drawdown Control

The difference is particularly visible during major market stress.

## 2008

| Strategy | Maximum Drawdown |
|---|---:|
| Buy & Hold | **-45.37%** |
| EWMA Vol Managed | **-14.56%** |
| Exposure-Matched Mix | -37.39% |

## 2020

| Strategy | Maximum Drawdown |
|---|---:|
| Buy & Hold | **-38.44%** |
| EWMA Vol Managed | **-19.64%** |
| Exposure-Matched Mix | -31.30% |

The exposure-matched benchmark held almost exactly the same **average equity exposure** as the EWMA strategy, but experienced substantially larger crisis drawdowns.

This suggests that dynamic exposure timing materially altered **path risk**, even though it did not improve average Sharpe ratio.

![Strategy drawdowns](results/figures/05_strategy_drawdowns.png)

---

# 8. How Volatility Management Works

The strategy lowers equity exposure when forecast volatility rises and restores exposure as volatility declines.

![EWMA equity exposure](results/figures/06_ewma_equity_exposure.png)

A critical limitation is that volatility targeting is **reactive, not clairvoyant**.

It cannot avoid the initial market shock. Exposure is reduced only after higher volatility has been observed and incorporated into the forecast.

---

# 9. Forecast Accuracy vs Portfolio Performance

An important result is that the model with the best statistical volatility forecast did **not** produce the best volatility-managed portfolio.

| Strategy | CAGR | Annual Vol | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|
| **Rolling20 Vol Managed** | **7.79%** | 11.90% | **0.200** | -18.98% |
| **EWMA94 Vol Managed** | 7.14% | 11.83% | 0.150 | -19.64% |
| **GARCH11 Vol Managed** | 7.53% | **11.46%** | 0.183 | **-18.51%** |
| **Buy & Hold** | 8.89% | 16.16% | 0.248 | -38.44% |

GARCH had the best out-of-sample QLIKE.

However, Rolling20 generated the highest Sharpe among the volatility-managed portfolios.

> **Better statistical forecast accuracy does not automatically imply better investment performance.**

Portfolio performance also depends on exposure, forecast smoothness, turnover, and the timing of market recoveries.

---

# 10. Bootstrap Uncertainty

Sharpe ratios estimated from one historical market path are noisy.

The project uses a **paired circular block bootstrap**, resampling identical market blocks for both strategies in each comparison.

The quantity being estimated is:

<div align="center">

**ΔSharpe = Sharpe<sub>A</sub> − Sharpe<sub>B</sub>**

</div>

## Results

| Comparison | Sharpe Difference | 95% Bootstrap CI |
|---|---:|---:|
| EWMA Vol − Buy & Hold | -0.0666 | [-0.2776, 0.1405] |
| EWMA Vol − Exposure Mix | -0.0649 | [-0.2642, 0.1359] |
| Trend + Vol − Buy & Hold | -0.1064 | [-0.5216, 0.3008] |

All confidence intervals contain zero.

The historical sample therefore does **not provide strong evidence of a reliable Sharpe-ratio difference** between the strategies.

This does not prove that their true Sharpe ratios are identical.

![Bootstrap Sharpe difference](results/figures/07_bootstrap_sharpe_difference.png)

---

# 11. Robustness Analysis

Reasonable alternative assumptions are reported without selecting the best-performing configuration after seeing the results.

## Volatility Target

| Target | CAGR | Annual Vol | Sharpe | Max Drawdown | Avg. Exposure |
|---|---:|---:|---:|---:|---:|
| 10% | 8.08% | 10.37% | 0.240 | -17.83% | 69.34% |
| 12% | 8.10% | 11.98% | 0.224 | -21.00% | 78.79% |
| 15% | 8.56% | 13.73% | 0.243 | -24.94% | 87.76% |

Higher volatility targets led to greater equity exposure, greater realized volatility, and generally deeper drawdowns.

## Transaction Costs

| Cost | CAGR | Sharpe |
|---|---:|---:|
| 0 bps | 8.24% | 0.235 |
| 5 bps | 8.12% | 0.226 |
| 10 bps | 8.01% | 0.217 |
| 20 bps | 7.78% | 0.199 |

Performance weakens gradually as costs rise rather than collapsing under modest transaction costs.

## Execution Lag

| Execution Lag | CAGR | Annual Vol | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|
| 1 day | 8.12% | 11.95% | 0.226 | -19.64% |
| 2 days | 8.26% | 12.02% | 0.236 | -22.31% |

The qualitative result does not depend on exact one-day implementation.

## Bootstrap Block Length

| Block Length | Sharpe Difference | 95% CI |
|---|---:|---:|
| 10 | -0.0649 | [-0.2698, 0.1431] |
| 15 | -0.0649 | [-0.2692, 0.1515] |
| 40 | -0.0649 | [-0.2743, 0.1460] |

Zero remains inside every interval.

## Trend Window

| MA Window | CAGR | Sharpe | Max Drawdown |
|---|---:|---:|---:|
| 100 days | 10.09% | 0.364 | -17.06% |
| 200 days | 8.01% | 0.209 | -21.72% |

The MA100 rule performed materially better in this sample.

However, the project's headline **MA200 specification is not retrospectively replaced** based on this observation.

Instead, the difference is reported as evidence of parameter sensitivity.

---

# 12. Data Quality Checks

The primary market series is the NIFTY 50 index:

```text
^NSEI
```

downloaded through `yfinance`.

NIFTYBEES was also investigated as a tradeable ETF proxy.

Its Yahoo Finance history contained severe discontinuities that were not corrected by the adjusted-price field, including implausibly large daily returns.

Rather than manually deleting suspicious observations, NIFTYBEES was excluded from the primary analysis.

This is a practical example of why financial data validation must occur **before modelling**.

---

# 13. Repository Structure

```text
nifty-volatility-risk-management/
│
├── README.md
├── PROTOCOL.md
├── requirements.txt
├── .gitignore
│
├── notebooks/
│   └── 01_end_to_end_analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── volatility.py
│   ├── backtest.py
│   ├── metrics.py
│   └── bootstrap.py
│
├── data/
│   └── README.md
│
└── results/
    ├── figures/
    └── tables/
```

The notebook contains the complete empirical workflow.

Reusable forecasting, backtesting, risk, and bootstrap functionality is separated into the `src/` modules.

---

# 14. Reproducing the Analysis

Clone:

```bash
git clone https://github.com/ShivasheeshDubey/nifty-volatility-risk-management.git
cd nifty-volatility-risk-management
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Then open:

```text
notebooks/01_end_to_end_analysis.ipynb
```

The notebook downloads NIFTY data programmatically using `yfinance`.

---

# 15. Experimental Discipline

The primary specifications were fixed before interpreting final strategy performance:

| Component | Primary Specification |
|---|---|
| Rolling window | 20 trading days |
| EWMA decay | λ = 0.94 |
| GARCH | GARCH(1,1) |
| Volatility target | 12% |
| Trend rule | MA200 |
| Transaction cost | 5 bps |
| Execution lag | 1 trading day |
| Forecast loss | QLIKE |
| Bootstrap block length | 15 trading days |

Alternative specifications are reported as robustness checks rather than used to retrospectively redefine the strategy.

See [`PROTOCOL.md`](PROTOCOL.md) for the complete experimental protocol.

---

# 16. Limitations

- Daily squared returns are noisy proxies for latent conditional variance.
- Normal VaR may not adequately represent fat-tailed returns.
- Volatility-targeting strategies react to shocks rather than predict the first shock.
- Results are based on one equity market and one historical sample.
- Transaction costs are simplified.
- The current analysis uses a simplified cash/risk-free-rate assumption.
- The exposure-matched benchmark is an ex-post diagnostic.
- Bootstrap inference quantifies sampling uncertainty but does not remove model uncertainty.
- 2026 is a partial calendar year.

---

# 17. Key Findings

### 1. GARCH produced the strongest overall volatility forecasts

GARCH(1,1) achieved the lowest out-of-sample QLIKE and MSE, while EWMA achieved the lowest MAE.

### 2. Better forecasts did not automatically produce better portfolios

GARCH had the strongest statistical forecast accuracy, yet Rolling20 produced the highest Sharpe among the volatility-managed portfolios over their common evaluation period.

### 3. Volatility management materially reduced crisis drawdowns

Full-sample maximum drawdown fell from approximately:

<div align="center">

**45.4% → 19.6%**

</div>

for Buy & Hold versus the EWMA volatility-managed strategy.

This risk reduction came with lower CAGR and no improvement in sample Sharpe.

### 4. Sharpe differences remained statistically uncertain

Paired block-bootstrap confidence intervals contained zero across all primary comparisons and remained similar under alternative block lengths.

---

# Conclusion

This project highlights an important distinction in quantitative investing:

> **Forecast accuracy, portfolio performance, and risk control are related — but they are not the same objective.**

GARCH improved statistical volatility forecasting.

Volatility-managed allocation materially changed the path of portfolio risk and reduced severe drawdowns.

However, those benefits did not translate into higher sample Sharpe ratios relative to Buy & Hold or an exposure-matched constant allocation.

In this experiment, volatility forecasting was therefore more useful as a **risk-management tool** than as evidence of a standalone return-enhancing trading strategy.

---

## Disclaimer

This repository is an academic and educational project.

**It is not investment advice.**
