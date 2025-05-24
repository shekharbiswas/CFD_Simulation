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
