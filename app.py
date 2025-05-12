import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np # Make sure numpy is imported

# Set path temporarily if needed (better to install as package or manage PYTHONPATH)
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))

# Import project modules
from scripts.config_loader import load_config
from scripts.data_loader import load_and_prepare_data
from scripts.simulation_engine import simulate_classic_portfolio, simulate_hedged_portfolio
from scripts.analysis import run_analysis
from scripts.plotting import (
    plot_portfolio_comparison,
    plot_vix,
    plot_costs,
    plot_contracts_margin
)

# --- Page Config ---
st.set_page_config(layout="wide", page_title="CFD Hedging Analysis")
st.title("S&P 500 CFD Hedging Strategy Analysis")

# --- Load Base Config ---
@st.cache_resource # Cache the config dictionary itself
def get_base_config():
    try:
        return load_config()
    except Exception as e:
        st.error(f"Failed to load base configuration: {e}")
        return None

config = get_base_config()

# --- Load Data ---
# Cache data loading based on the file path in config
@st.cache_data
def load_data_cached(data_file_path):
    # Create a temporary config subset just for loading
    temp_config = {'data_file': data_file_path, **config} # Add other needed keys if modified loader uses them
    try:
        df = load_and_prepare_data(temp_config)
        return df
    except Exception as e:
        st.error(f"Failed to load or prepare data from {data_file_path}: {e}")
        return None

if config:
    df_data = load_data_cached(config['data_file'])
else:
    df_data = None

# --- Sidebar for Inputs ---
st.sidebar.header("Simulation Parameters")

# Use sliders/number inputs for adjustable parameters
if config:
    # Use values from config as defaults
    capital = st.sidebar.number_input("Initial Capital (USD)", min_value=10000, value=int(config.get('initial_capital', 1_000_000)), step=10000, format="%d")
    vix_thresh = st.sidebar.slider("VIX Hedging Threshold", min_value=15.0, max_value=45.0, value=float(config.get('hedging_strategy', {}).get('vix_threshold', 25.0)), step=0.5)
    hedge_ratio = st.sidebar.slider("Hedge Ratio", min_value=0.0, max_value=1.0, value=float(config.get('hedging_strategy', {}).get('hedge_ratio', 0.5)), step=0.05, format="%.2f")
else:
    # Fallback default values if config fails
    capital = st.sidebar.number_input("Initial Capital (USD)", min_value=10000, value=1_000_000, step=10000, format="%d")
    vix_thresh = st.sidebar.slider("VIX Hedging Threshold", min_value=15.0, max_value=45.0, value=25.0, step=0.5)
    hedge_ratio = st.sidebar.slider("Hedge Ratio", min_value=0.0, max_value=1.0, value=0.50, step=0.05, format="%.2f")


# --- Simulation and Analysis Function (Cached) ---
# Cache results based on the input parameters
@st.cache_data # Using data cache as simulation depends on data and params
def run_full_analysis(_df_data, _config, initial_capital, vix_threshold, hedge_ratio):
    """Runs simulation and analysis, designed for caching."""
    if _df_data is None or _config is None:
        return None, None, None # Return None if data or config is missing

    # Create a temporary config reflecting sidebar inputs for the simulation
    sim_config = _config.copy()
    sim_config['initial_capital'] = initial_capital
    sim_config['hedging_strategy']['vix_threshold'] = vix_threshold
    sim_config['hedging_strategy']['hedge_ratio'] = hedge_ratio

    print(f"Running analysis with VIX Threshold: {vix_threshold}, Hedge Ratio: {hedge_ratio}") # Debug print

    # Run Simulations
    portfolio_a = simulate_classic_portfolio(_df_data, sim_config)
    portfolio_b, cost_df = simulate_hedged_portfolio(_df_data, sim_config)

    if portfolio_a.empty or portfolio_b.empty:
        st.warning("Simulation produced empty results.")
        return None, None, None

    # Perform Analysis
    analysis_results = run_analysis(portfolio_a, portfolio_b, _df_data, sim_config)

    return analysis_results, portfolio_a, portfolio_b, cost_df

