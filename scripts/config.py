# --- API & File Configuration ---
FMP_API_KEY = "m8TZJWQFGH7G6x2nowAqKdzDfAyakr0T" # Please use your own API key
SOFR_CSV_FILEPATH = 'SOFR.csv'
TARGET_SOFR_COL_NAME = 'SOFR' # Column name for processed SOFR rate

# --- Data Fetching & General Simulation Period ---
START_DATE = "2019-01-01"
END_DATE = "2025-05-21" # Ensure this covers all analysis periods

# --- Portfolio Configuration ---
INITIAL_CAPITAL = 1_000_000

# Model A (Classic)
EQUITY_ALLOC_A = 0.80
CASH_ALLOC_A = 1.0 - EQUITY_ALLOC_A # Calculated for consistency

# Model B (Dynamic/VIX Momentum Hedge)
EQUITY_ALLOC_B = 0.80
CASH_ALLOC_B = 1.0 - EQUITY_ALLOC_B # Calculated for consistency
MODEL_B_FIXED_HEDGE_RATIO_MOMENTUM = 0.70 # Hedge ratio for the VIX momentum strategy

# --- VIX Momentum Signal Generation Parameters ---
MOMENTUM_LOOKBACK_PERIOD = 5
VIX_PCT_CHANGE_THRESHOLD_UP = 0.35  # > +35%
VIX_PCT_CHANGE_THRESHOLD_DOWN = -0.20 # < -20%
N_CONSECUTIVE_UP_DAYS_TO_SHORT = 3
N_CONSECUTIVE_DOWN_DAYS_TO_COVER = 1
VIX_ABSOLUTE_COVER_THRESHOLD = 20.0

# --- CFD Cost Parameters (for Model B) ---
BROKER_FEE_ANNUALIZED = 0.025 # 2.5% annual fee for CFD financing (subtracted from SOFR for CFD P&L)
SPREAD_COST_PERCENT = 0.0002 # 0.02% of notional value as spread cost on closing CFD
CFD_INITIAL_MARGIN_PERCENT = 0.05 # 5% initial margin on CFD notional

# --- Crisis Period Definitions ---
# For H5 (Acute COVID Crisis)
COVID_CRISIS_START_DATE = "2020-02-01"
COVID_CRISIS_END_DATE = "2020-04-30"

# For H6 (COVID Crisis & Recovery Assessment)
COVID_ANALYSIS_START_DATE = "2020-02-01"    # Start of the crisis for trough identification
COVID_ANALYSIS_END_DATE = "2020-08-31"      # End of the recovery assessment period for H6

# For potential 2025 Crisis (if data extends this far and is simulated)
CRISIS_2025_START_DATE = "2025-03-01"
# CRISIS_2025_END_DATE will be set dynamically in main_analysis.py if needed,
# or ensure END_DATE above covers it.

# --- Metrics Calculation ---
TRADING_DAYS_PER_YEAR = 252

# --- Plotting ---
PORTFOLIO_A_LABEL = "A (Classic)"
# PORTFOLIO_B_LABEL will be f-string formatted in main script for dynamic hedge ratio
PLOT_TITLE_PERFORMANCE = "Hedge Fund Performance"
COLOR_A = "orange"
COLOR_B = "#007BBF"