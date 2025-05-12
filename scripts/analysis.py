import pandas as pd
from scripts import risk_metrics

def run_analysis(portfolio_a, portfolio_b, df_data, config):
    """Performs comparative analysis and hypothesis testing."""

    results = {}
    portfolio_comparison = pd.concat([portfolio_a, portfolio_b], axis=1).dropna()

    if portfolio_comparison.empty:
        print("Warning: No common dates between portfolio simulations. Analysis cannot proceed.")
        return None

    # --- Metrics Calculation ---
    sofr_series = df_data[config['sofr_column']]
    trading_days = config['trading_days_per_year']

    # Full Period
    metrics_full = {
        'Model A': risk_metrics.calculate_metrics(portfolio_comparison['Portfolio_A'], sofr_series, trading_days),
        'Model B': risk_metrics.calculate_metrics(portfolio_comparison['Portfolio_B'], sofr_series, trading_days)
    }
    results['full_period'] = pd.DataFrame(metrics_full)

    # Crisis Periods
    results['crisis'] = {}
    for name, period in config.get('crisis_periods', {}).items():
        start = period['start']
        end = period['end']
        portfolio_slice = portfolio_comparison.loc[start:end]
        sofr_slice = sofr_series.loc[start:end] if sofr_series is not None else None

        if portfolio_slice.empty:
            print(f"Warning: No data available for crisis period '{name}' ({start} to {end}). Skipping.")
            continue

        metrics_crisis = {
            'Model A': risk_metrics.calculate_metrics(portfolio_slice['Portfolio_A'], sofr_slice, trading_days),
            'Model B': risk_metrics.calculate_metrics(portfolio_slice['Portfolio_B'], sofr_slice, trading_days)
        }
        results['crisis'][name] = pd.DataFrame(metrics_crisis)


    # --- Hypothesis Testing (Qualitative based on metrics) ---
    hypotheses = {}
    try:
        m_full_a = metrics_full['Model A']
        m_full_b = metrics_full['Model B']

        # 1) Performance Hypothesis: Higher average return for CFD (Model B)
        h1 = m_full_b['Annualized Return'] > m_full_a['Annualized Return']
        hypotheses['H1_Higher_Return_B'] = 'Supported' if h1 else 'Not Supported'

        # 2) Risk Hypothesis: Higher volatility for CFD (Model B)
        h2 = m_full_b['Annualized Volatility'] > m_full_a['Annualized Volatility']
        hypotheses['H2_Higher_Vol_B'] = 'Supported' if h2 else 'Not Supported'

        # 3) Risk-Adjusted Return Hypothesis: Higher Sharpe Ratio for CFD (Model B)
        h3 = m_full_b['Sharpe Ratio'] > m_full_a['Sharpe Ratio']
        hypotheses['H3_Higher_Sharpe_B'] = 'Supported' if h3 else 'Not Supported'

        # 4) Diversification Hypothesis: Reduces overall portfolio risk (Lower Vol or MDD for B)
        h4 = (m_full_b['Max Drawdown'] > m_full_a['Max Drawdown']) or \
             (m_full_b['Annualized Volatility'] < m_full_a['Annualized Volatility'])
        hypotheses['H4_Lower_Risk_B'] = 'Supported' if h4 else 'Not Supported'

        # 5) Crisis Behavior Hypothesis: B reacts more strongly (magnitude of return/drawdown)
        h5_details = {}
        for name, metrics_df in results['crisis'].items():
             mc_a = metrics_df['Model A']
             mc_b = metrics_df['Model B']
             # Compare magnitude of total return during crisis
             h5_crisis = abs(mc_b['Total Return']) > abs(mc_a['Total Return'])
             h5_details[f'H5_Stronger_React_B_{name}_Return'] = 'Supported' if h5_crisis else 'Not Supported'
             h5_details[f'H5_{name}_MDD_B'] = mc_b['Max Drawdown']
             h5_details[f'H5_{name}_MDD_A'] = mc_a['Max Drawdown']
        hypotheses['H5_Crisis_Behavior'] = h5_details

    except KeyError as e:
        print(f"Warning: Could not perform hypothesis testing, metric missing: {e}")
    except Exception as e:
         print(f"Warning: Error during hypothesis testing: {e}")


    results['hypotheses'] = hypotheses
    print("Analysis complete.")
    return results
