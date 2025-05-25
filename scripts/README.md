# CFD - Simulation Steps and Strategies

## Overview

This project simulates and compares different investment portfolio strategies, with a focus on incorporating Contracts for Difference (CFDs) for hedging and tactical positioning.
It is structured logically around clear hypotheses and financial metrics, offering insights into how CFDs can enhance or impact portfolio performance and risk.

The simulations are built on a solid framework (TCCM: Theory, Context, Characteristics, Methods) and focus on both static comparisons and dynamic strategies, particularly a VIX momentum-based CFD hedging approach for Model B.

## Project Structure

The project is organized into several Python scripts:

*   **`config.py`**: Contains all configuration parameters, API keys, file paths, and simulation settings. **Modify this file first to set up your environment.**
*   **`data_loader.py`**: Handles fetching and preparing market data (S&P 500, VIX, SOFR).
*   **`signal_generation.py`**: Implements the logic for generating trading signals, specifically the VIX momentum signals for Model B.
*   **`simulation_engine.py`**: Contains the core functions for simulating portfolio performance for Model A (classic) and Model B (dynamic CFD hedge).
*   **`risk_metrics.py`**: Provides a comprehensive function to calculate various financial and risk metrics for portfolio evaluation.
*   **`plotting.py`**: Includes functions to generate plots for market data, portfolio performance, and specific crisis period analyses.
*   **`main_analysis.py`**: The main script that orchestrates the entire analysis workflow: data loading, signal generation, simulation, metrics calculation, hypothesis testing, and plotting.

## Prerequisites

Before running the simulation, ensure you have Python installed (preferably Python 3.8+) and the following libraries:

*   pandas
*   numpy
*   requests
*   plotly

You can install them using pip:

```bash
pip install pandas numpy requests plotly
```

## Setup and Configuration

1.  **API Key**:
    *   This project uses Financial Modeling Prep (FMP) to fetch historical market data. You will need an FMP API key.
    *   Open `config.py`.
    *   Replace the placeholder value for `FMP_API_KEY` with your actual FMP API key:
        ```python
        FMP_API_KEY = "YOUR_ACTUAL_FMP_API_KEY"
        ```

2.  **SOFR Data**:
    *   The simulation requires SOFR (Secured Overnight Financing Rate) data.
    *   Ensure you have a CSV file named `SOFR.csv` in the root directory of the project.
    *   The CSV file should have at least two columns:
        *   `observation_date` (e.g., `YYYY-MM-DD`)
        *   `SOFR` (the rate as a percentage, e.g., `5.31` for 5.31%).
    *   If your file is named differently or located elsewhere, update `SOFR_CSV_FILEPATH` in `config.py`.
    *   If your SOFR rate column name in the CSV is different from 'SOFR', update `TARGET_SOFR_COL_NAME` in `config.py`. This should be the name of the column in your CSV that holds the rate value *before* it's processed by the script (the script will then internally use 'SOFR_Rate' after converting it to a decimal).

3.  **Review Other Parameters (Optional)**:
    *   Open `config.py` to review and adjust other parameters if needed, such as:
        *   `START_DATE`, `END_DATE` for the simulation period.
        *   `INITIAL_CAPITAL`.
        *   Portfolio allocation percentages (`EQUITY_ALLOC_A`, `EQUITY_ALLOC_B`).
        *   VIX momentum signal parameters.
        *   CFD cost parameters.
        *   Crisis period dates for specific hypothesis testing.

## Running the Simulation

Once the prerequisites and setup are complete, you can run the main analysis script from your terminal:

1.  Navigate to the root directory of the project in your terminal.
2.  Execute the `main_analysis.py` script:
    ```bash
    python main_analysis.py
    ```

## Expected Output

The script will:

1.  Print status messages to the console indicating the progress of data loading, signal generation, and simulations.
2.  Display plots in your default web browser (or inline if your IDE supports it, like VS Code with the Python extension):
    *   S&P 500 Index and VIX levels over time.
    *   Full period portfolio performance comparison (Model A vs. Model B).
    *   COVID crisis and recovery performance plot, highlighting troughs (if applicable data exists).
3.  Print a summary table of full-period financial metrics for both portfolios to the console.
4.  Print the findings for each of the defined hypotheses (H1 to H6) to the console.

## Troubleshooting

*   **`FileNotFoundError: [Errno 2] No such file or directory: 'SOFR.csv'`**: Ensure `SOFR.csv` is in the correct location (project root by default) or that `SOFR_CSV_FILEPATH` in `config.py` points to the correct path.
*   **API Key Errors / HTTP Errors from FMP**:
    *   Double-check your `FMP_API_KEY` in `config.py` is correct and active.
    *   Ensure you have a stable internet connection.
    *   FMP has usage limits on free tiers; you might encounter issues if you exceed them frequently.
*   **Plotly plots not showing**:
    *   If running as a script from a standard terminal, plots should open in a web browser. Ensure your browser is not blocking pop-ups for `localhost` or `127.0.0.1`.
    *   In some Integrated Development Environments (IDEs) or virtual environments, you might need to configure Plotly's default renderer if inline plotting is desired and not working automatically. However, `fig.show()` is generally robust.
*   **`KeyError` or `AttributeError`**: This usually indicates missing columns in the input data or misnamed parameters in `config.py` or within the scripts. Check the console output for specific error messages which often point to the problematic key or attribute. Review `config.py` and the data loading steps in `data_loader.py`.
*   **Performance**: Fetching large amounts of historical data via API can take time, especially on the first run. Subsequent runs might be faster if data is cached by your operating system or if you implement local data caching within the scripts (not included by default in this version).
*   **`NameError` for a config variable**: Ensure all configuration variables used in `main_analysis.py` and other modules are correctly defined in `config.py` and that `config` is imported correctly (e.g., `import config as cfg`).