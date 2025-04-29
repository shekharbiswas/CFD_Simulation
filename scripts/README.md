# CFD - Simulation Steps and Strategies

## Overview

This project simulates and compares different investment portfolio strategies using Contracts for Difference (CFDs).  
It is structured logically around clear hypotheses and financial metrics, offering insights into how CFDs can enhance or impact portfolio performance and risk.

The simulations are built on a solid framework (TCCM: Theory, Context, Characteristics, Methods) and focus on both static comparisons and dynamic strategies.



## Simulation Steps

### 1. Project Setup
- **Objective**: Analyze how CFDs affect returns, risk, and diversification.
- **Hypotheses Formulated**:
  - **H1**: CFDs improve portfolio returns.
  - **H2**: CFDs increase portfolio risk.
  - **H3**: CFDs may affect diversification during crises.
- **Framework Used**: TCCM (Theory, Context, Characteristics, Methods) to ensure structured evaluation.

### 2. Data Collection
- Historical daily price data for major US indices downloaded:
  - **SPY** (S&P 500 ETF)
  - **QQQ** (NASDAQ 100 ETF)
- Data source: Yahoo Finance (`yfinance` Python library).

### 3. Portfolio Construction
- **Classic Portfolio**:
  - 50% SPY, 50% QQQ
  - No leverage applied.
- **CFD-Enhanced Portfolio**:
  - 50% SPY, 50% leveraged QQQ (e.g., 3x leverage).
  - Leverage simulates the effect of using CFDs.

### 4. Metrics Calculation
Key financial performance and risk metrics are calculated:
- **Annualized Return**: Average yearly portfolio growth.
- **Annualized Volatility**: Yearly fluctuations in portfolio returns.
- **Sharpe Ratio**: Return earned per unit of risk.
- **Maximum Drawdown**: Worst peak-to-trough decline.
- **Value at Risk (VaR 95%)**: Maximum loss at 95% confidence.
- **Expected Shortfall (ES 95%)**: Average loss beyond the VaR.

*Assumptions*: 252 trading days per year.

### 5. Results Visualization
- **Portfolio Growth**: Cumulative returns over time.
- **Drawdown Analysis**: Visualization of portfolio losses from all-time highs.
- **Comparison Table**: Clear side-by-side risk/return metrics.

### 6. Hypotheses Testing
Each hypothesis is tested directly based on calculated results:
- **H1**: Did CFDs lead to higher returns?
- **H2**: Did CFDs cause greater risk (volatility, drawdown)?
- **H3**: Diversification impact considered for future exploration.

A clear success/failure statement is printed for each hypothesis.



## Extended Simulations: Strategies and Scripts

In addition to the basic classic vs. CFD comparison, several advanced simulations are implemented to deepen the analysis:


Performance and risk analysis
1) Performance hypothesis: The use of CFDs leads to a higher average portfolio return compared to a traditional portfolio without CFDs.
 
Performance and risk analysis
2) Risk hypothesis: The use of CFDs increases the volatility of the portfolio compared to a traditional portfolio.
 
Performance and risk analysis
3) Risk-adjusted return hypothesis: The risk-adjusted return (Sharpe ratio) is higher for CFD portfolios than for traditional portfolios.
 
Performance and risk analysis
4) Diversification hypothesis: The addition of CFDs leads to better risk diversification and reduces the overall risk of the portfolio despite the leverage effect.
 
Behavior in times of crisis
5) Crisis behavior hypothesis: Portfolios with CFDs react more strongly in times of crisis than traditional portfolios.


| Script Name | Purpose | Description |
|:---|:---|:---|
| **01_classic_vs_cfd.ipynb** | Baseline Simulation | Compares traditional and CFD-enhanced portfolios under normal conditions. Tests basic return and risk differences. |
| **02_cfd_varied_leverage.ipynb** | Leverage Sensitivity | Studies how different leverage levels (e.g., 2x, 3x, 5x) affect returns, volatility, and Sharpe Ratios. |
| **03_cfd_crisis_simulation.ipynb** | Crisis Resilience | Injects simulated market crashes (-10% to -20%) and evaluates portfolio survival and recovery patterns. |
| **04_cfd_sector_rotation.ipynb** | Tactical Allocation | Simulates using CFDs to rotate exposure between sectors (e.g., technology, energy) based on simple rules. |
| **05_cfd_dynamic_risk_control.ipynb** | Smart Risk Management | Reduces CFD leverage dynamically when volatility rises, aiming to control extreme risks during crises. |
| **06_cfd_vs_margin_trading.ipynb** (optional) | Product Comparison | Compares the behavior of CFDs against traditional margin trading — differences in risk and cost structure. |

Each script builds logically upon the last, adding complexity and reflecting real-world investment decisions with CFDs.



## Why This Simulation Approach Matters

✅ **Structured and Hypotheses-Driven**: Focused on answering specific, realistic questions.  
✅ **Real Data Analysis**: Uses historical market behavior for realistic simulation.  
✅ **Comprehensive Risk Metrics**: Not just returns, but full risk spectrum evaluated.  
✅ **Clear, Modular Design**: Easy to expand, modify, or specialize simulations.  
✅ **Practical Insights**: Simulates strategies portfolio managers or investors might actually consider using.

This project provides a practical and robust view into how CFDs influence investment outcomes — demonstrating both their potential benefits and the significant risks they bring when leverage is involved.

