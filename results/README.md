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
      
*   **VIX-Based Hedging Triggers:** These parameters define when the dynamic hedging component of Model B is activated or deactivated based on recent VIX momentum, not fixed thresholds.
    *   `VIX_PCT_CHANGE_THRESHOLD_UP = 0.35`: The VIX must rise by more than **35% over the past 5 days** to be considered a valid fear signal.
    *   `N_CONSECUTIVE_UP_DAYS_TO_SHORT = 3`: If the above condition holds for **3 consecutive days**, a short hedge is activated.
    *   `MODEL_B_FIXED_HEDGE_RATIO_MOMENTUM = 0.70`: When active, the hedge covers **70% of the equity position** using CFDs.
    *   `VIX_PCT_CHANGE_THRESHOLD_DOWN = -0.20`: If the VIX drops by **20% or more in a single day**, it may trigger a hedge removal.
    *   `N_CONSECUTIVE_DOWN_DAYS_TO_COVER = 1`: A single qualifying drop is enough to start covering the hedge.
    *   `VIX_ABSOLUTE_COVER_THRESHOLD = 20.0`: If VIX falls below **20**, the hedge is also removed — regardless of momentum.


         *   **Construction logic of the strategy:**
         
         The percentage change in the VIX compared to its value five trading days prior (VIX_Pct_Change_5D) is analyzed daily.
         
         Trigger conditions for initiating the hedge:
         - The 5-day VIX percentage change (VIX_Pct_Change_5D) must be greater than +35%.
         - This specific condition (5-day VIX % change > +35%) must persist for 3 consecutive trading days.
         - If both of these criteria are met, a short hedge position covering 70% of the portfolio's equity value is opened using CFDs.
         
           
         Exit signals for the hedge (deactivating the short position):
         
         The hedge is closed if either of the following conditions is met:
         -The 5-day VIX percentage change (VIX_Pct_Change_5D) is less than -20% (i.e., the VIX has dropped by more than 20% compared to 5 days ago) for at least 1 trading day.
         OR
         - The current daily VIX level falls below an absolute threshold value of 20.0.


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


<img width="1024" alt="image" src="https://github.com/user-attachments/assets/9e9beb9b-8c6d-4f85-8153-d00c077e7890" />


## Full Period Performance Analysis: Model A (Classic) vs. Model B (VIX Momentum Hedge)

This section analyzes the overall performance of the two simulated portfolios – Model A (a classic, static 80/20 equity/cash allocation) and Model B (an 80/20 base allocation with a dynamic VIX momentum-based CFD hedge at a 0.70 hedge ratio) – over the entire simulation period from early 2019 to mid-2025. The evaluation considers both the quantitative metrics presented in the table and the visual representation of portfolio growth in the "Simplified Portfolio Performance" chart.

**Key Performance Metrics Overview:**

| Metric                  | A (Classic) | B (Momentum HR:0.70) | Interpretation of B vs. A                                   |
| :---------------------- | :---------- | :--------------------- | :-------------------------------------------------------- |
| **Total Return**        | 1.0097      | 1.1834                 | **Higher:** Model B achieved a significantly greater total growth. |
| **Annualized Return**   | 0.1158      | 0.1304                 | **Higher:** Model B delivered a better annualized return.        |
| **Annualized Volatility**| 0.1648      | 0.1892                 | **Higher:** Model B exhibited more price fluctuation.        |
| **Sharpe Ratio**        | 0.5504      | 0.5566                 | **Slightly Higher:** Model B offered marginally better risk-adjusted returns per unit of total volatility. |
| **Max Drawdown**        | -0.2784     | -0.2821                | **Slightly Worse:** Model B experienced a slightly deeper maximum loss. |
| **Calmar Ratio**        | 0.4160      | 0.4624                 | **Higher:** Model B showed better returns relative to its max drawdown. |
| **Sortino Ratio**       | 0.7706      | 0.8642                 | **Higher:** Model B provided better returns per unit of downside risk. |
| Daily VaR 95%           | -0.0147     | -0.0149                | Similar: Potential worst-day loss at 95% confidence is comparable. |
| Daily CVaR 95%          | -0.0249     | -0.0261                | Similar: Expected loss on worst 5% of days is comparable, slightly higher for B. |
| Omega Ratio             | 1.1222      | 1.1390                 | Slightly Higher: Model B had a marginally better probability-weighted gain/loss ratio. |
| Skewness                | -0.3409     | 3.4874                 | **Significantly Different:** Model B shows strong positive skewness (more frequent small losses, few large gains), while A is slightly negatively skewed. |
| Kurtosis                | 13.9773     | 77.2671                | **Significantly Higher (Fat Tails):** Model B has much higher kurtosis, indicating more extreme outcomes (both positive and negative) compared to a normal distribution. |
| Best Day                | 0.0761      | 0.2186                 | **Much Higher:** Model B had a significantly better best single-day performance. |
| Worst Day               | -0.0959     | -0.0959                | **Identical:** Both models shared the same worst single-day loss. |
| Win Rate %              | 54.8287     | 54.6417                | Similar: Proportion of winning days is nearly identical.    |
| Average Win %           | 0.6621      | 0.6941                 | Slightly Higher: Model B's average gain on winning days was slightly better. |
| Average Loss %          | -0.6954     | -0.7136                | Slightly Worse: Model B's average loss on losing days was slightly larger. |
| Profit Factor           | 1.1557      | 1.1718                 | Slightly Higher: Model B's gross profits were slightly higher relative to gross losses. |
| **Recovery Factor**     | 3.6268      | 4.1952                 | **Higher:** Model B demonstrated a better ability to recover from its maximum drawdown relative to its total profit. |

