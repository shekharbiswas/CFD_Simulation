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


<img width="1024" alt="image" src="https://github.com/user-attachments/assets/26dba559-076d-42ff-adf4-970de254c520" />



## VIX Momentum Hedging Strategy: Rationale and Feature Engineering

The core of Model B's dynamic component revolves around a VIX-based momentum hedging strategy. This strategy was conceptualized based on observations of the typical inverse relationship between the S&P 500 index and the VIX (CBOE Volatility Index), particularly during periods of market stress.

**Rationale from Market Behavior (as seen in the "S&P 500 Index and VIX Over Time" chart):**

The provided chart visually illustrates a common market phenomenon:
*   **Inverse Correlation:** Generally, when the S&P 500 index (blue line) experiences sharp declines, the VIX index (red line) tends to spike significantly. This is because the VIX measures expected market volatility, and fear or uncertainty often leads to higher anticipated volatility and falling equity prices. The COVID-19 crash in early 2020 is a stark example of this.
*   **Momentum in VIX Spikes:** VIX spikes are not always instantaneous single-day events. Often, a period of rising fear can lead to sustained increases in the VIX over several days. This "momentum" in the VIX's upward trajectory can signal a potentially deepening market downturn.
*   **VIX Mean Reversion (to some extent):** While VIX can stay elevated during prolonged uncertainty, extremely high VIX levels are typically not sustained indefinitely. After a volatility spike, the VIX often trends downwards as market conditions stabilize. This suggests that shorting the market (or an S&P 500 proxy) when VIX shows strong upward momentum, and covering that short when VIX momentum reverses or VIX falls to lower levels, could be a viable hedging approach.

Based on these observations, a momentum strategy was designed to identify periods of rapidly increasing VIX, interpret them as signals of heightened market risk and potential equity drawdowns, and consequently initiate a hedge (e.g., by shorting S&P 500 CFDs). Conversely, signals of VIX stabilization or decline are used to remove the hedge.

**Engineered Features and Their Meanings:**

To implement this VIX momentum strategy, several new features were engineered and calculated from the raw VIX data. These features serve as the building blocks for generating trading signals:

1.  **`VIX_Lagged_5D`**:
    *   **Calculation:** The VIX value from 5 trading days prior (`df_sim['VIX'].shift(MOMENTUM_LOOKBACK_PERIOD)` where `MOMENTUM_LOOKBACK_PERIOD = 5`).
    *   **Meaning:** This provides a historical reference point to measure recent VIX movement.

2.  **`VIX_Pct_Change_5D`**:
    *   **Calculation:** `(df_sim['VIX'] - df_sim['VIX_Lagged_5D']) / df_sim['VIX_Lagged_5D']`.
    *   **Meaning:** This feature quantifies the percentage change in the VIX over the last 5 trading days. It's the primary indicator of VIX momentum. A large positive value indicates a rapid increase in VIX, while a large negative value indicates a rapid decrease.

3.  **`Is_VIX_Momentum_Up_Condition_Met`**:
    *   **Calculation:** A boolean flag (`True`/`False`) set to `True` if `VIX_Pct_Change_5D` is greater than `VIX_PCT_CHANGE_THRESHOLD_UP` (which is +35%).
    *   **Meaning:** Identifies individual days where the VIX has shown significant upward momentum (a greater than 35% increase over 5 days).

4.  **`Is_VIX_Momentum_Down_Condition_Met`**:
    *   **Calculation:** A boolean flag set to `True` if `VIX_Pct_Change_5D` is less than `VIX_PCT_CHANGE_THRESHOLD_DOWN` (which is -20%).
    *   **Meaning:** Identifies individual days where the VIX has shown significant downward momentum (a greater than 20% decrease over 5 days). This is a component of the "cover short" signal.

5.  **`Consecutive_VIX_Momentum_Up_Days`**:
    *   **Calculation:** Counts the number of consecutive trading days where `Is_VIX_Momentum_Up_Condition_Met` has been `True`.
    *   **Meaning:** This feature measures the persistence of strong upward VIX momentum. A short signal is generated only after a sustained period of such momentum.

6.  **`Consecutive_VIX_Momentum_Down_Days`**:
    *   **Calculation:** Counts the number of consecutive trading days where `Is_VIX_Momentum_Down_Condition_Met` has been `True`.
    *   **Meaning:** Measures the persistence of strong downward VIX momentum, which can contribute to a signal to cover (close) any existing short hedge positions.

7.  **`Short_Signal_Today`**:
    *   **Calculation:** A boolean flag set to `True` if `Consecutive_VIX_Momentum_Up_Days` is greater than or equal to `N_CONSECUTIVE_UP_DAYS_TO_SHORT` (which is 3 days).
    *   **Meaning:** This is the final signal to initiate a short hedge. It requires not just a single day of high VIX momentum, but at least 3 consecutive days of such momentum, indicating a more robust trend.

8.  **`Cover_Signal_Momentum_Today`**:
    *   **Calculation:** A boolean flag set to `True` if `Consecutive_VIX_Momentum_Down_Days` is greater than or equal to `N_CONSECUTIVE_DOWN_DAYS_TO_COVER` (which is 1 day).
    *   **Meaning:** This is one of the conditions to cover an existing short hedge. It triggers if the VIX shows at least one day of significant downward momentum, suggesting that the period of heightened fear might be subsiding.

9.  **`Cover_Signal_Absolute_VIX_Today`**:
    *   **Calculation:** A boolean flag set to `True` if the current `VIX` level is below `VIX_ABSOLUTE_COVER_THRESHOLD` (which is 20.0).
    *   **Meaning:** This provides an alternative condition to cover the short hedge. Regardless of recent momentum, if the VIX level itself drops below a certain "calm" threshold (e.g., 20), it's considered a signal that the heightened risk period has passed, and the hedge can be removed.

By combining these engineered features, the strategy aims to dynamically adjust the portfolio's market exposure, hedging against potential downturns signaled by rising VIX momentum and removing those hedges when volatility subsides.
