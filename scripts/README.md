# CFD Portfolio Simulation

## Overview

This project analyzes how Contracts for Difference (CFDs) impact portfolio performance and risk.  
It compares a traditional portfolio with a CFD-enhanced portfolio by using real historical data, applying leverage, and evaluating risk-return profiles.

The project is built on a clear, structured framework to ensure every step — from hypothesis formulation to data-driven testing — is transparent and logical.

The main objectives are:
- To assess whether CFDs can improve portfolio returns
- To measure the impact of leverage on risk
- To understand how portfolios behave under normal and crisis conditions

---

## What is a CFD?

A **Contract for Difference (CFD)** is a financial contract where two parties exchange the difference between the entry and exit price of an asset, without owning the actual asset.

Key features of CFDs:
- **Leverage**: Control a larger position with a smaller amount of capital
- **Flexibility**: Trade both rising and falling markets
- **Higher risk**: Losses can be magnified as much as profits

CFDs are popular tools among investors seeking quick market exposure or hedging opportunities, but they require careful risk management due to their leverage.

---

## Simulation Approach

This project follows a structured approach to ensure completeness and credibility:

### 1. Project Setup
- Introduction to CFDs and portfolio leverage concepts
- Formulation of clear hypotheses:
  - H1: CFDs can improve portfolio returns
  - H2: CFDs increase portfolio risk
  - H3: CFDs can affect diversification behavior

### 2. Data Collection
- Historical price data of major indices (e.g., S&P500, NASDAQ100) downloaded using real-world sources.

### 3. Portfolio Construction
- **Classic Portfolio**: Simple allocation between two major indices without leverage.
- **CFD-Enhanced Portfolio**: Applying leverage (e.g., 3x exposure) to simulate CFD behavior on selected assets.

### 4. Metrics Calculation
For both portfolios, key financial metrics are calculated:
- **Annualized Return**
- **Annualized Volatility**
- **Sharpe Ratio**
- **Maximum Drawdown**
- **Value at Risk (VaR 95%)**
- **Expected Shortfall (Conditional VaR 95%)**

### 5. Results Visualization
- Growth curves and drawdown charts comparing the two portfolios over time.
- Risk-return tables to highlight the trade-offs introduced by CFDs.

### 6. Hypotheses Testing
- Directly evaluate the formulated hypotheses by comparing portfolio performance and risk metrics.

---

## Project Structure and Framework (TCCM)

| Category | Description |
|:---|:---|
| **Theory** | Modern Portfolio Theory, CAPM, risk-return trade-off theories, leverage impact. |
| **Context** | Investment management under both normal and crisis market conditions. |
| **Characteristics** | Comparison between traditional and CFD-leveraged portfolios based on standard risk and performance metrics. |
| **Methods** | Quantitative simulation using Python, statistical risk analysis, real market data application. |

Each element ensures that the project is based on sound financial theory, realistic market scenarios, and systematic evaluation methods.

---

## Why This Project is Valuable

- **Clear and focused**: Straightforward simulation of real-world portfolio management scenarios involving leveraged products.
- **Data-driven**: Uses historical price data to ensure realistic performance simulation.
- **Complete**: Covers return, risk, drawdowns, and tail-risk metrics for a full portfolio evaluation.
- **Educational**: Demonstrates both the opportunities and dangers of using leverage via CFDs.

This project provides a practical, structured view into how CFDs can affect investment outcomes and risk management decisions.

---
