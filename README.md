# Volatility Forecasting & Risk-Managed Equity Strategies on NIFTY

An empirical study of **volatility forecasting, Value-at-Risk calibration, and risk-managed equity allocation** on the NIFTY 50.

The project asks a simple question:

> Does a more accurate volatility forecast necessarily lead to a better investment strategy?

I compare simple rolling volatility, EWMA, and GARCH(1,1) forecasts out-of-sample, evaluate their risk forecasts, and use them to construct long-only volatility-managed equity strategies with transaction costs and execution lags.

---

## Project Overview

The analysis covers daily NIFTY 50 data from approximately **September 2007 to October 2026**.

The project has four main components:

1. **Volatility modelling**
   - 20-day rolling variance
   - EWMA with lambda = 0.94
   - GARCH(1,1)

2. **Out-of-sample forecast evaluation**
   - QLIKE
   - Mean Squared Error
   - Mean Absolute Error
   - calendar-year model comparisons

3. **Risk modelling**
   - 95% and 99% one-day Normal VaR
   - exception-rate analysis
   - Kupiec unconditional coverage test

4. **Portfolio construction**
   - Buy & Hold
   - moving-average trend strategy
   - volatility-managed strategy
   - trend + volatility strategy
   - exposure-matched constant allocation benchmark

Transaction costs, delayed execution, portfolio-weight drift, bootstrap uncertainty, and robustness tests are explicitly included.

---

## Research Questions

The project investigates four questions:

1. Which simple volatility model provides the strongest out-of-sample forecast of next-day NIFTY variance?
2. Are Normal VaR forecasts appropriately calibrated?
3. Does volatility targeting improve portfolio risk-adjusted performance?
4. Are the conclusions robust to reasonable choices of costs, execution lags, volatility targets, trend windows, and bootstrap assumptions?

---

# 1. Volatility Forecasting

For daily log return \(r_t\), the project compares three one-day-ahead variance forecasts.

### Rolling 20-Day Variance

\[
\hat{\sigma}^{2}_{t+1|t}
=
\frac{1}{20}
\sum_{i=0}^{19}
r_{t-i}^{2}
\]

Every observation receives equal weight until it abruptly leaves the window.

### EWMA

\[
\hat{\sigma}^{2}_{t+1|t}
=
0.94\hat{\sigma}^{2}_{t|t-1}
+
0.06r_t^2
\]

Recent shocks receive more weight and their influence decays exponentially.

### GARCH(1,1)

\[
\hat{\sigma}^{2}_{t+1|t}
=
\omega
+
\alpha r_t^2
+
\beta\hat{\sigma}^{2}_{t|t-1}
\]

GARCH parameters are estimated using an expanding window and refitted monthly. Conditional variance continues to update daily between parameter refits.

The average estimated persistence was approximately

\[
\alpha+\beta \approx 0.994,
\]

indicating highly persistent volatility dynamics.

![One-day volatility forecasts](results/figures/01_volatility_forecasts.png)

---

## Out-of-Sample Forecast Results

All models are compared over common out-of-sample dates beginning in 2015.

| Model | MAE × 1e4 | MSE × 1e8 | QLIKE |
|---|---:|---:|---:|
| GARCH(1,1) | 1.1701 | **20.5962** | **-8.4767** |
| EWMA(0.94) | **1.1473** | 20.9658 | -8.4586 |
| Rolling 20 | 1.1667 | 21.8084 | -8.4391 |

Lower loss is better.

GARCH produced the lowest **QLIKE** and **MSE**, while EWMA produced the lowest **MAE**.

Across the 11 complete calendar years from 2015–2025:

- GARCH won 8 years on QLIKE
- EWMA won 3 years
- Rolling won 0 years

This suggests that GARCH provided the strongest overall variance forecasts, although the advantage over EWMA was modest rather than overwhelming.

![Yearly QLIKE](results/figures/02_yearly_qlike.png)

---

# 2. Value-at-Risk

One-day Normal VaR is constructed directly from each volatility forecast.

For example,

