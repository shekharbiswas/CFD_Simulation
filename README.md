# CFD Hedging Strategy

This project investigates how Contracts for Difference (CFDs) can be strategically integrated into modern investment portfolios to manage return, risk, and crisis resilience.

CFDs are derivative instruments that allow investors to speculate on asset price movements without actually owning the underlying security. This characteristic grants them flexibility but also introduces significant risks, primarily through leverage.

Traditional investing often focuses on long-term growth, diversification, and capital preservation through asset allocation. However, traditional portfolios can be slow to adapt and may suffer substantial losses during periods of heightened market volatility or sudden downturns.

CFDs, when employed strategically and with rigorous risk management, offer potential tools to address these challenges. They provide mechanisms for both long and short market exposure, can be implemented relatively quickly, and allow investors to potentially hedge existing positions without liquidating underlying assets.

This project specifically aims to evaluate a *defensive* use case for CFDs. It compares a classic S&P 500 stock/cash portfolio against a similar portfolio that incorporates short S&P 500 CFD positions as a hedge, automatically triggered by elevated market volatility (measured by the VIX index).

Simulations are conducted using historical market data covering the period from 2019 through mid-2025, encompassing diverse market conditions, including the significant volatility spike during the COVID-19 crash of 2020 and a simulated high-volatility period in 2025 based on the provided data. This allows for an assessment of the strategy's performance in both volatile and more stable environments.

We utilize historical price data (S&P 500, VIX) and interest rate data (SOFR) to analyze key financial metrics, including:

*   Total Return & Annualized Volatility
*   Sharpe Ratio (risk-adjusted return)
*   Maximum Drawdown (peak-to-trough decline)
*   Value at Risk (VaR) and Expected Shortfall (ES) (tail risk measures)

A crucial aspect of the analysis is the incorporation of realistic CFD trading costs, modeled based on provider information (IG Markets, 2024), covering overnight financing charges, borrowing costs for short positions, average spreads, and margin requirements.

By combining financial theory with quantitative simulation, this project tests specific hypotheses about how this VIX-triggered CFD hedging strategy influences portfolio behavior, particularly its effectiveness in mitigating risk during market stress versus its potential drag on returns during normal conditions.

## 📘 What Are CFDs? (In this Project Context)

A Contract for Difference (CFD) is a derivative contract where two parties agree to exchange the difference in the value of an underlying asset between the time the contract is opened and when it is closed. For this project, we focus on:

*   **No Ownership:** Trading the S&P 500 index via CFDs without owning the underlying stocks.
*   **Hedging Tool:** Primarily using **short** S&P 500 CFDs to offset potential losses in a long S&P 500 equity position during high volatility.
*   **Costs:** Acknowledging and modeling associated costs like financing, borrowing, spreads, and margin.
*   **Leverage Implication:** While CFDs inherently offer leverage, this project uses them defensively, meaning the leverage primarily impacts the *cost basis* (financing/borrowing) and *margin requirements* rather than amplifying upside returns. The risk profile is modified by the hedge, not necessarily amplified in the traditional leveraged sense.

## 📌 Objectives

The core objectives of this project are to:

1.  **Compare Performance:** Simulate and contrast the performance of two distinct portfolio models:
    *   **Model A (Classic):** A traditional portfolio holding 80% in S&P 500 equities and 20% in cash.
    *   **Model B (CFD-Hedged):** A portfolio holding 80% S&P 500 equities, 20% initial cash, but which activates **short S&P 500 CFD positions** to hedge a portion (e.g., 50%) of the equity exposure when the VIX index exceeds a predefined threshold (e.g., VIX > 25).
      
2.  **Evaluate Risk & Diversification Impact:** Quantify how the CFD hedging strategy affects portfolio risk using standard metrics:
    *   Volatility (Standard Deviation)
    *   Value at Risk (VaR - 95th percentile potential loss)
    *   Expected Shortfall (ES - average loss beyond VaR)
    *   Sharpe Ratio (comparing return against risk)
    *   Maximum Drawdown (largest peak-to-valley loss)
      
