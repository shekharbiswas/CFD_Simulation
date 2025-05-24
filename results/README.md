## Data Collection

The financial data utilized in this analysis is aggregated from three distinct sources, covering key market indices and interest rates:

1.  **Secured Overnight Financing Rate (SOFR):**
    *   **Primary Source:** Federal Reserve Economic Data (FRED), maintained by the Federal Reserve Bank of St. Louis.
    *   **Access Method:** Data is initially downloaded from the official FRED series page for SOFR: [https://fred.stlouisfed.org/series/SOFR](https://fred.stlouisfed.org/series/SOFR).
    *   **Local Storage:** For this analysis, the downloaded SOFR data is stored and accessed locally via a CSV file named `SOFR.csv`, located within the `CFD_Simulation/` project directory.
    *   **Processing:** The script reads this CSV, handles potential missing value indicators (e.g., '.', empty strings), converts date columns to datetime objects, transforms the rate from percentage to decimal, and forward-fills missing values to ensure daily continuity.

2.  **S&P 500 Index (`^GSPC`):**
    *   **Primary Source:** Financial Modeling Prep (FMP) API.
    *   **Access Method:** Historical daily closing prices are fetched programmatically using the FMP API endpoint for historical price data, queried with the S&P 500 ticker symbol `^GSPC`.
    *   **Timeframe:** Data is requested for the period from January 1, 2019, to May 21, 2025.

3.  **CBOE Volatility Index (VIX - `^VIX`):**
    *   **Primary Source:** Financial Modeling Prep (FMP) API.
    *   **Access Method:** Similar to the S&P 500, historical daily closing prices for the VIX are retrieved via the FMP API, using the ticker symbol `^VIX`.
    *   **Timeframe:** The VIX data is also fetched for the period spanning January 1, 2019, to May 21, 2025.

**Data Integration and Derived Metrics:**

*   The individual datasets (S&P 500, VIX, and the processed SOFR) are merged based on their common 'date' field using an inner join. This ensures that the final analytical dataset only contains dates for which all three data points are available.
*   Following the merge, key analytical metrics such as daily percentage returns for the S&P 500 and VIX, as well as lagged index values (e.g., `Prev_S&P500`), are calculated from this combined dataset.


## Configuration & Simulation Parameters

This section outlines the core parameters and settings that govern the behavior of the portfolio simulations and data processing steps. These configurations allow for consistent and replicable analysis of different investment strategies.

**Global Simulation Settings:**

*   `INITIAL_CAPITAL = 1,000,000`: Defines the starting capital amount (e.g., $1 million) for both Model A and Model B portfolios. This ensures a common baseline for performance comparison.
*   `pd.set_option('display.float_format', lambda x: '%.4f' % x)`: A Pandas display setting to format floating-point numbers to four decimal places when DataFrames are printed, enhancing readability of financial figures.

**Model A (Classic Portfolio) Parameters:**

This model represents a traditional, static asset allocation strategy.

*   `EQUITY_ALLOC_A = 0.80`: Specifies that 80% of Model A's portfolio is allocated to equities (presumably tracking the S&P 500).
*   `CASH_ALLOC_A = 0.20`: The remaining 20% of Model A's portfolio is held in cash or a cash equivalent.

**Model B (Dynamic/CFD Hedging Portfolio) Parameters:**

This model incorporates a dynamic hedging strategy potentially using Contracts for Difference (CFDs) based on VIX levels.

*   **Base Allocation:**
    *   `EQUITY_ALLOC_B = 0.80`: Similar to Model A, the base allocation for Model B is 80% in equities.
    *   `CASH_ALLOC_B = 0.20`: The base cash allocation for Model B is 20%.
*   **VIX-Based Hedging Triggers:** These parameters define when the dynamic hedging component of Model B is activated or deactivated.
    *   `MODEL_B_VIX_ACTIVATE_THRESH = 30.0`: The hedging strategy is triggered (e.g., short CFD positions are opened) if the VIX index rises above this threshold of 30.0.
    *   `MODEL_B_VIX_DEACTIVATE_THRESH = 10.0`: The hedge is removed (e.g., CFD positions are closed) if the VIX falls below this threshold of 10.0. It's crucial that this is lower than the activation threshold to prevent rapid cycling.
    *   `MODEL_B_FIXED_HEDGE_RATIO = 0.90`: When the hedge is active, this ratio (90%) determines the notional value of the hedge relative to the portfolio's equity value.
*   **CFD Cost Assumptions (for Model B):** These parameters model the realistic costs associated with using CFDs for hedging.
    *   `BROKER_FEE_ANNUALIZED = 0.025`: An annualized financing cost of 2.5% charged by the broker on the notional value of open CFD positions (often related to the underlying interest rate plus a broker spread).
    *   `SPREAD_COST_PERCENT = 0.0002`: A one-time transaction cost, representing 0.02% of the notional value, incurred when a CFD position is closed. This models the bid-ask spread.
    *   `CFD_INITIAL_MARGIN_PERCENT = 0.05`: The initial margin requirement, set at 5% of the CFD's notional value, which must be available in cash to open a CFD position.

**Crisis Period Definitions:**

These date ranges are used to analyze portfolio performance during specific market stress events.

*   `COVID_START_DATE = "2020-02-01"`: Marks the beginning of the COVID-19 market crisis analysis period.
*   `COVID_END_DATE = "2020-04-30"`: Marks the end of the acute phase of the COVID-19 market crisis analysis period.
*   `CRISIS_2025_START_DATE = "2025-03-01"`: Defines the start of a hypothetical future crisis period for analysis.
*   `CRISIS_2025_END_DATE`: This is set dynamically after data loading to be the last date available in the simulation dataset, ensuring the analysis covers the full extent of available data if it falls within the 2025 crisis window defined by the start date.

**Data Processing and Derived Parameters (Post-Configuration):**

The following steps and derived parameters are set up after the initial configuration, based on the loaded data:

*   **Data Loading and Cleaning:** The script copies `df_final` to `df_full_data` and performs essential data type conversions (date to datetime, relevant columns to numeric) and handles missing values by dropping rows with NaNs in critical columns to create `df_sim`.
*   **Dynamic `CRISIS_2025_END_DATE`:** As mentioned, this is determined from the maximum date in the prepared `df_sim`.
*   **Risk-Free Rate (`RFR_ANNUAL`):** Calculated as the average of the daily `SOFR_Rate` from the `df_sim` dataset, providing an annualized risk-free rate benchmark for performance metrics like the Sharpe ratio.
*   **Simulation Period Confirmation:** The script prints the start and end dates of the simulation period covered by `df_sim` and the total number of simulation days.
