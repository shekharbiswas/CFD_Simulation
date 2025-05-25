# CFD Hedging Strategy & VIX Momentum Simulation

## Overview

This project investigates how Contracts for Difference (CFDs) can be strategically integrated into investment portfolios. It specifically simulates and compares two main portfolio models:

*   **Model A (Classic):** A traditional portfolio with a static allocation to S&P 500 equities and cash.
*   **Model B (Dynamic CFD Hedge):** A portfolio with a similar base allocation to Model A, but which dynamically activates **short S&P 500 CFD positions** as a hedge. This hedging is triggered by a **VIX momentum strategy**, where signals to short or cover are generated based on recent VIX percentage changes and absolute VIX levels.

The project aims to evaluate the impact of this dynamic CFD hedging strategy on portfolio return, risk, and resilience during various market conditions, including historical events like the COVID-19 crash and simulated future crisis scenarios.

Simulations are conducted using historical market data for S&P 500, VIX, and SOFR (Secured Overnight Financing Rate) from 2019 through mid-2025. The analysis incorporates realistic CFD trading costs, including financing, spreads, and margin requirements.

## 📘 What Are CFDs? (In this Project Context)

A Contract for Difference (CFD) is a derivative contract where two parties agree to exchange the difference in the value of an underlying asset between the time the contract is opened and when it is closed. For this project, we focus on:

*   **No Ownership:** Trading the S&P 500 index via CFDs without owning the underlying stocks.
*   **Hedging Tool:** Primarily using **short** S&P 500 CFDs to offset potential losses in a long S&P 500 equity position during periods of high or increasing market volatility.
*   **VIX Momentum Trigger:** The decision to hedge (short CFDs) or cover (close short CFDs) is based on a defined VIX momentum strategy, considering:
    *   Significant percentage increases in VIX over a lookback period to initiate shorts.
    *   Significant percentage decreases in VIX or absolute VIX levels falling below a threshold to cover shorts.
*   **Costs:** Acknowledging and modeling associated costs like financing charges/credits, spreads on closing positions, and initial margin requirements.
*   **Leverage Implication:** While CFDs offer leverage, this project uses them for a defensive hedge. Leverage impacts cost calculations (financing based on notional value) and margin, rather than seeking amplified speculative returns.

## 📌 Objectives

The core objectives of this project are to:

1.  **Compare Performance:** Simulate and contrast the performance of:
    *   **Model A (Classic):** 80% S&P 500 equities, 20% cash.
    *   **Model B (VIX Momentum Hedge):** 80% S&P 500 equities, 20% initial cash, with short S&P 500 CFDs activated based on the VIX momentum strategy to hedge a specified portion of equity exposure.
2.  **Evaluate Risk & Return Profile:** Quantify how the VIX-momentum CFD hedging strategy affects:
    *   Portfolio volatility and risk-adjusted returns (Sharpe Ratio, Sortino Ratio).
    *   Downside risk (Maximum Drawdown, VaR, Expected Shortfall).
3.  **Incorporate Realistic Costs:** Model the financial impact of using CFDs, including overnight financing (based on SOFR and broker fees), spread costs on closing, and initial margin.
4.  **Simulate Crisis Behavior:** Analyze portfolio performance during specific historical (COVID-19 crash) and simulated high-stress periods.
5.  **Test Hypotheses:** Evaluate predefined hypotheses regarding the effects of the VIX-momentum CFD hedging strategy.

## 📊 Key Metrics Used

*   **Total Return & Annualized Return**
*   **Annualized Volatility (Standard Deviation)**
*   **Sharpe Ratio** (risk-adjusted return using average SOFR as risk-free rate proxy)
*   **Sortino Ratio** (risk-adjusted return focusing on downside deviation)
*   **Maximum Drawdown (MDD)**
*   **Value at Risk (VaR 95%)** (Historical)
*   **Expected Shortfall (ES / CVaR 95%)** (Historical)
*   Omega Ratio, Skewness, Kurtosis, Win/Loss Ratios, Profit Factor, Recovery Factor.

## 📈 Data Used

| Data Component       | Source/Ticker/Label          | Used For                                                  |
| :------------------- | :--------------------------- | :-------------------------------------------------------- |
| S&P 500 Index Prices | `^GSPC` (API)                | Portfolio equity component returns                        |
| VIX Index Levels     | `^VIX` (API)                 | VIX momentum signal generation for hedging strategy       |
| SOFR Rate (USD O/N)  | `SOFR.csv` (local file)      | Benchmark rate for CFD overnight financing calculations |