3.  **Incorporate Realistic Costs:** Model the financial impact of using CFDs by including:
    *   Overnight financing charges/credits based on the SOFR benchmark rate plus/minus a broker fee.
    *   Specific borrowing costs associated with maintaining short CFD positions.
    *   Average spread costs incurred when closing CFD hedge positions.
    *   Tiered margin requirements based on position size, affecting available cash.
      
4.  **Simulate Crisis Behavior:** Analyze portfolio performance during specific historical and simulated high-stress periods:
    *   The COVID-19 market crash (approx. Feb-Apr 2020).
    *   A period of high VIX readings in the provided 2025 data (approx. Mar-May 2025).
      
5.  **Test VIX Trigger:** Utilize the VIX index as the explicit mechanism to activate and deactivate the short CFD hedges.
   
6.  **Test Hypotheses:** Evaluate predefined hypotheses regarding the expected effects of this CFD hedging strategy on:
    *   Average portfolio return.
    *   Overall portfolio risk (volatility).
    *   Risk-adjusted return (Sharpe Ratio).
    *   Diversification / Risk Reduction effectiveness.
    *   Portfolio behavior during crisis periods.

<br>

## 📊 Key Metrics Used

*   **Total Return:** The overall percentage gain or loss over the entire simulation period.
*   **Annualized Return:** The geometric average annual rate of return.
*   **Annualized Volatility (σ):** The standard deviation of daily returns, scaled to an annual figure, measuring price fluctuation risk.
*   **Sharpe Ratio:** Measures risk-adjusted return by calculating excess return (over a risk-free rate, proxied by average SOFR) per unit of volatility.
*   **Value at Risk (VaR):** Estimates the maximum potential loss over a specific time horizon at a given confidence level (e.g., 95% VaR indicates the loss expected to be exceeded only 5% of the time). Calculated historically.
*   **Expected Shortfall (ES):** Also known as Conditional VaR (CVaR), measures the expected loss *given* that the loss exceeds the VaR threshold. Provides insight into the severity of tail-risk events. Calculated historically.
*   **Maximum Drawdown (MDD):** The largest percentage decline from a portfolio's peak value to a subsequent trough, indicating the worst-case loss experienced.

<br>

## 📈 Data Used

| Data Component          | Source/Ticker/Label             | Used For                                                     | Notes                                                                |
| :---------------------- | :------------------------------ | :----------------------------------------------------------- | :------------------------------------------------------------------- |
| S&P 500 Index Prices    | `^GSPC` (API) / `S&P500` (CSV)  | Portfolio equity component return, volatility, drawdown        | Fetched via FMP API or loaded from CSV.                                |
| VIX Index Levels        | `^VIX` (API) / `VIX` (CSV)      | Hedging trigger logic (signal to open/close short CFDs)      | Fetched via FMP API or loaded from CSV.                                |
| SOFR Rate (USD O/N)     | `SOFR` (CSV column)             | Benchmark rate for calculating CFD overnight financing costs | **Crucially loaded from the provided CSV file.** Not fetched from API. |
| CFD Cost Parameters     | Static values in `params.yaml`  | Cost modeling (spread, financing fee, borrow rate)           | Based on IG Markets (2024) assumptions from source material.         |
| CFD Margin Requirements | Tiered rates in `params.yaml` | Calculating margin cash needed, impacting available cash    | Based on IG Markets (2024) tiered structure.                       |

<br>

## ⚙️ Technology Stack

*   **Language:** Python (version 3.8+ recommended)
*   **Core Libraries:**
    *   `pandas`: Data manipulation and analysis.
    *   `numpy`: Numerical operations.
    *   `matplotlib`: Plotting and visualization.
    *   `PyYAML`: Loading configuration from YAML files.
    *   `requests`: Fetching data from web APIs (if enabled).
    *   `python-dotenv`: Loading environment variables from `.env` files (for API keys).
    *   `streamlit`: Creating the interactive web application.