# --- Main Display Area ---
if df_data is None or config is None:
    st.warning("Data or Configuration failed to load. Cannot run analysis.")
else:
    st.sidebar.success(f"{len(df_data)} data rows loaded.")
    if st.sidebar.button("Run Analysis"):
        start_run_time = time.time()
        analysis_results, portfolio_a, portfolio_b, cost_df = run_full_analysis(df_data, config, capital, vix_thresh, hedge_ratio)
        end_run_time = time.time()
        st.sidebar.info(f"Analysis ran in {end_run_time - start_run_time:.2f} sec.")

        if analysis_results and not portfolio_a.empty and not portfolio_b.empty:
            st.header("Analysis Results")

            # --- Display Metrics ---
            st.subheader("Performance & Risk Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Full Period**")
                st.dataframe(analysis_results['full_period'].applymap('{:,.4f}'.format))
            with col2:
                if 'covid_19' in analysis_results['crisis']:
                    st.markdown("**COVID-19 Crisis**")
                    st.dataframe(analysis_results['crisis']['covid_19'].applymap('{:,.4f}'.format))
                else: st.markdown("**COVID-19 Crisis:** *No data*")
            with col3:
                 if 'hypothetical_2025' in analysis_results['crisis']:
                    st.markdown("**Hypothetical 2025 Crisis**")
                    st.dataframe(analysis_results['crisis']['hypothetical_2025'].applymap('{:,.4f}'.format))
                 else: st.markdown("**Hypothetical 2025 Crisis:** *No data*")

            # --- Display Hypotheses ---
            st.subheader("Hypothesis Testing Summary")
            hypotheses = analysis_results.get('hypotheses', {})
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                st.markdown(f"- **H1 (Higher Return B):** {hypotheses.get('H1_Higher_Return_B','N/A')}")
                st.markdown(f"- **H2 (Higher Vol B):** {hypotheses.get('H2_Higher_Vol_B','N/A')}")
                st.markdown(f"- **H3 (Higher Sharpe B):** {hypotheses.get('H3_Higher_Sharpe_B','N/A')}")
                st.markdown(f"- **H4 (Lower Risk B):** {hypotheses.get('H4_Lower_Risk_B','N/A')}")
            with h_col2:
                if 'H5_Crisis_Behavior' in hypotheses:
                    st.markdown("- **H5 (Crisis Behavior Details):**")
                    for k, v in hypotheses['H5_Crisis_Behavior'].items():
                         # Format floats, leave strings as is
                         display_v = f"{v:.4f}" if isinstance(v, (float, np.floating)) else v
                         st.markdown(f"  - `{k}`: {display_v}")
                else:
                     st.markdown("- **H5 (Crisis Behavior):** *N/A*")


            # --- Display Plots ---
            st.subheader("Visualizations")

            st.markdown("#### Portfolio Growth Comparison")
            fig_compare = plot_portfolio_comparison(portfolio_a, portfolio_b, config)
            st.pyplot(fig_compare)
            plt.close(fig_compare) # Close figure

            st.markdown("#### VIX Index and Hedging Trigger")
            fig_vix = plot_vix(df_data, config)
            st.pyplot(fig_vix)
            plt.close(fig_vix)

            st.markdown("#### Model B: Cumulative Costs and Contracts/Margin")
            plot_col1, plot_col2 = st.columns(2)
            with plot_col1:
                fig_costs = plot_costs(cost_df)
                st.pyplot(fig_costs)
                plt.close(fig_costs)
            with plot_col2:
                fig_contracts = plot_contracts_margin(cost_df)
                st.pyplot(fig_contracts)
                plt.close(fig_contracts)

        elif not analysis_results and (portfolio_a is None or portfolio_b is None):
             st.error("Simulation failed to run with the selected parameters.")
        else: # Analysis failed but simulation might have run
             st.warning("Analysis failed, but simulation data might be available. Check logs.")
             # Optionally display basic portfolio plots if they exist

    else:
        st.info("Adjust parameters in the sidebar and click 'Run Analysis' to generate results.")
