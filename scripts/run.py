import matplotlib.pyplot as plt
import pandas as pd
import json
import time

# Import project modules using relative paths or assuming PYTHONPATH is set
from scripts.config_loader import load_config
from scripts.data_loader import load_and_prepare_data
from scripts.simulation_engine import simulate_classic_portfolio, simulate_hedged_portfolio
from scripts.analysis import run_analysis
from scripts.plotting import (
    plot_portfolio_comparison,
    plot_vix,
    plot_costs,
    plot_contracts_margin,
    save_plot
)
# from scripts.utils import setup_logging # Optional logging

def main():
    # setup_logging() # Optional
    start_time = time.time()
    print("--- Starting CFD Hedging Analysis ---")

    # 1. Load Configuration
    try:
        config = load_config() # Assumes params.yaml is in config/ directory
    except Exception as e:
        print(f"FATAL: Could not load configuration. {e}")
        return # Exit if config fails

    # 2. Load Data
    try:
        df_data = load_and_prepare_data(config)
        if df_data is None or df_data.empty: raise ValueError("Data loading returned empty DataFrame.")
    except Exception as e:
        print(f"FATAL: Could not load or prepare data. {e}")
        return # Exit if data fails

    # 3. Run Simulations
    print("\n--- Running Simulations ---")
    try:
        portfolio_a = simulate_classic_portfolio(df_data, config)
        portfolio_b, cost_df = simulate_hedged_portfolio(df_data, config)
        if portfolio_a.empty or portfolio_b.empty:
            raise ValueError("One or both simulations produced empty results.")
    except Exception as e:
        print(f"FATAL: Simulation failed. {e}")
        return # Exit if simulation fails

    # 4. Perform Analysis
    print("\n--- Performing Analysis ---")
    try:
        analysis_results = run_analysis(portfolio_a, portfolio_b, df_data, config)
        if analysis_results is None: raise ValueError("Analysis failed to produce results.")
    except Exception as e:
        print(f"ERROR: Analysis failed. {e}")
        # Allow continuing to show simulation results maybe?
        analysis_results = None


    # 5. Display Results
    print("\n--- Analysis Results ---")
    pd.set_option('display.float_format', '{:,.4f}'.format) # Format output

    if analysis_results:
        print("\nMetrics: Full Period")
        print(analysis_results['full_period'].to_string())

        if 'crisis' in analysis_results:
            for name, df_crisis in analysis_results['crisis'].items():
                print(f"\nMetrics: Crisis Period '{name}'")
                print(df_crisis.to_string())

        print("\nHypothesis Testing Summary:")
        # Print hypothesis results neatly
        hypotheses = analysis_results.get('hypotheses', {})
        for key, value in hypotheses.items():
            if isinstance(value, dict): # Nested crisis details
                print(f"  {key}:")
                for k, v in value.items():
                     print(f"    {k}: {v:.4f}" if isinstance(v, float) else f"    {k}: {v}")
            else:
                 print(f"  {key}: {value}")

    else:
        print("Analysis results are not available.")

    # 6. Generate and Show/Save Plots
    print("\n--- Generating Plots ---")
    try:
        fig_compare = plot_portfolio_comparison(portfolio_a, portfolio_b, config)
        save_plot(fig_compare, "portfolio_comparison.png", config)

        fig_vix = plot_vix(df_data, config)
        save_plot(fig_vix, "vix_threshold.png", config)

        fig_costs = plot_costs(cost_df)
        save_plot(fig_costs, "cumulative_costs.png", config)

        fig_contracts = plot_contracts_margin(cost_df)
        save_plot(fig_contracts, "contracts_margin.png", config)

        # Show plots if not saving or if explicitly desired
        if not config.get('save_plots', False):
            plt.show() # Shows all generated figures
        else:
            plt.close('all') # Close figures if saving to prevent display

    except Exception as e:
        print(f"ERROR: Plot generation failed. {e}")


    end_time = time.time()
    print(f"\n--- Analysis Finished in {end_time - start_time:.2f} seconds ---")

if __name__ == "__main__":
    main()