\[
VaR_{95,t}
=
1.645\hat{\sigma}_{t+1|t}
\]

and

\[
VaR_{99,t}
=
2.326\hat{\sigma}_{t+1|t}.
\]

A violation occurs when the realized return is below the negative VaR threshold.

Coverage is evaluated using:

- expected versus observed exception rates
- the Kupiec unconditional coverage test
- calendar-year exception counts

The VaR analysis is intentionally kept separate from volatility-forecast accuracy because forecasting conditional variance well does not necessarily imply accurate tail-risk modelling.

![GARCH VaR during COVID](results/figures/03_garch_var_covid.png)

Detailed VaR results are available under [`results/tables/`](results/tables/).

---

# 3. Portfolio Construction

The portfolio contains NIFTY equity and cash.

For equity weight \(w_t\),

\[
R_{p,t}
=
w_tR_{equity,t}
+
(1-w_t)R_{f,t}
-
c|w_t-w_{t-1}|.
\]

The primary implementation uses:

- long-only exposure
- maximum equity weight of 100%
- 12% annualized volatility target
- weekly rebalancing for volatility-managed strategies
- 5 bps one-way transaction cost
- one-trading-day execution lag

Portfolio weights are allowed to **drift naturally between scheduled rebalances** rather than being implicitly reset every day.

---

## Strategies

### Buy & Hold

\[
w_t=1
\]

### MA200 Trend

Equity is held when price is above its 200-day moving average.

### EWMA Volatility Managed

\[
w_t
=
\min
\left(
1,
\frac{0.12}
{\hat{\sigma}_{t}}
\right)
\]

### MA200 + EWMA Volatility Managed

The volatility target is combined with the trend filter.

### Exposure-Matched Constant Mix

A constant equity allocation equal to the realized average equity exposure of the EWMA strategy.

This is an **ex-post diagnostic benchmark**, used to distinguish the effect of volatility timing from the simpler effect of holding less equity.

---

# 4. Main Portfolio Results

| Strategy | CAGR | Annual Vol | Sharpe | Max Drawdown | Avg. Equity Exposure |
|---|---:|---:|---:|---:|---:|
| Buy & Hold | **10.10%** | 19.50% | **0.292** | -45.37% | 100.00% |
| MA200 Trend | 8.24% | 12.92% | 0.226 | -20.04% | 71.37% |
| EWMA Vol Managed | 8.12% | 11.95% | 0.226 | -19.64% | 78.79% |
| MA200 + EWMA Vol | 7.43% | **9.74%** | 0.186 | **-15.73%** | 60.33% |
| Exposure-Matched Mix | 9.54% | 15.35% | 0.291 | -37.39% | 78.79% |

The primary result is **not** that volatility management outperformed the market.

Instead, volatility management substantially reduced portfolio risk and drawdowns while sacrificing some return.

![Strategy wealth](results/figures/04_strategy_wealth.png)

---

## Drawdown Control

The difference becomes particularly clear during major market stress.

### 2008

- Buy & Hold maximum drawdown: **-45.37%**
- EWMA Vol Managed: **-14.56%**
- Exposure-Matched Mix: **-37.39%**

### 2020

- Buy & Hold: **-38.44%**
- EWMA Vol Managed: **-19.64%**
- Exposure-Matched Mix: **-31.30%**

The exposure-matched portfolio held almost exactly the same average amount of equity as the EWMA strategy, but still experienced substantially larger crisis drawdowns.

This suggests that **dynamic exposure timing affected path risk**, even though it did not improve average Sharpe ratio.

![Strategy drawdowns](results/figures/05_strategy_drawdowns.png)

---

# 5. How Volatility Management Works

The strategy reduces equity exposure when forecast volatility rises and gradually restores exposure as volatility falls.

![EWMA equity exposure](results/figures/06_ewma_equity_exposure.png)

An important limitation is that this mechanism is **reactive rather than clairvoyant**.

The strategy cannot avoid the first volatility shock. Exposure falls only after higher volatility has been observed and incorporated into the forecast.

