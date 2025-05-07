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



## 📘 What Are CFDs?

A Contract for Difference is a derivative contract where traders exchange the difference in asset value between the opening and closing of the position. CFDs offer:

- **No ownership** of the underlying asset
- **Leverage**, allowing large exposure for small margin
- **Two-way trading**, enabling long and short positions
- **Higher risk and return**, due to amplified exposure

## 📌 Objectives 

1. **Compare performance** of two portfolio models:
   - Model A: Traditional portfolio with 80% S&P 500 and 20% cash
   - Model B: CFD-hedged portfolio with S&P 500 + short CFD positions triggered by VIX > 25

2. **Evaluate portfolio risk and diversification** using:
   - Volatility (standard deviation)
   - Value at Risk (VaR)
   - Expected Shortfall (ES)
   - Sharpe Ratio
   - Maximum Drawdown

3. **Incorporate realistic CFD trading costs** based on IG Markets (2024), including:
   - Spread variation by time of day
   - Overnight financing charges based on SOFR
   - Borrowing costs and margin requirements

4. **Simulate behavior during market crises**, specifically:
   - The COVID-19 crisis (2020)
   - Projected market disruption in 2025 (modeled via VIX spikes)

5. **Use the VIX index as a hedging trigger**, activating CFD shorts when VIX exceeds a threshold (e.g., VIX > 25)

6. **Test hypotheses** regarding the effect of CFDs on:
   - Average return
   - Risk
   - Risk-adjusted return
   - Diversification
   - Crisis-period behavior


## 📊 Key Metrics

- Return, Volatility (σ)
- Sharpe Ratio
- Value at Risk (VaR)
- Expected Shortfall (ES)
- Maximum Drawdown (MDD)
- Correlation and diversification index
- Hedge efficiency index


## Data 

| **Data Source**               | **Ticker/Label** | **Used For**                                  |
|------------------------------|------------------|------------------------------------------------|
| S&P 500 Index Prices         | `^GSPC`          | Portfolio return, volatility, drawdown         |
| VIX Index Levels             | `^VIX`           | Hedging trigger logic                          |
| SOFR Rate (USD Overnight)    | `SOFR` (manual)  | CFD financing cost                             |
| CFD Cost Parameters          | Static from IG   | Cost modeling and margin requirements          |



## ⚙️ Technology Stack

- Python 3.10+
- Libraries: `pandas`, `numpy`, `matplotlib`, `scipy`, `yfinance`, `statsmodels`, `arch`, `scikit-learn`

## 📁 Project Structure

```bash
cfd_simulation/
├── data/
│   └── vix_sp500_data.csv
├── scripts/
│   ├── data_loader.py
│   ├── portfolio_models.py
│   ├── cfd_cost_model.py
│   ├── risk_metrics.py
│   ├── hedging_strategy.py
│   ├── crisis_analysis.py
│   └── simulate.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── config/
│   └── params.yaml
├── run.py
├── requirements.txt
└── README.md

```

<br>


### 🔍 Why It Matters

- **Practical insight**: Helps portfolio managers and investors understand when and how to use CFDs safely.
- **Risk education**: Quantifies how leverage affects portfolio drawdowns and returns.
- **Crisis resilience**: Offers ideas for hedging and stabilizing portfolios in unpredictable markets.


<br>


## 📜 Script Breakdown and Logic

| Script Name               | Purpose                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| `data_loader.py`          | Fetches and preprocesses VIX, S&P 500, and other index data (FMP, yfinance). |
| `portfolio_models.py`     | Defines Model A (classic) and Model B (CFD-based); calculates weights and returns. |
| `cfd_cost_model.py`       | Calculates CFD costs including spread, margin, and overnight financing. |
| `risk_metrics.py`         | Computes VaR, ES, Sharpe Ratio, Max Drawdown, volatility, and returns. |
| `hedging_strategy.py`     | Implements VIX-based dynamic hedging using short CFD positions. |
| `crisis_analysis.py`      | Isolates crisis periods (e.g., 2020, 2025) and compares model responses. |
| `simulate.py`             | Runs simulations over the full 2019–2025 timeline and applies risk/cost metrics. |
| `run.py`                  | Entry point to run the full pipeline with logging and config integration. |
| `params.yaml`             | Contains configuration: thresholds, VIX cutoff, cost rates, portfolio size. |
| `exploratory_analysis.ipynb` | Optional Jupyter notebook for plotting, preliminary data checks, and debugging. |

<br>


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

| Element           | Description                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------|
| **Theory**         | Practical finance principles: portfolio optimization, leverage mechanics, and risk hedging   |
| **Context**        | High-volatility markets such as the COVID-19 crash (2020) and a modeled future crash (2025) |
| **Characteristics**| Side-by-side simulation of traditional portfolios vs. CFD-enhanced portfolios                |
| **Methods**        | Python-based simulation engine, VIX-triggered hedge logic, risk metric analysis, and Streamlit app for interaction |



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

By combining real-world finance logic with simulation-based experimentation, this project bridges the gap between traditional portfolio construction and modern R&D for dynamic market environments.
