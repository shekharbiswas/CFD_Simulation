import numpy as np
import pandas as pd

def calculate_metrics(portfolio_values, sofr_series=None, trading_days_per_year=252):
    """Calculates performance and risk metrics for a portfolio series."""
    if portfolio_values.empty or len(portfolio_values) < 2:
        return {
            'Total Return': np.nan, 'Annualized Return': np.nan, 'Annualized Volatility': np.nan,
            'Sharpe Ratio': np.nan, 'Max Drawdown': np.nan, 'VaR 95%': np.nan, 'ES 95%': np.nan
        }

    # Ensure clean numeric data
    portfolio_values = pd.to_numeric(portfolio_values, errors='coerce').dropna()
    if len(portfolio_values) < 2: return calculate_metrics(pd.Series([], dtype=float)) # Recurse with empty

    daily_returns = portfolio_values.pct_change().dropna()

    if daily_returns.empty:
         return calculate_metrics(pd.Series([], dtype=float)) # Recurse with empty

    total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1

    # Use number of trading days in the segment for annualization
    num_trading_days = len(daily_returns)
    years = num_trading_days / trading_days_per_year if trading_days_per_year > 0 else 0

    # More stable calculation using average daily return for annualization
    # Avoid annualizing periods shorter than a year (or adjust logic if needed)
    if years >= 0.5: # Arbitrary threshold to avoid extreme annualization of short periods
        annualized_return = daily_returns.mean() * trading_days_per_year
        annualized_volatility = daily_returns.std() * np.sqrt(trading_days_per_year)
    else:
        annualized_return = daily_returns.mean() * num_trading_days # Simple cumulative return rate for short periods
        annualized_volatility = daily_returns.std() * np.sqrt(num_trading_days) # Unannualized volatility


    # Risk-free rate
    risk_free_rate = 0.0
    if sofr_series is not None and not sofr_series.empty:
        # Align SOFR dates to the period of the portfolio_values
        aligned_sofr = sofr_series.reindex(portfolio_values.index).ffill().bfill()
        if not aligned_sofr.empty:
            risk_free_rate = aligned_sofr.mean() # Use average annual SOFR for the period

    # Sharpe Ratio
    if annualized_volatility is not None and annualized_volatility != 0 and not np.isnan(annualized_volatility):
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    else:
        sharpe_ratio = np.nan

    # Max Drawdown
    rolling_max = portfolio_values.cummax()
    daily_drawdown = portfolio_values / rolling_max - 1.0
    max_drawdown = daily_drawdown.min()
    if np.isinf(max_drawdown): max_drawdown = np.nan # Handle potential inf

    # VaR 95% (Historical)
    var_95 = daily_returns.quantile(0.05)

    # ES 95% (Historical)
    es_95 = daily_returns[daily_returns <= var_95].mean()

    return {
        'Total Return': total_return if not np.isnan(total_return) else np.nan,
        'Annualized Return': annualized_return if not np.isnan(annualized_return) else np.nan,
        'Annualized Volatility': annualized_volatility if not np.isnan(annualized_volatility) else np.nan,
        'Sharpe Ratio': sharpe_ratio if not np.isnan(sharpe_ratio) else np.nan,
        'Max Drawdown': max_drawdown if not np.isnan(max_drawdown) else np.nan,
        'VaR 95%': -var_95 if not np.isnan(var_95) else np.nan, # Report as positive loss
        'ES 95%': -es_95 if not np.isnan(es_95) else np.nan    # Report as positive loss
    }

if __name__ == '__main__':
    # Example Usage
    idx = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
    vals = pd.Series([100, 101, 100, 102, 101.5], index=idx)
    sofr = pd.Series([0.01, 0.01, 0.01, 0.01, 0.01], index=idx)
    metrics = calculate_metrics(vals, sofr)
    print("\nExample Metrics:")
    import json
    print(json.dumps(metrics, indent=2))

    # Example with NaN
    vals_nan = pd.Series([100, 101, np.nan, 102, 101.5], index=idx)
    metrics_nan = calculate_metrics(vals_nan, sofr)
    print("\nExample Metrics with NaN:")
    print(json.dumps(metrics_nan, indent=2))
