# Simulation Steps

## Overview

This notebook simulates and compares two types of investment portfolios:

- **Classic Portfolio**: A traditional portfolio with simple equal-weight allocation.
- **CFD-Enhanced Portfolio**: A leveraged portfolio simulating the use of Contracts for Difference (CFDs).

The simulation is structured logically to follow clear hypotheses and uses standard financial risk and performance metrics.


## Simulation Steps

### 1. Project Setup

- **Objective**: Analyze how CFDs affect returns, risk, and diversification.
- **Hypotheses Formulated**:
  - H1: CFDs improve portfolio returns.
  - H2: CFDs increase portfolio risk.
  - H3: CFDs may affect diversification during crises.
- **Framework Used**: TCCM (Theory, Context, Characteristics, Methods) to ensure structured evaluation.

### 2. Data Collection

- Historical daily price data for two major US indices is downloaded:
  - **SPY** (S&P 500 ETF)
  - **QQQ** (NASDAQ 100 ETF)
- Data source: Yahoo Finance (`yfinance` library).

### 3. Portfolio Construction

- **Classic Portfolio**:
  - 50% SPY, 50% QQQ
  - No leverage applied.

- **CFD-Enhanced Portfolio**:
  - 50% SPY, 50% leveraged QQQ (e.g., 3x leverage).
  - Leverage simulates the effect of using CFDs.

### 4. Metrics Calculation

Key risk and return metrics are calculated for both portfolios:

- **Annualized Return**: Measures overall portfolio growth per year.
- **Annualized Volatility**: Measures how much returns fluctuate.
- **Sharpe Ratio**: Risk-adjusted performance (return vs. volatility).
- **Maximum Drawdown**: Largest portfolio value loss during the period.
- **Value at Risk (VaR 95%)**: Maximum expected loss at a 95% confidence level.
- **Expected Shortfall (ES 95%)**: Average loss beyond the VaR threshold.

All metrics are calculated using standard financial formulas and assumptions (252 trading days per year).

### 5. Results Visualization

- **Portfolio Growth**: Line charts showing cumulative returns over time.
- **Drawdown Analysis**: Visualization of portfolio drawdowns from historical peaks.
- **Comparison Table**: Summary table comparing risk and performance metrics side-by-side.

### 6. Hypotheses Testing

Each hypothesis is evaluated based on the results:

- **H1**: Did the CFD-enhanced portfolio show higher returns?
- **H2**: Did the CFD-enhanced portfolio show higher risk (volatility, drawdowns)?
- **H3**: (Partially evaluated) Diversification effects considered for future expansion.

A clear success/failure statement is printed for each hypothesis based on actual data.



## Why This Simulation Matters

- **Structured Approach**: Hypotheses-driven, not random testing.
- **Real Data**: Ensures realistic performance behavior.
- **Comprehensive Metrics**: Both return and risk sides are fully analyzed.
- **Clarity**: Clear steps make it easy to understand, replicate, and expand.

This simulation gives a practical, insightful look into how leveraged products like CFDs influence portfolio outcomes — helping investors make better-informed decisions.