**Visual Performance (from the Chart):**

The "Simplified Portfolio Performance" chart visually corroborates many of the metric findings:

*   **Overall Growth:** The red line (Model B) consistently tracks above the blue line (Model A) for the majority of the period, especially after the initial COVID-19 recovery, indicating superior overall wealth generation.
*   **COVID-19 Crisis (Early 2020):** Both portfolios experience a sharp dip. Model B appears to dip slightly more or similarly to Model A initially but then recovers much more rapidly and strongly, diverging significantly upwards. This suggests the VIX momentum hedge, while perhaps not preventing the initial shock perfectly, may have allowed for a more aggressive or better-timed re-entry or benefited from the subsequent market rebound when the hedge was lifted.
*   **Volatility:** The red line (Model B) shows more pronounced peaks and troughs (greater oscillation) compared to the smoother blue line (Model A), visually confirming its higher annualized volatility.
*   **Periods of Underperformance/Choppiness for Model B:** There are periods (e.g., parts of 2022-2023) where Model B's growth flattens or even slightly underperforms Model A before resuming its outperformance. This could be due to the costs of hedging (CFD fees, spread costs) or "whipsaw" effects if the VIX signals trigger hedges that don't align with subsequent market moves.
*   **Recent Performance (2024-2025):** Model B continues to maintain its lead over Model A, though both show an upward trend.

**Interpretation and Key Insights:**

1.  **Higher Returns at the Cost of Higher Volatility:** Model B (VIX Momentum Hedge) achieved higher Total and Annualized Returns compared to the classic Model A. However, this came with increased Annualized Volatility. The hedging strategy, while aiming to protect during downturns, also introduces its own dynamics that can increase short-term price swings.

2.  **Risk-Adjusted Performance:**
    *   The Sharpe Ratio is marginally better for Model B, suggesting that the increased return slightly compensated for the increased total volatility.
    *   Crucially, the Sortino Ratio and Calmar Ratio are notably better for Model B. This indicates that Model B was more efficient in generating returns relative to its downside risk (Sortino) and its maximum drawdown (Calmar). This is a key strength, suggesting the hedge was effective in managing specific types of risk, even if overall volatility increased.

3.  **Drawdown Management:** While Model B's Max Drawdown was slightly worse than Model A's, its significantly higher Calmar Ratio and Recovery Factor suggest that it recovered more effectively from this drawdown. The chart strongly supports the idea of a quicker, more robust recovery post-COVID for Model B.

4.  **Distributional Characteristics (Skewness and Kurtosis):**
    *   The dramatically positive skewness (3.4874) for Model B is very interesting. It implies that while Model B might have frequent small losses (or smaller gains), it also experienced some significantly large positive returns (as seen in "Best Day" performance: 21.86% for B vs 7.61% for A). This pattern is often desirable if the large positive outliers significantly contribute to overall returns.
    *   The very high kurtosis (77.26) for Model B indicates "fat tails" – a higher probability of extreme outcomes (both good and bad) compared to a normal distribution. This aligns with the higher "Best Day" return but also the slightly higher CVaR.