*Note: S&P 500 and VIX data are fetched via the Financial Modeling Prep (FMP) API. SOFR data is loaded from a local CSV file.*

## ⚙️ Technology Stack

*   **Language:** Python (3.8+)
*   **Core Libraries:** `pandas`, `numpy`, `requests`, `plotly`

## 📁 Project Structure

The project is organized into Python scripts for modularity:

*   **`config.py`**: All configuration parameters, API keys, file paths, and simulation settings.
*   **`data_loader.py`**: Functions for fetching (S&P 500, VIX via FMP) and loading (SOFR from CSV) market data.
*   **`signal_generation.py`**: Implements the VIX momentum strategy to generate `Short_Signal_Today`, `Cover_Signal_Momentum_Today`, and `Cover_Signal_Absolute_VIX_Today` signals.
*   **`simulation_engine.py`**: Contains `simulate_portfolio_A` and `simulate_portfolio_B_momentum` functions.
*   **`risk_metrics.py`**: Calculates the comprehensive set of financial and risk metrics.
*   **`plotting.py`**: Generates Plotly charts for visualization.
*   **`main_analysis.py`**: Orchestrates the entire workflow: data loading, signal generation, simulation, metrics calculation, hypothesis testing, and plotting.

## 📜 Script Breakdown and Logic

