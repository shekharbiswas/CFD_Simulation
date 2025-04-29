# CFD Portfolio Simulation and Hypotheses Testing

# ---
# 1. Project Overview

# Hypotheses (from Chapter 13.2):
# H1: CFDs improve portfolio returns.
# H2: CFDs increase portfolio risk (volatility, drawdown).
# H3: CFDs may enhance diversification during crises.

# TCCM Framework:
# Theory: Modern Portfolio Theory, CAPM, Leverage and Risk Management Theories
# Context: Portfolio Management under Crisis Conditions (COVID-19 2020, Hypothetical 2025)
# Characteristics: Compare traditional vs CFD-enhanced portfolios
# Methods: Python simulation using historical index data, leverage modeling, risk metrics calculation

# ---
# 2. Data Collection

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Download data for SPY (S&P500 ETF) and QQQ (NASDAQ100 ETF)
tickers = ['SPY', 'QQQ']
start_date = '2018-01-01'
end_date = '2024-01-01'

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
returns = data.pct_change().dropna()

# ---
# 3. Portfolio Construction

# Classic Portfolio: Equal weights
weights_classic = np.array([0.5, 0.5])

# CFD Portfolio: leverage on QQQ (e.g., 3x leverage)
leverage_QQQ = 3
returns_cfd = returns.copy()
returns_cfd['QQQ'] = returns['QQQ'] * leverage_QQQ
weights_cfd = np.array([0.5, 0.5])

# Portfolio Returns
classic_returns = returns @ weights_classic
cfd_returns = returns_cfd @ weights_cfd

# ---
# 4. Metrics Calculation

def calculate_metrics(portfolio_returns, risk_free_rate=0.01):
    mean_return = np.mean(portfolio_returns) * 252
    volatility = np.std(portfolio_returns) * np.sqrt(252)
    sharpe_ratio = (mean_return - risk_free_rate) / volatility

    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    # Value at Risk (95%)
    var_95 = np.percentile(portfolio_returns, 5)

    # Expected Shortfall (95%)
    es_95 = portfolio_returns[portfolio_returns <= var_95].mean()

    return {
        'Annualized Return': mean_return,
        'Annualized Volatility': volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown,
        'VaR (95%)': var_95,
        'Expected Shortfall (95%)': es_95
    }

# Calculate metrics
classic_metrics = calculate_metrics(classic_returns)
cfd_metrics = calculate_metrics(cfd_returns)

# Display metrics
classic_metrics_df = pd.DataFrame.from_dict(classic_metrics, orient='index', columns=['Classic Portfolio'])
cfd_metrics_df = pd.DataFrame.from_dict(cfd_metrics, orient='index', columns=['CFD Portfolio'])

metrics_comparison = pd.concat([classic_metrics_df, cfd_metrics_df], axis=1)
metrics_comparison

# ---
# 5. Results Visualization

plt.figure(figsize=(14,7))
(1 + classic_returns).cumprod().plot(label='Classic Portfolio')
(1 + cfd_returns).cumprod().plot(label='CFD Portfolio', linestyle='--')
plt.title('Portfolio Growth Comparison')
plt.ylabel('Portfolio Value (Normalized)')
plt.xlabel('Date')
plt.legend()
plt.grid(True)
plt.show()

# ---
# 6. Hypotheses Testing

print("\n--- Hypotheses Testing Results ---\")
if cfd_metrics['Annualized Return'] > classic_metrics['Annualized Return']:
    print("✅ H1 Supported: CFDs improved portfolio returns.")
else:
    print("❌ H1 Not Supported: CFDs did not improve returns.")

if cfd_metrics['Annualized Volatility'] > classic_metrics['Annualized Volatility'] or \
   cfd_metrics['Max Drawdown'] < classic_metrics['Max Drawdown']:
    print("✅ H2 Supported: CFDs increased portfolio risk.")
else:
    print("❌ H2 Not Supported: No significant risk increase observed.")

# H3: Diversification is more complex — requires correlation analysis, done in future versions.

# ---
# End of Notebook