5.  **Effectiveness of the VIX Momentum Hedge:**
    *   The strategy appears to have been particularly beneficial during and after the COVID-19 crisis, as evidenced by the chart's visual recovery and the better Calmar/Recovery Factors.
    *   The costs associated with CFD hedging (broker fees, spreads) and the potential for the hedge to be active during market upswings (if VIX remained elevated) likely contributed to the increased volatility and periods of choppiness for Model B.

**Outcome:**

Over the full simulation period, Model B, with its VIX momentum-based CFD hedging strategy, generally outperformed the classic Model A in terms of overall and annualized returns. While it exhibited higher total volatility, its risk-adjusted metrics (particularly Sortino and Calmar Ratios) were superior, suggesting effective management of downside risk and a better recovery profile. The positive skewness and high "Best Day" return indicate that the strategy, when conditions were favorable (perhaps during high volatility exits or hedge removals), captured significant upside. The primary trade-off was the increased day-to-day price fluctuation and a marginally worse maximum drawdown, though its recovery from that drawdown was stronger. The performance during the COVID-19 period, as seen in the chart, highlights a key strength of Model B's dynamic approach.



## Hypotheses Evaluation Summary

This table summarizes the findings for the pre-defined hypotheses comparing Model A (Classic 80/20) and Model B (80/20 with VIX Momentum CFD Hedge).

| Hypothesis Statement                                                                 | Finding                               | Supporting Detail / Metric Comparison                                     | Brief Explanation/Implication                                                                                                                               |
| :----------------------------------------------------------------------------------- | :------------------------------------ | :------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **H1:** CFDs lead to higher average returns.                                         | **Supported**                         | Annualized Return (B: 13.04% vs A: 11.58%)                                | Model B, incorporating the CFD-based VIX momentum strategy, generated higher annualized returns over the full period compared to the static Model A.             |
| **H2:** CFDs increase volatility.                                                    | **Supported**                         | Annualized Volatility (B: 18.92% vs A: 16.48%)                            | The dynamic nature of Model B's CFD hedging and its market timing attempts resulted in greater overall price fluctuations (volatility) than Model A.           |
| **H3:** CFDs improve risk-adjusted returns (Sharpe Ratio).                           | **Supported**                         | Sharpe Ratio (B: 0.56 vs A: 0.55)                                         | Model B offered slightly better returns per unit of total risk (as measured by standard deviation), indicating a marginal improvement in risk-adjusted efficiency. |
| **H4:** CFDs enhance risk reduction (lower MDD & Volatility).                        | **Not Supported**                     | MDD (B: -28.21% vs A: -27.84%) - Not Improved; Vol (B: 18.92% vs A: 16.48%) - Not Improved | Model B did not achieve a lower maximum drawdown nor lower overall volatility. Its max loss was slightly deeper, and its volatility was higher than Model A's. |
| **H5 (COVID Only):** CFD portfolios react more strongly (magnitude) during COVID.    | **Not Supported (Reacted Less Strongly)** | COVID Total Return (B: -10.00% vs A: -15.00%)                             | During the acute COVID crisis period analyzed, Model B experienced a smaller decline (less negative total return) than Model A, indicating a less severe reaction in terms of magnitude of loss. |
| **H6:** Model B exhibited a stronger recovery than Model A post-COVID trough.      | **Supported**                         | Recovery from Trough (B: 74.91% vs A: 43.53% by 2020-08-31)                 | Following its lowest point during the COVID crisis, Model B recovered significantly more strongly and rapidly than Model A by the assessment date of Aug 31, 2020. |

**Overall Implications:**

The VIX momentum strategy (Model B) successfully generated higher overall returns (H1) and showed a superior ability to recover from significant market stress like the COVID-19 trough (H6). While it did lead to increased overall volatility (H2) and didn't reduce the absolute maximum drawdown or overall volatility compared to the simpler Model A (H4), its risk-adjusted returns (Sharpe Ratio, H3) were marginally better. A key observation from H5 is that during the specific COVID downturn, Model B actually lost less than Model A, suggesting the hedge provided some downside mitigation during that particular crisis event, even if its overall volatility was higher. The strategy appears to trade off smoother returns for higher growth potential and better crisis recovery, with the CFD component playing a crucial role in its dynamic behavior.
