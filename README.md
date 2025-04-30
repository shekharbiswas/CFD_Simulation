## 📘 Project Introduction

This project investigates how **Contracts for Difference (CFDs)** can be strategically integrated into modern investment portfolios to manage return, risk, and crisis resilience. 

CFDs are **derivative instruments** that allow investors to speculate on asset price movements without actually owning the underlying security. This makes them extremely flexible — and extremely risky.

In traditional investing, portfolio composition focuses on diversification, capital preservation, and long-term growth. However, during **periods of high market volatility**, traditional portfolios may not respond quickly or effectively enough to protect investor capital.

CFDs, when used responsibly, can provide **flexibility, leverage, and tactical agility**. They enable both long and short exposure and can be deployed to hedge against downturns or exploit short-term market opportunities.

This project compares a **classic stock/ETF portfolio** with a **CFD-enhanced portfolio** that includes leveraged and short CFD positions.

Simulations are run across **stable markets and crisis scenarios** (like the COVID-19 crash of 2020), allowing us to evaluate real-world implications of using CFDs in portfolio design.

We use historical price data to analyze key financial metrics such as:
- Total Return & Volatility  
- Sharpe Ratio (risk-adjusted return)  
- Maximum Drawdown  
- Value at Risk (VaR) and Expected Shortfall (ES)

The project further applies **VIX-based hedging**, simulating CFD strategies that automatically trigger when market volatility exceeds defined thresholds.

By combining **financial theory** with **quantitative simulation**, we test how CFDs influence portfolio behavior under stress and in normal conditions.


### 🔍 Why It Matters

- **Practical insight**: Helps portfolio managers and investors understand when and how to use CFDs safely.
- **Risk education**: Quantifies how leverage affects portfolio drawdowns and returns.
- **Crisis resilience**: Offers ideas for hedging and stabilizing portfolios in unpredictable markets.


## 🎯 Project Goals

- Simulate two portfolios:
  - A **traditional portfolio** using stocks and ETFs
  - A **CFD-enhanced portfolio** introducing leveraged CFD positions
- Evaluate performance across:
  - Return and volatility
  - Sharpe Ratio
  - Maximum Drawdown
  - Value at Risk (VaR) and Expected Shortfall (ES)
  - Diversification
- Model crisis responses (e.g., COVID-19 crash 2020, hypothetical 2025 event)
- Assess hedging performance using CFDs and volatility indicators like the **VIX**



## 📘 What Are CFDs?

A Contract for Difference is a derivative contract where traders exchange the difference in asset value between the opening and closing of the position. CFDs offer:

- **No ownership** of the underlying asset
- **Leverage**, allowing large exposure for small margin
- **Two-way trading**, enabling long and short positions
- **Higher risk and return**, due to amplified exposure



## 💼 Relevance for Portfolio Managers

CFDs provide flexibility in:

- **Hedging** without liquidating core holdings
- **Tactical shifts** across markets or sectors
- **Cost efficiency**, especially for shorting
- **Quick exposure** to indices, stocks, forex, or commodities



## 🧪 Methodology

Two model portfolios are simulated using historical price data:

1. **Base Portfolio**: traditional assets only (e.g., stocks/ETFs)
2. **CFD Portfolio**: includes leveraged and short CFD positions

Key modeling considerations:

- Historical prices from **Financial Modeling Prep (FMP)**
- CFD **costs and leverage** based on IG Markets (2024)
- Hedging strategies triggered by **VIX thresholds**
- Crisis modeling for 2020 and 2025 scenarios
- Calculations: return, volatility, Sharpe Ratio, VaR, ES, drawdown



## 📈 Hypotheses

| Category         | Hypothesis                                                  |
|------------------|-------------------------------------------------------------|
| Performance      | CFDs lead to **higher average returns**                     |
| Risk             | CFDs **increase volatility**                                |
| Sharpe Ratio     | CFDs improve **risk-adjusted returns**                      |
| Diversification  | CFDs **enhance diversification** despite leverage           |
| Crisis Response  | CFD portfolios **react more strongly** to crises            |



## 🧮 Metrics Evaluated

- Total return and volatility
- Sharpe Ratio (risk-adjusted returns)
- Maximum Drawdown (worst peak-to-trough loss)
- Value at Risk (VaR) and Expected Shortfall (ES)
- Diversification via correlation matrix
- Hedging efficiency



## 🔍 Use of VIX and MOVE

- **VIX**: S&P 500 volatility index used to trigger hedging mechanisms (e.g., VIX > 25)
- **MOVE**: Treasury market volatility index — acknowledged but not actionable via CFDs
- CFDs are applied dynamically for protection during volatility spikes



## 📉 Cost Assumptions

| Cost Component        | Treatment                     |
|-----------------------|-------------------------------|
| Commissions           | ✅ 0.1% per trade              |
| Financing (long CFDs) | ✅ Included                   |
| Spread                | ❌ Excluded                   |
| Slippage              | ❌ Excluded                   |
| Currency Conversion   | ❌ Excluded                   |
| Margin                | 10–50% depending on asset type|



## 🧭 Project Framework (TCCM)

| Element         | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **Theory**       | Modern Portfolio Theory (Markowitz), CAPM, and Hull's hedging model        |
| **Context**      | High-volatility markets like the COVID-19 crash (2020) and a 2025 scenario |
| **Characteristics** | Comparison of classic vs CFD-enhanced portfolios under normal and crisis conditions |
| **Methods**      | Python-based simulations, risk metric analysis, VIX-based dynamic hedging, crisis modeling, and interactive Streamlit dashboards |



## 🗂 Project Structure

TBD







## 👤 Who Should Use This Project?

- Finance students & educators
- Portfolio and fund managers
- Retail investors exploring leverage
- Risk management analysts
- Researchers studying market behavior under stress



## 🌐 Why This Project Matters

Mastering CFDs as part of a disciplined, risk-managed strategy helps modern investors:

- Navigate crises without panic selling
- Apply **targeted hedging** dynamically
- **Boost returns** in flat or sideways markets
- **Diversify smarter**, not just broader

By combining academic finance with applied simulations, this project aims to bridge theory and practice for today's market environment.
