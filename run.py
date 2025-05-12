#sb # run.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np # Import numpy for type checking in results display
import json
import time
import os
import sys
from dotenv import load_dotenv

# --- Environment Setup ---
# Load environment variables from .env file if it exists.
# This allows storing the API key locally in a .env file (ignored by git).
# If the key is provided directly in the environment (e.g., via export),
# os.environ.get will pick that up later.

load_dotenv()
print("Attempted to load .env file (if present).")

# --- Project Imports ---
# Ensure the 'scripts' directory is accessible
# This might be needed if running 'python run.py' from the project root
scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

try:
    from config_loader import load_config
    from data_loader import load_and_prepare_data
    from simulation_engine import simulate_classic_portfolio, simulate_hedged_portfolio
    from analysis import run_analysis
    from plotting import (
        plot_portfolio_comparison,
        plot_vix,
        plot_costs,
        plot_contracts_margin,
        save_plot
    )
    # from utils import setup_logging # Optional logging
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Ensure you are running this script from the project root directory"
          " or that the 'scripts' directory is in your PYTHONPATH.")
    sys.exit(1)

# --- Main Execution Function ---
def main():
    # setup_logging() # Optional
    start_time = time.time()
    print("\n--- Starting CFD Hedging Analysis ---")

    # 1. Load Configuration
    # ---------------------
    print("\n[Step 1/6] Loading Configuration...")
    try:
        # Pass the path relative to run.py location
        config_path = os.path.join(os.path.dirname(__file__), 'config/params.yaml')
        config = load_config(config_path)
        # Store config path for potential use in other modules (like finding .env)
        config['_config_path_'] = config_path
    except Exception as e:
        print(f"FATAL: Could not load configuration. {e}")
        return # Exit if config fails

    # 2. Load Data
    # -------------
    # API key check happens INSIDE load_and_prepare_data if fetching is needed
    print("\n[Step 2/6] Loading and Preparing Data...")
    try:
        df_data = load_and_prepare_data(config) # API key check logic is within this function
        if df_data is None or df_data.empty:
             raise ValueError("Data loading returned empty DataFrame.")
    except (ValueError, FileNotFoundError) as e:
         # Catch specific errors related to data/key issues from data_loader
         print(f"FATAL: Could not load or prepare data. Error: {e}")
         print("Check 'data_file' path in config/params.yaml.")
         if "API key" in str(e):
              api_key_var = config.get('api_key_env_var', 'FMP_API_KEY')
              print(f"Ensure the environment variable '{api_key_var}' is set OR "
                    f"the key is in a '.env' file in the project root.")
         return # Exit if data fails
    except Exception as e:
         # Catch any other unexpected errors during data loading
         import traceback
         print(f"FATAL: An unexpected error occurred during data loading.")
         traceback.print_exc()
         return


    # 3. Run Simulations
    # ------------------
    print("\n[Step 3/6] Running Simulations...")
    try:
        portfolio_a = simulate_classic_portfolio(df_data, config)
        portfolio_b, cost_df = simulate_hedged_portfolio(df_data, config)
        if portfolio_a.empty or portfolio_b.empty:
            # Check if source data was empty after prep
            if df_data.empty:
                 print("Warning: Source data was empty, simulation resulted in empty portfolios.")
            else:
                 raise ValueError("One or both simulations produced empty results despite having input data.")
    except Exception as e:
        print(f"FATAL: Simulation failed. {e}")
        import traceback
        traceback.print_exc()
        return # Exit if simulation fails

    # 4. Perform Analysis
    # -------------------
    print("\n[Step 4/6] Performing Analysis...")
    analysis_results = None # Initialize
    try:
        if not portfolio_a.empty and not portfolio_b.empty:
             analysis_results = run_analysis(portfolio_a, portfolio_b, df_data, config)
             if analysis_results is None: raise ValueError("Analysis function returned None.")
        else:
             print("Skipping analysis because portfolio simulation results are empty.")
    except Exception as e:
        print(f"ERROR: Analysis failed. {e}")
        # Allow continuing to show simulation results if they exist
        analysis_results = None


    # 5. Display Results
    # ------------------
    print("\n[Step 5/6] Displaying Analysis Results...")
    # Set display format for pandas
    pd.set_option('display.float_format', '{:,.4f}'.format)
    pd.set_option('display.width', 120) # Adjust width for better console display

    if analysis_results:
        print("\nMetrics: Full Period")
        # Use .fillna('N/A') or similar if metrics can be NaN
        print(analysis_results['full_period'].fillna('N/A').to_string())

        if 'crisis' in analysis_results and analysis_results['crisis']:
            for name, df_crisis in analysis_results['crisis'].items():
                print(f"\nMetrics: Crisis Period '{name}'")
                print(df_crisis.fillna('N/A').to_string())
        else:
             print("\nNo crisis period metrics calculated.")


        print("\nHypothesis Testing Summary:")
        hypotheses = analysis_results.get('hypotheses', {})
        if hypotheses:
            for key, value in hypotheses.items():
                if isinstance(value, dict): # Nested crisis details
                    print(f"  {key}:")
                    for k, v in value.items():
                         # Format floats, leave strings as is, handle NaN
                         display_v = f"{v:.4f}" if isinstance(v, (float, np.floating)) and pd.notna(v) else ('N/A' if pd.isna(v) else v)
                         print(f"    - {k}: {display_v}")
                else:
                     display_v = value if pd.notna(value) else 'N/A'
                     print(f"  - {key}: {display_v}")
        else:
             print("No hypothesis results available.")

    else:
        print("Analysis results are not available (Analysis may have failed or simulations were empty).")

    # 6. Generate and Show/Save Plots
    # -------------------------------
    print("\n[Step 6/6] Generating Plots...")
    try:
        # Only generate plots if simulation data exists
        if not portfolio_a.empty and not portfolio_b.empty:
            fig_compare = plot_portfolio_comparison(portfolio_a, portfolio_b, config)
            save_plot(fig_compare, "portfolio_comparison.png", config)

            fig_vix = plot_vix(df_data, config)
            save_plot(fig_vix, "vix_threshold.png", config)

            # Cost and contract plots only relevant if Model B ran
            if not cost_df.empty:
                fig_costs = plot_costs(cost_df)
                save_plot(fig_costs, "cumulative_costs.png", config)

                fig_contracts = plot_contracts_margin(cost_df)
                save_plot(fig_contracts, "contracts_margin.png", config)
            else:
                print("Skipping cost/contract plots as cost_df is empty.")

            # Show plots interactively if not saving
            if not config.get('save_plots', False):
                print("Displaying plots...")
                plt.show() # Shows all generated figures
            else:
                print("Plots saved (if enabled in config). Closing figures.")
                plt.close('all') # Close figures if saving to prevent memory issues
        else:
            print("Skipping plot generation as simulation results are empty.")

    except Exception as e:
        print(f"ERROR: Plot generation failed. {e}")
        import traceback
        traceback.print_exc()


    end_time = time.time()
    print(f"\n--- Analysis Finished in {end_time - start_time:.2f} seconds ---")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()
