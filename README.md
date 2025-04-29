# CFD portfolio simulation

This project explores how Contracts for Difference (CFDs) can be strategically used to enhance or manage the performance and risk profile of investment portfolios.  
CFDs are leveraged financial instruments that allow investors to speculate on price movements of assets without owning the underlying securities.  
Due to their leverage effect, CFDs can potentially boost returns but also significantly increase risk, making them an attractive yet complex tool for modern portfolio management.

We simulate two types of portfolios: a traditional investment portfolio composed of stocks and ETFs, and a CFD-enhanced portfolio that introduces leveraged positions via CFDs.  
The goal is to assess how CFDs impact key financial metrics, including total return, volatility, Sharpe Ratio, Maximum Drawdown, Value at Risk (VaR), and Expected Shortfall (ES).

The project applies various statistical and quantitative techniques:  
- Portfolio simulations using historical price data
- Risk metric calculations (mean, standard deviation, downside risk measures)
- Crisis scenario modeling to mimic market crashes
- Correlation and diversification analysis across assets
- Comparative analysis between classic and leveraged portfolios.

By combining financial theory with practical simulation techniques, this project provides insights into the opportunities and risks associated with CFDs, particularly during periods of high market volatility like the COVID-19 crash of 2020 or hypothetical future crises.


## What is a CFD?

A **Contract for Difference (CFD)** is a financial contract between a trader and a broker to exchange the difference in the value of an asset between the time the contract opens and closes.

Key points about CFDs:
- **No ownership**: You do not own the underlying asset (e.g., a stock or index).
- **Leverage**: You can control a large position with a small amount of money (margin).
- **Two-way trading**: You can speculate on both rising (long) and falling (short) prices.
- **Higher risk and return**: Leverage magnifies both profits and losses.

In simple terms, CFDs let investors bet on price movements **with less capital** but **higher risk** compared to buying the real asset.



## Why Are CFDs Important for Portfolio Managers?

Portfolio managers use CFDs for several practical reasons:

- **Hedging**: Protect portfolios against sudden market declines without selling existing assets.
- **Flexibility**: Quickly take positions in different markets (stocks, indices, forex) without moving large amounts of capital.
- **Cost efficiency**: CFDs often have lower transaction costs compared to trading real stocks, especially when shorting.
- **Leverage Management**: Enhance returns by carefully using leverage, especially in stable markets.
- **Crisis Strategies**: During turbulent times, CFDs allow tactical shifts (e.g., shorting falling sectors) without major restructuring of the portfolio.


## Practical Use Cases of CFDs in Portfolio Management

- **Crisis Hedging**: A fund manager fearing a market crash can short the S&P 500 using CFDs while keeping long-term stock holdings untouched.
- **Sector Rotation**: Quickly moving exposure between sectors (e.g., shifting from tech stocks to energy) using sector index CFDs.
- **Currency Risk Management**: Hedging currency exposure in international portfolios without physically converting money.
- **Enhanced Yield Strategies**: Gaining additional returns in sideways markets by taking small leveraged positions.



## Goals of This Project

- Simulate **classic portfolios** (only stocks/ETFs) vs. **CFD-enhanced portfolios**.
- Understand how CFDs affect:
  - Returns
  - Volatility (risk)
  - Sharpe Ratio (risk-adjusted returns)
  - Maximum Drawdown
  - Value at Risk (VaR)
  - Diversification
- Explore performance under **crisis scenarios** (e.g., 2020 COVID crash, hypothetical 2025 crash).



## Project Framework: TCCM

This project is structured based on the **TCCM** framework (Theory, Context, Characteristics, Methods):

| Element | Description |
|:---|:---|
| **Theory** | Modern Portfolio Theory (Markowitz, 1952), Capital Asset Pricing Model (CAPM), and leverage theories related to derivative instruments like CFDs. |
| **Context** | Financial market management during high-volatility periods (COVID-19 2020 crash and hypothetical 2025 crisis). |
| **Characteristics** | Simulation of two portfolio types: traditional (stocks/ETFs) and CFD-enhanced portfolios. Comparison based on risk and return metrics. |
| **Methods** | Quantitative simulation using Python, scenario modeling, risk metric calculation, and interactive visualization through a Streamlit app. |


## Techniques We Will Apply (High Level)

- **Portfolio Simulation**: Generate return series for portfolios with and without CFDs.
- **Risk Metrics Calculation**: Calculate Sharpe Ratio, VaR, Expected Shortfall, Max Drawdown.
- **Crisis Scenario Modeling**: Simulate sudden market declines and study portfolio behavior.
- **Leverage Impact Analysis**: Measure how different levels of CFD leverage change portfolio performance.
- **Visualization**: Interactive charts and tables built with Streamlit.



## Why This Project Matters

Understanding CFDs equips investors and portfolio managers to:
- Use leverage intelligently and responsibly.
- Build resilient portfolios capable of surviving market shocks.
- Apply hedging strategies without disrupting core investments.
- Improve portfolio returns when used in a controlled, risk-managed way.

Mastering CFDs can significantly widen the tactical options available in modern portfolio management.


## Who Should Use This Project?

- Finance students
- Aspiring portfolio managers
- Retail investors seeking to understand leverage
- Risk management professionals
- Anyone interested in learning about modern investing tools





