import pandas as pd
import numpy as np

# Import your custom modules
import config as cfg # Assuming your config file is named config.py
import data_loader
import signal_generation
import simulation_engine
import risk_metrics
import plotting

def format_metrics_for_print(metrics_dict):
    """Converts numeric metrics to appropriate string formats for printing."""
    formatted = metrics_dict.copy()
    for key, value in formatted.items():
        if isinstance(value, float):
            if "Return" in key or "Volatility" in key or "Drawdown" in key or \
               "VaR" in key or "CVaR" in key or "Win %" in key or "Loss %" in key:
                if not pd.isna(value):
                    formatted[key] = f"{value*100:.2f}%"
                else:
                    formatted[key] = "N/A"
            elif "Ratio" in key or "Factor" in key or "Omega" in key:
                 if not pd.isna(value):
                    formatted[key] = f"{value:.2f}"
                 else:
                    formatted[key] = "N/A"
            elif key in ["Skewness", "Kurtosis"]:
                 if not pd.isna(value):
                    formatted[key] = f"{value:.2f}"
                 else:
                    formatted[key] = "N/A"
            # Add other specific formatting if needed
    return formatted


def main():
    print("--- Starting Final Analysis ---")
    pd.set_option('display.float_format', lambda x: '%.4f' % x)

    # 1. Load and Prepare Data
    df_market_data = data_loader.load_and_prepare_market_data(cfg)
    if df_market_data.empty:
        print("Exiting due to data loading issues.")
        return

    # 2. Generate VIX Momentum Signals
    df_sim_full = signal_generation.generate_vix_momentum_signals(df_market_data, cfg)

    # Drop rows with NaN in essential columns for simulation after all calculations
    essential_cols_for_sim = ['SP500_Return', 'S&P500', 'SOFR_Rate', 'VIX', 
                              'Short_Signal_Today', 'Cover_Signal_Momentum_Today', 
                              'Cover_Signal_Absolute_VIX_Today']
    df_sim_full = df_sim_full.dropna(subset=essential_cols_for_sim).copy()
    df_sim_full.reset_index(drop=True, inplace=True)

    if df_sim_full.empty:
        print("No data available for simulation after NaN drop. Exiting.")
        return
        
    RFR_ANNUAL = df_sim_full[cfg.TARGET_SOFR_COL_NAME].mean()
    print(f"Average Annualized SOFR (Risk-Free Rate): {RFR_ANNUAL*100:.4f}%")
    print(f"Simulation period from {df_sim_full['date'].min().date()} to {df_sim_full['date'].max().date()} ({len(df_sim_full)} days).\n")

    # Plot S&P 500 and VIX
    plotting.plot_market_data(df_sim_full[['date', 'S&P500', 'VIX']])

    # --- Full Period Simulations & Metrics ---
    print("--- Running Full Period Simulations ---")
    values_A_full = simulation_engine.simulate_portfolio_A(df_sim_full, cfg.INITIAL_CAPITAL, cfg.EQUITY_ALLOC_A)
    values_B_momentum_full = simulation_engine.simulate_portfolio_B_momentum(df_sim_full, cfg.INITIAL_CAPITAL, cfg)
    print("Simulations complete.")

    returns_A_full = values_A_full.pct_change().fillna(0)
    returns_B_momentum_full = values_B_momentum_full.pct_change().fillna(0)

    print("\n--- Full Period Metrics ---")
    portfolio_B_label_full = f"B (Momentum HR:{cfg.MODEL_B_FIXED_HEDGE_RATIO_MOMENTUM:.2f})"
    metrics_A_full = risk_metrics.calculate_metrics_summary(
        cfg.PORTFOLIO_A_LABEL, values_A_full, returns_A_full, RFR_ANNUAL, cfg.INITIAL_CAPITAL, cfg.TRADING_DAYS_PER_YEAR
    )
    metrics_B_full = risk_metrics.calculate_metrics_summary(
        portfolio_B_label_full, values_B_momentum_full, returns_B_momentum_full, RFR_ANNUAL, cfg.INITIAL_CAPITAL, cfg.TRADING_DAYS_PER_YEAR
    )
    
    # Format for printing
    formatted_metrics_A = format_metrics_for_print(metrics_A_full)
    formatted_metrics_B = format_metrics_for_print(metrics_B_full)
    
    results_df_full = pd.DataFrame([formatted_metrics_A, formatted_metrics_B])
    print(results_df_full.set_index('Portfolio').T)

    # Plot Full Period Performance
    df_plot_full = pd.DataFrame({
        'date': df_sim_full['date'],
        cfg.PORTFOLIO_A_LABEL: values_A_full,
        portfolio_B_label_full: values_B_momentum_full
    }).melt(id_vars=['date'], var_name='Portfolio', value_name='Value')
    
    color_map_full = {
        cfg.PORTFOLIO_A_LABEL: cfg.COLOR_A,
        portfolio_B_label_full: cfg.COLOR_B
    }
    plotting.plot_portfolio_performance(df_plot_full, title=cfg.PLOT_TITLE_PERFORMANCE, color_map=color_map_full)

    # --- Hypothesis Testing (Full Period) ---
    print("\n--- Hypothesis Testing (Full Period) ---")
    # H1
    h1_status = "Supported" if metrics_B_full['Annualized Return'] > metrics_A_full['Annualized Return'] else "Not Supported"
    print(f"H1: CFDs lead to higher average returns. Finding: {h1_status}. Detail: Annualized Return (B: {metrics_B_full['Annualized Return']*100:.2f}% vs A: {metrics_A_full['Annualized Return']*100:.2f}%)")
    # H2
    h2_status = "Supported" if metrics_B_full['Annualized Volatility'] > metrics_A_full['Annualized Volatility'] else "Not Supported"
    print(f"H2: CFDs increase volatility. Finding: {h2_status}. Detail: Annualized Volatility (B: {metrics_B_full['Annualized Volatility']*100:.2f}% vs A: {metrics_A_full['Annualized Volatility']*100:.2f}%)")
    # H3
    h3_status = "Supported" if metrics_B_full['Sharpe Ratio'] > metrics_A_full['Sharpe Ratio'] else "Not Supported"
    print(f"H3: CFDs improve risk-adjusted returns (Sharpe Ratio). Finding: {h3_status}. Detail: Sharpe Ratio (B: {metrics_B_full['Sharpe Ratio']:.2f} vs A: {metrics_A_full['Sharpe Ratio']:.2f})")
    # H4
    mdd_improved = metrics_B_full['Max Drawdown'] > metrics_A_full['Max Drawdown'] # MDD is negative
    vol_improved = metrics_B_full['Annualized Volatility'] < metrics_A_full['Annualized Volatility']
    if mdd_improved and vol_improved: h4_status = "Supported"
    elif mdd_improved or vol_improved: h4_status = "Partially Supported"
    else: h4_status = "Not Supported"
    h4_detail = (f"Max Drawdown (B: {metrics_B_full['Max Drawdown']*100:.2f}%, A: {metrics_A_full['Max Drawdown']*100:.2f}%) - {'Improved' if mdd_improved else 'Not Improved'}; "
                   f"Volatility (B: {metrics_B_full['Annualized Volatility']*100:.2f}%, A: {metrics_A_full['Annualized Volatility']*100:.2f}%) - {'Improved' if vol_improved else 'Not Improved'}")
    print(f"H4: CFDs enhance risk reduction (lower MDD & Volatility). Finding: {h4_status}. Detail: {h4_detail}")

    # --- H5: COVID Acute Crisis Analysis ---
    print("\n--- H5: COVID Acute Crisis Analysis ---")
    df_sim_covid_acute = df_sim_full[
        (df_sim_full['date'] >= pd.to_datetime(cfg.COVID_CRISIS_START_DATE)) &
        (df_sim_full['date'] <= pd.to_datetime(cfg.COVID_CRISIS_END_DATE))
    ].copy().reset_index(drop=True)

    if not df_sim_covid_acute.empty:
        values_A_covid_acute = simulation_engine.simulate_portfolio_A(df_sim_covid_acute, cfg.INITIAL_CAPITAL, cfg.EQUITY_ALLOC_A)
        values_B_covid_acute = simulation_engine.simulate_portfolio_B_momentum(df_sim_covid_acute, cfg.INITIAL_CAPITAL, cfg)
        
        returns_A_covid_acute = values_A_covid_acute.pct_change().fillna(0)
        returns_B_covid_acute = values_B_covid_acute.pct_change().fillna(0)

        metrics_A_covid_acute = risk_metrics.calculate_metrics_summary("A (COVID Acute)", values_A_covid_acute, returns_A_covid_acute, RFR_ANNUAL, cfg.INITIAL_CAPITAL, cfg.TRADING_DAYS_PER_YEAR)
        metrics_B_covid_acute = risk_metrics.calculate_metrics_summary("B (COVID Acute)", values_B_covid_acute, returns_B_covid_acute, RFR_ANNUAL, cfg.INITIAL_CAPITAL, cfg.TRADING_DAYS_PER_YEAR)

        if metrics_A_covid_acute.get('Total Return') is not None and metrics_B_covid_acute.get('Total Return') is not None:
            h5_status = "Supported (Reacted More Strongly)" if abs(metrics_B_covid_acute['Total Return']) > abs(metrics_A_covid_acute['Total Return']) else "Not Supported (Reacted Less Strongly or Similarly)"
            h5_detail = f"COVID Total Return (B: {metrics_B_covid_acute['Total Return']*100:.2f}%, A: {metrics_A_covid_acute['Total Return']*100:.2f}%)"
            print(f"H5 (COVID Only): CFD portfolios react more strongly (magnitude) during the COVID crisis. Finding: {h5_status}. Detail: {h5_detail}")
        else:
            print("H5 (COVID Only): Could not calculate metrics for COVID acute period.")
    else:
        print("H5 (COVID Only): No data for COVID acute period.")


    # --- H6: COVID Trough to Recovery Analysis ---
    print("\n--- H6: COVID Trough to Recovery Analysis ---")
    df_h6_period_values = pd.DataFrame({
        'date': df_sim_full['date'], 
        'A_Value': values_A_full, 
        'B_Value': values_B_momentum_full
        })

    # Filter for the period covering the acute crisis (to find trough) and recovery assessment
    df_crisis_recovery_data = df_h6_period_values[
        (df_h6_period_values['date'] >= pd.to_datetime(cfg.COVID_ANALYSIS_START_DATE)) &
        (df_h6_period_values['date'] <= pd.to_datetime(cfg.COVID_ANALYSIS_END_DATE))
    ].copy()

    if not df_crisis_recovery_data.empty:
        # Identify trough within the acute crisis phase (e.g., Feb-Apr 2020)
        acute_crisis_window = df_crisis_recovery_data[
            (df_crisis_recovery_data['date'] >= pd.to_datetime(cfg.COVID_CRISIS_START_DATE)) &
            (df_crisis_recovery_data['date'] <= pd.to_datetime(cfg.COVID_CRISIS_END_DATE))
        ]
        if not acute_crisis_window.empty:
            trough_A_idx = acute_crisis_window['A_Value'].idxmin()
            trough_B_idx = acute_crisis_window['B_Value'].idxmin()
            
            trough_A_value = acute_crisis_window.loc[trough_A_idx, 'A_Value']
            trough_A_date = acute_crisis_window.loc[trough_A_idx, 'date']
            trough_B_value = acute_crisis_window.loc[trough_B_idx, 'B_Value']
            trough_B_date = acute_crisis_window.loc[trough_B_idx, 'date']

            # Value at the end of the recovery assessment period
            end_recovery_data_A = df_crisis_recovery_data[df_crisis_recovery_data['date'] == pd.to_datetime(cfg.COVID_ANALYSIS_END_DATE)]
            end_recovery_data_B = df_crisis_recovery_data[df_crisis_recovery_data['date'] == pd.to_datetime(cfg.COVID_ANALYSIS_END_DATE)]

            if not end_recovery_data_A.empty and not end_recovery_data_B.empty:
                end_value_A = end_recovery_data_A['A_Value'].iloc[0]
                end_value_B = end_recovery_data_B['B_Value'].iloc[0]

                recovery_A_return = (end_value_A / trough_A_value) - 1 if trough_A_value > 0 else np.nan
                recovery_B_return = (end_value_B / trough_B_value) - 1 if trough_B_value > 0 else np.nan
                
                if pd.notna(recovery_A_return) and pd.notna(recovery_B_return):
                    h6_status = "Supported" if recovery_B_return > recovery_A_return else "Not Supported"
                    h6_detail = f"Recovery from Trough (B: {recovery_B_return*100:.2f}% vs A: {recovery_A_return*100:.2f}% by {cfg.COVID_ANALYSIS_END_DATE})"
                    print(f"H6: Model B exhibited a stronger recovery than Model A post-COVID trough. Finding: {h6_status}. Detail: {h6_detail}")
                    
                    # Plot for H6
                    plot_df_h6 = df_crisis_recovery_data.melt(id_vars=['date', 'A_Value', 'B_Value'], value_vars=[], var_name="TempPortfolio", value_name="TempValue") # Base for melt
                    plot_df_h6_A = df_crisis_recovery_data[['date', 'A_Value']].rename(columns={'A_Value':'Value'})
                    plot_df_h6_A['Portfolio'] = cfg.PORTFOLIO_A_LABEL
                    plot_df_h6_B = df_crisis_recovery_data[['date', 'B_Value']].rename(columns={'B_Value':'Value'})
                    plot_df_h6_B['Portfolio'] = portfolio_B_label_full
                    plot_df_h6_final = pd.concat([plot_df_h6_A, plot_df_h6_B])

                    plotting.plot_covid_recovery(plot_df_h6_final, 
                                                 trough_A_date, trough_A_value, 
                                                 trough_B_date, trough_B_value,
                                                 cfg.PORTFOLIO_A_LABEL, portfolio_B_label_full,
                                                 cfg.COLOR_A, cfg.COLOR_B,
                                                 title=f"COVID Crisis & Recovery Performance ({cfg.COVID_ANALYSIS_START_DATE} to {cfg.COVID_ANALYSIS_END_DATE})")
                else:
                    print("H6: Could not calculate recovery returns for H6.")
            else:
                print(f"H6: No data at recovery end date {cfg.COVID_ANALYSIS_END_DATE}.")
        else:
            print(f"H6: No data in acute COVID window ({cfg.COVID_CRISIS_START_DATE} to {cfg.COVID_CRISIS_END_DATE}) to find trough.")
    else:
        print(f"H6: No data for specified COVID analysis period ({cfg.COVID_ANALYSIS_START_DATE} to {cfg.COVID_ANALYSIS_END_DATE}).")


    print("\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()