*   **Optional Libraries (for `notebooks/` or extended analysis):** `scipy`, `statsmodels`, `arch`, `scikit-learn`.

<br>

## 📁 Project Structure

The project follows a modular structure for better organization and maintainability:

<pre>
cfd_simulation/
├── data/ # Input data files
│ └── vix_sp500_data.csv
├── config/ # Configuration files
│ └── params.yaml
├── scripts/ # Python source code modules
│ ├── init.py # Makes 'scripts' a package
│ ├── config_loader.py # Loads YAML configuration
│ ├── data_loader.py # Loads/Fetches and prepares data
│ ├── cfd_cost_model.py # Calculates CFD costs (margin, financing, etc.)
│ ├── risk_metrics.py # Calculates portfolio risk/performance metrics
│ ├── hedging_strategy.py # Defines the VIX-based hedging logic
│ ├── simulation_engine.py # Runs the day-by-day portfolio simulation loop
│ ├── analysis.py # Performs comparative analysis on simulation results
│ ├── plotting.py # Generates plots using Matplotlib
│ └── utils.py # Utility functions (optional, e.g., logging)
├── notebooks/ # Jupyter notebooks for exploration (optional)
│ └── exploratory_analysis.ipynb
├── app.py # Streamlit web application (imports from scripts)
├── run.py # Main script for command-line execution
├── requirements.txt # Python dependencies
└── README.md # This file

</pre>

<br>

## 📜 Script Breakdown and Logic