---

# 6. Forecast Accuracy vs Investment Performance

One of the most interesting findings is that the model with the best statistical volatility forecast did not produce the best volatility-managed portfolio.

Over the common 2015–2026 model-comparison period:

| Strategy | CAGR | Annual Vol | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|
| Rolling20 Vol Managed | **7.79%** | 11.90% | **0.200** | -18.98% |
| EWMA94 Vol Managed | 7.14% | 11.83% | 0.150 | -19.64% |
| GARCH11 Vol Managed | 7.53% | **11.46%** | 0.183 | **-18.51%** |
| Buy & Hold | 8.89% | 16.16% | 0.248 | -38.44% |

GARCH had the best out-of-sample QLIKE, but Rolling20 generated the highest Sharpe among the volatility-managed portfolios.

This illustrates an important distinction:

> **Better statistical forecast accuracy does not automatically imply better portfolio performance.**

Forecast smoothness, exposure levels, turnover, and the timing of market recoveries all matter.

---

# 7. Bootstrap Uncertainty

Sharpe ratios estimated from a single historical path are noisy.

The project therefore uses a **paired circular block bootstrap** so that both strategies in a comparison are resampled using identical market blocks.

Primary results:

| Comparison | Sharpe Difference | 95% Bootstrap CI |
|---|---:|---:|
| EWMA Vol − Buy & Hold | -0.0666 | [-0.2776, 0.1405] |
| EWMA Vol − Exposure Mix | -0.0649 | [-0.2642, 0.1359] |
| Trend + Vol − Buy & Hold | -0.1064 | [-0.5216, 0.3008] |

All intervals contain zero.

Therefore the historical sample does **not provide strong evidence of a reliable Sharpe-ratio difference** between these strategies.

This should not be interpreted as proof that the strategies have identical Sharpe ratios.

![Bootstrap Sharpe difference](results/figures/07_bootstrap_sharpe_difference.png)

---

# 8. Robustness

The analysis reports reasonable alternative assumptions without selecting the best-performing specification after observing the results.

### Volatility Target

Targets tested:

- 10%
- 12%
- 15%

As the target increased:

- average equity exposure increased
- realized portfolio volatility increased
- maximum drawdown generally increased

This is economically consistent with the intended strategy mechanism.

### Transaction Costs

For the 12% target with one-day execution lag:

| Cost | CAGR | Sharpe |
|---|---:|---:|
| 0 bps | 8.24% | 0.235 |
| 5 bps | 8.12% | 0.226 |
| 10 bps | 8.01% | 0.217 |
| 20 bps | 7.78% | 0.199 |

The strategy weakens gradually as costs increase rather than collapsing under modest transaction costs.

### Execution Lag

Moving from a one-day to two-day implementation lag did not qualitatively overturn the results.

### Bootstrap Block Length

The EWMA-versus-exposure-matched Sharpe confidence interval remained similar for block lengths of 10, 15, and 40 trading days.

### Trend Window

Trend strategies were more parameter-sensitive.

A 100-day moving average produced materially stronger results than the pre-specified 200-day rule.

The headline strategy is **not changed retrospectively** to exploit this observation.

---

# 9. Data Quality

The primary series is the NIFTY 50 index (`^NSEI`) downloaded using `yfinance`.

NIFTYBEES was also investigated as a tradeable ETF proxy, but its Yahoo Finance history contained severe discontinuities that were not corrected by the adjusted-price field.

Rather than manually deleting suspicious observations, the ETF series was excluded from the primary analysis.

This provides a practical example of why data validation is necessary before financial modelling.

---

# 10. Repository Structure

```text
nifty-volatility-risk-management/
│
├── README.md
├── PROTOCOL.md
├── requirements.txt
├── notebooks/
│   └── 01_end_to_end_analysis.ipynb
├── src/
│   ├── volatility.py
│   ├── backtest.py
│   ├── metrics.py
│   └── bootstrap.py
├── data/
│   └── README.md
└── results/
    ├── figures/
    └── tables/
