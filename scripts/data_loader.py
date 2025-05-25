import pandas as pd
import requests
import numpy as np # For np.nan if needed in future extensions

def load_sofr_data(filepath, target_col_name='SOFR_Rate', start_date_str=None, end_date_str=None):
    """Loads and processes SOFR data from a CSV file."""
    try:
        df_sofr = pd.read_csv(filepath, na_values=['', '.'])
        # print(f"Successfully read '{filepath}'. Initial rows: {len(df_sofr)}")
    except FileNotFoundError:
        print(f"ERROR: File '{filepath}' not found. Returning empty DataFrame.")
        return pd.DataFrame(columns=['date', target_col_name])

    if df_sofr.empty:
        return pd.DataFrame(columns=['date', target_col_name])

    df_sofr.rename(columns={'observation_date': 'date', 'SOFR': 'value'}, inplace=True)
    df_sofr['date'] = pd.to_datetime(df_sofr['date'])
    df_sofr['value'] = pd.to_numeric(df_sofr['value'], errors='coerce')
    df_sofr[target_col_name] = df_sofr['value'] / 100.0 # Convert from percent to decimal

    df_sofr = df_sofr[['date', target_col_name]].set_index('date').sort_index()
    df_sofr[target_col_name] = df_sofr[target_col_name].ffill()
    df_sofr.reset_index(inplace=True)

    # Filter by date range if provided
    if start_date_str:
        df_sofr = df_sofr[df_sofr['date'] >= pd.to_datetime(start_date_str)]
    if end_date_str:
        df_sofr = df_sofr[df_sofr['date'] <= pd.to_datetime(end_date_str)]
    
    df_sofr = df_sofr.drop_duplicates(subset=['date'], keep='last').reset_index(drop=True)
    return df_sofr

def fetch_fmp_historical_data(symbol, api_key, from_date, to_date):
    """Fetches historical 'close' price data for a symbol from FMP."""
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={from_date}&to={to_date}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(columns=['date', 'close'])


    if not data or not data.get('historical'):
        print(f"Warning: No historical data found or 'historical' key missing for {symbol} from {from_date} to {to_date}.")
        return pd.DataFrame(columns=['date', 'close'])
        
    df = pd.DataFrame(data['historical'])
    if 'date' not in df.columns or 'close' not in df.columns:
        print(f"Warning: 'date' or 'close' column missing in FMP data for {symbol}.")
        return pd.DataFrame(columns=['date', 'close'])

    df = df[['date', 'close']].copy()
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.sort_values(by='date', ascending=True).reset_index(drop=True)
    return df

def load_and_prepare_market_data(cfg):
    """Loads S&P500, VIX, and SOFR data, merges, and prepares them."""
    print("--- Loading and Preparing Market Data ---")
    # 1. Fetch S&P 500 data
    df_sp500 = fetch_fmp_historical_data("^GSPC", cfg.FMP_API_KEY, cfg.START_DATE, cfg.END_DATE)
    if df_sp500.empty:
        print("Critical error: S&P500 data could not be loaded. Exiting.")
        return pd.DataFrame()
    df_sp500 = df_sp500.rename(columns={'close': 'S&P500'})

    # 2. Fetch VIX data
    df_vix = fetch_fmp_historical_data("^VIX", cfg.FMP_API_KEY, cfg.START_DATE, cfg.END_DATE)
    if df_vix.empty:
        print("Critical error: VIX data could not be loaded. Exiting.")
        return pd.DataFrame()
    df_vix = df_vix.rename(columns={'close': 'VIX'})

    # 3. Process SOFR data
    df_sofr_processed = load_sofr_data(cfg.SOFR_CSV_FILEPATH, cfg.TARGET_SOFR_COL_NAME, cfg.START_DATE, cfg.END_DATE)
    if df_sofr_processed.empty:
        print("Warning: SOFR data could not be loaded. Proceeding without it if possible, or this may cause errors.")
        # Create a dummy SOFR DataFrame to allow merging if only SOFR is missing
        # This helps avoid merge errors but subsequent calculations needing SOFR will fail
        date_range = pd.date_range(start=cfg.START_DATE, end=cfg.END_DATE, freq='B')
        df_sofr_processed = pd.DataFrame({'date': date_range, cfg.TARGET_SOFR_COL_NAME: np.nan})


    # 4. Merge dataframes
    df_combined = pd.merge(df_sp500, df_vix, on='date', how='inner')
    if not df_sofr_processed.empty:
         df_combined = pd.merge(df_combined, df_sofr_processed, on='date', how='left') # Left merge to keep all market days
    else: # If SOFR is truly empty and dummy wasn't created or failed
        df_combined[cfg.TARGET_SOFR_COL_NAME] = np.nan


    # 5. Calculate returns and lagged values
    df_combined = df_combined.sort_values(by='date').reset_index(drop=True)
    df_combined['Prev_S&P500'] = df_combined['S&P500'].shift(1)
    df_combined['SP500_Return'] = df_combined['S&P500'].pct_change() # More direct

    # VIX Return (example, 5-day lag from notebook, might be different from signal generation)
    df_combined['Prev_VIX_5D_for_report'] = df_combined['VIX'].shift(5) 
    df_combined['VIX_Return_5D_for_report'] = (df_combined['VIX'] - df_combined['Prev_VIX_5D_for_report']) / df_combined['Prev_VIX_5D_for_report']

    # Select and order final columns (can be adjusted)
    # Note: VIX_Return and SP500_Return are now standard pct_change.
    # Prev_S&P500 is useful. VIX_Return (daily) can be added if needed.
    final_columns_base = ['date', 'S&P500', 'VIX', cfg.TARGET_SOFR_COL_NAME, 'SP500_Return', 'Prev_S&P500']
    
    # Add SOFR if it was successfully loaded
    #if cfg.TARGET_SOFR_COL_NAME not in df_combined.columns and not df_sofr_processed.empty:
    #    df_combined = pd.merge(df_combined, df_sofr_processed[['date', cfg.TARGET_SOFR_COL_NAME]], on='date', how='left')
    
    # df_final = df_combined[final_columns_base].copy() # Removed VIX_Return_5D as it might be confusing here
    df_final = df_combined.copy() # Keep all for flexibility, filter later if needed
    
    print(f"Market data prepared. Shape: {df_final.shape}")
    # print("Sample of prepared data:")
    # print(df_final.head(2))
    return df_final