| Script Name             | Purpose                                                                                                | Key Logic / Functionality                                                                                                                            |
| :---------------------- | :----------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config_loader.py`      | Loads simulation parameters.                                                                           | Reads `config/params.yaml` into a Python dictionary.                                                                                                 |
| `data_loader.py`        | Loads/fetches and preprocesses data.                                                                   | Handles loading `vix_sp500_data.csv` OR fetching S&P500/VIX from FMP API (using secure API key), merges with SOFR from CSV, calculates returns, cleans data. |
| `cfd_cost_model.py`     | Calculates CFD-specific costs.                                                                         | Functions for tiered margin (`calculate_margin`), daily financing (`calculate_daily_financing_cost`), borrowing (`calculate_daily_borrowing_cost`), spread. |
| `risk_metrics.py`       | Computes portfolio metrics.                                                                            | Functions for `calculate_metrics` (Return, Volatility, Sharpe, MDD, VaR, ES).                                                                       |
| `hedging_strategy.py`   | Implements the hedging decision logic.                                                                 | Function `get_hedge_action` determines target short CFD contracts based on VIX level, current portfolio state, and config thresholds/ratios.           |
| `simulation_engine.py`  | Runs the core day-by-day simulation.                                                                   | Contains `simulate_classic_portfolio` (Model A) and `simulate_hedged_portfolio` (Model B) which iterate daily, update values, apply costs, and implement hedging. |
| `analysis.py`           | Performs comparative analysis.                                                                         | Function `run_analysis` takes simulation results, calculates metrics for full/crisis periods, and evaluates the predefined hypotheses.                 |
| `plotting.py`           | Generates visualizations.                                                                              | Functions to create Matplotlib charts (portfolio comparison, VIX, costs, contracts/margin). Includes logic to save plots based on config.          |
| `utils.py`              | Optional helper functions.                                                                             | Can include logging setup or other reusable utilities.                                                                                             |
| `run.py`                | Command-line execution entry point.                                                                    | Orchestrates the workflow: load config -> load data -> run simulations -> run analysis -> display results -> generate plots.                           |
| `app.py`                | Interactive web application entry point.                                                               | Uses Streamlit to provide UI controls (sliders, inputs), runs simulations/analysis on demand, and displays results/plots interactively.             |
| `params.yaml`           | Central configuration file.                                                                            | Defines all adjustable parameters: file paths, tickers, thresholds, costs, allocations, API settings, etc.                                          |
<br>

## 💼 Relevance for Portfolio Managers & Investors

Understanding the practical implications of using CFDs defensively can be valuable:

*   **Hedging Tool:** Provides a way to potentially reduce downside risk during volatility spikes without selling core equity holdings.
*   **Tactical Flexibility:** CFDs allow for relatively quick implementation of short positions compared to other methods.
*   **Cost-Benefit Analysis:** Quantifies the direct costs (financing, borrowing, spread) associated with this hedging strategy versus the potential benefit of reduced drawdowns.
*   **Risk Awareness:** Highlights that even defensive strategies have trade-offs (lower overall returns) and are not foolproof (performance varies depending on crisis characteristics).

<br>

## 🧪 Methodology

1.  **Data Acquisition:** Historical daily data for S&P 500, VIX (fetched or loaded), and SOFR (loaded) from 2019 to mid-2025 is prepared.
2.  **Configuration:** Simulation parameters (capital, allocation, VIX threshold, hedge ratio, costs) are defined in `config/params.yaml`.
3.  **Model Simulation:**
    *   **Model A:** The 80/20 S&P 500/Cash portfolio value is calculated daily based on S&P 500 returns.
    *   **Model B:**
        *   Equity portion value changes based on S&P 500 returns.
        *   Each day, the VIX level is checked against the threshold (`config['hedging_strategy']['vix_threshold']`).
        *   If VIX > threshold, the `hedging_strategy.py` calculates the target number of short S&P 500 CFD contracts based on the `hedge_ratio` and current equity value.
        *   The simulation adjusts the number of contracts held, calculates required margin using `cfd_cost_model.py`, and updates cash available.
        *   If already hedged, daily P&L from the short CFD position, overnight financing costs/credits, and borrowing costs are calculated and applied to the cash balance.
        *   Spread costs are applied when CFD positions are closed.
        *   Total portfolio value (Equity + Free Cash + Margin Held) is tracked daily.
4.  **Analysis:**
    *   Performance and risk metrics (`risk_metrics.py`) are calculated for both portfolios over the full period and defined crisis periods.
    *   Results are compared, and the hypotheses (`analysis.py`) are evaluated based on the calculated metrics.
5.  **Visualization:** Key results are plotted using `plotting.py` (portfolio growth, VIX trigger, costs, contracts/margin).

<br>

## 📈 Hypotheses Evaluated

The simulation results are used to assess the following hypotheses:

| Category         | Hypothesis                                                        | Expected Outcome based on Simulation | Finding (Example based on previous run) |
| :--------------- | :---------------------------------------------------------------- | :----------------------------------- | :-------------------------------------- |
| Performance      | **H1:** CFDs lead to higher average returns                       | Unlikely due to costs/drag           | Check results                        |
| Risk             | **H2:** CFDs increase volatility                                  | Unlikely (used defensively)          | Check results                            |
| Sharpe Ratio     | **H3:** CFDs improve risk-adjusted returns                        | Possible if risk reduction is large  | Check results                  |
| Diversification  | **H4:** CFDs enhance risk reduction despite inherent leverage | Expected (Lower MDD/Vol)             | Check results                              |
| Crisis Response  | **H5:** CFD portfolios react more strongly (magnitude) to crises | Mixed (Depends on crisis)            | Check results      |

<br>

## 📉 CFD Cost Assumptions (Modeled)

Based on IG Markets (2024) information from source documents:

| Cost Component        | Treatment in Simulation                                                               | Notes                                                     |
| :-------------------- | :------------------------------------------------------------------------------------ | :-------------------------------------------------------- |
| Spread                | ✅ Applied average point cost (`avg_spread_points`) when closing short hedge positions. | Represents round-trip cost. Time-of-day variation excluded. |
| Financing (O/N)       | ✅ Calculated daily for short positions: `SOFR - broker_annual_financing_fee`.        | Can be a cost or credit. Based on `days_in_year_financing`. |
| Borrowing (Short CFD) | ✅ Calculated daily for short positions: `borrowing_cost_annual`.                       | Added cost specific to shorts.                            |
| Margin                | ✅ Calculated daily using tiered rates; cash is allocated, reducing free cash.          | Affects available cash but not directly P&L.              |
| Commissions           | ❌ Excluded (Source indicated spread used instead for index CFDs).                    | Assume index CFD, not share CFD.                          |
| Slippage              | ❌ Excluded (Difficult to model historically).                                          | Limitation of the simulation.                             |
| Currency Conversion   | ❌ Excluded (Assumes USD base for portfolio and index).                               | Limitation.                                               |

<br>

## 🗂 Setup and Usage

### Setup

1.  **Clone Repository:**
    ```
    # (No bash commands here, assuming user clones manually)
    # Navigate to the project directory: cfd_simulation/
    ```
2.  **Create Environment (Recommended):**
    ```
    # (Instructions for virtual environment creation omitted as requested)
    # Activate the environment if created.
    ```
3.  **Install Dependencies:**
    ```
    # Ensure pip is available
    # Run from the project root directory:
    pip install -r requirements.txt
    ```
4.  **Data File:** Place your `vix_sp500_data.csv` file inside the `data/` directory. It **must** contain columns for date, S&P 500 price, VIX level, and the SOFR rate.
5.  **API Key (Optional, for Fetching):**
    *   Create a `.env` file in the project root (`cfd_simulation/.env`).
    *   Add your FMP API key to the `.env` file: `FMP_API_KEY="your_actual_key_here"`
    *   **Ensure `.env` is listed in your `.gitignore` file.**
    *   Alternatively, set the `FMP_API_KEY` environment variable in your system or terminal session before running.
6.  **Configuration:** Review and modify parameters in `config/params.yaml`. Pay attention to `load_from_api` if you want to fetch data.

### Usage

#### Command-Line Execution

*   Navigate to the project root directory (`cfd_simulation/`) in your terminal.
*   To run the analysis using the settings in `params.yaml`:
    ```
    python run.py
    ```
*   If you want to fetch data using the API key stored in your environment or `.env` file, ensure `load_from_api: true` is set in `config/params.yaml` before running the command above. The script will handle finding the key.

#### Interactive Web Application (Streamlit)

*   Navigate to the project root directory (`cfd_simulation/`) in your terminal.
*   Launch the Streamlit app:
    ```
    streamlit run app.py
    ```
*   The application will open in your web browser.
*   Use the sidebar to adjust key parameters (Initial Capital, VIX Threshold, Hedge Ratio).
*   Click "Run Analysis" to execute the simulations and view results interactively. The app uses the API key setup (env var or `.env`) if data fetching is triggered (which usually happens on the first run or if data loading fails).

## 👤 Who Should Use This Project?

*   **Finance Students & Educators:** As a practical example of derivatives application, risk management, and quantitative simulation.
*   **Portfolio and Fund Managers:** To explore potential defensive strategies and understand the cost/benefit of VIX-based hedging.
*   **Retail Investors:** To gain insight into the mechanics and risks of CFDs used for hedging (educational purposes, **not** investment advice).
*   **Risk Management Analysts:** To model and quantify the impact of specific hedging instruments and triggers.
*   **Researchers:** Studying market behavior, volatility dynamics, and crisis performance.

## 🌐 Why This Project Matters

While CFDs carry significant risks, especially when used speculatively with high leverage, understanding their potential defensive applications is valuable in modern finance. This project aims to provide a quantitative perspective on:

*   **Crisis Navigation:** Can VIX-triggered CFD hedges offer meaningful protection during market downturns?
*   **Dynamic Hedging:** Evaluating the feasibility and outcome of an automated, volatility-based hedging rule.
*   **Cost vs. Benefit:** Quantifying the performance drag from costs against the value of reduced drawdown.
*   **Strategy Limitations:** Demonstrating that effectiveness can vary significantly depending on market conditions (e.g., COVID vs. 2025 scenario).

By simulating this specific strategy with realistic costs, the project offers insights into the practical trade-offs involved in incorporating such tools into portfolio management.

[CFD_app](https://github.com/shekharbiswas/CFD_app)