| Script Name             | Purpose                                                              | Key Logic / Functionality                                                                                                                                                                                                                            |
| :---------------------- | :------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config.py`             | Central configuration.                                               | Stores API keys, file paths, simulation start/end dates, portfolio allocations, VIX momentum parameters (lookback, thresholds, consecutive days), CFD costs (broker fee, spread, margin).                                                                |
| `data_loader.py`        | Data acquisition and preparation.                                    | Fetches S&P 500 & VIX from FMP API; loads SOFR from `SOFR.csv`; merges data; calculates basic returns.                                                                                                                                                 |
| `signal_generation.py`  | VIX momentum signal logic.                                           | Calculates VIX percentage change over a lookback, identifies up/down momentum conditions based on thresholds, counts consecutive days meeting conditions, and generates `Short_Signal_Today` and cover signals based on rules defined in `config.py`.      |
| `simulation_engine.py`  | Core portfolio simulation.                                           | `simulate_portfolio_A` for classic strategy. `simulate_portfolio_B_momentum` implements the dynamic hedge: updates equity, applies CFD financing (SOFR - broker fee), opens/closes short CFDs based on signals from `signal_generation.py`, applies spread costs, manages margin. |
| `risk_metrics.py`       | Portfolio metrics computation.                                       | `calculate_metrics_summary` function computes a wide array of performance and risk metrics.                                                                                                                                                            |
| `plotting.py`           | Visualization.                                                       | Generates Plotly charts for market data (S&P 500/VIX), portfolio performance comparisons, and specific crisis period analyses (e.g., COVID recovery with trough markers).                                                                                 |
| `main_analysis.py`      | Main execution script.                                               | Orchestrates calls to other modules: loads config, loads data, generates signals, runs simulations for full and crisis periods, calculates metrics, prints hypothesis testing results, and calls plotting functions.                                     |

## 💼 Relevance

This project provides insights into:

*   **Dynamic Hedging:** Evaluating a rules-based VIX momentum strategy for activating CFD hedges.
*   **Crisis Performance:** Assessing how such a strategy performs during market stress versus normal conditions.
*   **Cost Impact:** Quantifying the effect of CFD trading costs on overall portfolio results.
*   **Risk-Return Trade-offs:** Understanding the balance between potential risk reduction and performance drag.

## 🧪 Methodology

1.  **Configuration:** Parameters are set in `config.py`.
2.  **Data Acquisition & Preparation (`data_loader.py`):**
    *   S&P 500 and VIX data fetched from FMP API.
    *   SOFR data loaded from `SOFR.csv`.
    *   Data is merged, cleaned, and basic returns calculated.
3.  **Signal Generation (`signal_generation.py`):**
    *   VIX momentum signals (`Short_Signal_Today`, `Cover_Signal_Momentum_Today`, `Cover_Signal_Absolute_VIX_Today`) are generated daily based on parameters in `config.py`.
4.  **Model Simulation (`simulation_engine.py`):**
    *   **Model A:** Value calculated daily based on S&P 500 returns and static allocation.
    *   **Model B:**
        *   Equity portion tracks S&P 500.
        *   Daily, checks signals:
            *   If `Short_Signal_Today` is true and not hedged: open short CFD hedge (calculating notional, deducting margin, applying entry price).
            *   If hedged and (`Cover_Signal_Momentum_Today` or `Cover_Signal_Absolute_VIX_Today`) is true: close CFD hedge (calculating P&L, applying spread cost, returning margin).
        *   Daily CFD financing costs/credits (SOFR - Broker Fee) applied to cash if CFD is active.
        *   Portfolio rebalanced daily to target equity/cash allocations.
5.  **Analysis & Metrics (`main_analysis.py`, `risk_metrics.py`):**
    *   Simulations run for the full period and specified crisis periods.
    *   Comprehensive performance and risk metrics calculated.
    *   Hypotheses evaluated based on these metrics.
6.  **Visualization (`plotting.py`):** Key results are plotted.

## 📈 Hypotheses Evaluated

The simulation results are used to assess hypotheses (H1-H6) regarding the VIX-momentum CFD hedging strategy's impact on:

*   **H1:** Average portfolio return.
*   **H2:** Overall portfolio volatility.
*   **H3:** Risk-adjusted return (Sharpe Ratio).
*   **H4:** Risk reduction (Max Drawdown and Volatility).
*   **H5:** Portfolio reaction magnitude during the acute COVID-19 crisis.
*   **H6:** Strength of recovery post-COVID trough compared to the classic portfolio.

*Detailed findings for each hypothesis are printed to the console by `main_analysis.py`.*

## 📉 CFD Cost Assumptions (Modeled)

*   **Spread:** Applied as a percentage cost (`SPREAD_COST_PERCENT`) on the notional value when closing short hedge positions.
*   **Financing (Overnight):** Calculated daily for active short CFD positions. The net rate is `(SOFR_Rate_Daily - BROKER_FEE_ANNUALIZED_Daily)`. A positive result is a credit to cash; a negative result is a debit.
*   **Margin:** A percentage (`CFD_INITIAL_MARGIN_PERCENT`) of the CFD's notional value is deducted from cash when a position is opened and returned when closed. This affects available cash but not directly P&L until a position is closed or financing is considered on potentially reduced cash balances (implicitly handled by overall portfolio rebalancing).
*   *Commissions, Slippage, Currency Conversion are currently excluded for simplicity.*

## 🗂 Setup and Usage

### Prerequisites

*   Python 3.8+
*   Required libraries (see `requirements.txt` if provided, or install manually):
    ```bash
    pip install pandas numpy requests plotly
    ```

### Setup and Configuration

1.  **API Key**:
    *   Open `config.py`.
    *   Replace the placeholder value for `FMP_API_KEY` with your actual FMP API key:
        ```python
        FMP_API_KEY = "YOUR_ACTUAL_FMP_API_KEY"
        ```

2.  **SOFR Data**:
    *   Ensure `SOFR.csv` is in the project's root directory. It must contain `observation_date` and `SOFR` (as percentage) columns.
    *   Adjust `SOFR_CSV_FILEPATH` in `config.py` if needed.
    *   `TARGET_SOFR_COL_NAME` in `config.py` should match the CSV's SOFR value column name.

3.  **Review `config.py`**: Adjust dates, initial capital, allocations, VIX signal parameters, and CFD costs as desired.

### Running the Simulation

1.  Navigate to the project's root directory in your terminal.
2.  Execute `main_analysis.py`:
    ```bash
    python main_analysis.py
    ```

### Expected Output

*   Console messages detailing simulation progress.
*   Plotly charts displayed in your web browser (market data, full portfolio performance, COVID crisis/recovery analysis).
*   A console table summarizing full-period financial metrics.
*   Console output of findings for Hypotheses H1-H6.

### Troubleshooting

*   **`FileNotFoundError: 'SOFR.csv'`**: Check `SOFR.csv` location and `SOFR_CSV_FILEPATH` in `config.py`.
*   **API Key Errors (FMP)**: Verify `FMP_API_KEY`, internet connection, and FMP plan limits.
*   **Plots Not Showing**: Ensure browser pop-ups are allowed.
*   **`KeyError`/`AttributeError`**: Check for missing data columns or misconfigured parameters in `config.py`.
*   **Performance**: Initial data fetching via API can be slow.