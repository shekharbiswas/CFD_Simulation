# scripts/data_loader.py

import pandas as pd
import os
import numpy as np
import requests
from functools import wraps
import time
import sys # Import sys for path manipulation if needed, though direct imports should work if run correctly

# --- Decorator ---
def log_and_time(func):
    """Decorator to log and time method execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to get instance name if called on a method
        instance_name = ""
        if args and hasattr(args[0], '__class__') and not isinstance(args[0], dict): # Check it's an object instance, not the config dict
             instance_name = f"{args[0].__class__.__name__}."

        start_time = time.time()
        # More robust function name getting
        func_name = getattr(func, '__name__', repr(func))
        print(f"Running {instance_name}{func_name}...")

        result = func(*args, **kwargs) # Execute the function

        duration = time.time() - start_time
        print(f"{instance_name}{func_name} completed in {duration:.2f}s")
        return result
    return wrapper

# --- FMPDataLoader Class ---
class FMPDataLoader:
    """Class to fetch data specifically from Financial Modeling Prep API."""
    def __init__(self, api_key: str, start: str, end: str):
        if not api_key:
             raise ValueError("FMP API key is required.")
        self.api_key = api_key
        self.start = start
        self.end = end
        self.base_url = "https://financialmodelingprep.com/api/v3"
        print(f"FMPDataLoader initialized for dates: {start} to {end}")

    @log_and_time
    def _fetch_single_symbol(self, symbol: str) -> pd.DataFrame:
        """Fetches historical price data for a single symbol from FMP."""
        url = f"{self.base_url}/historical-price-full/{symbol}?from={self.start}&to={self.end}&apikey={self.api_key}"
        print(f"Fetching URL: {url.replace(self.api_key, '***API_KEY***')}") # Avoid logging key
        try:
            r = requests.get(url, timeout=30) # Add timeout
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {symbol}: {e}")
            # Provide more context in the error
            raise ValueError(f"Network or API error fetching {symbol} from {url.replace(self.api_key, '***API_KEY***')}: {e}") from e

        data = r.json()
        # Check for FMP's specific error message structure
        if isinstance(data, dict) and 'Error Message' in data:
             raise ValueError(f"FMP API error for {symbol}: {data['Error Message']}")

        historical_data = data.get("historical", [])
        if not historical_data:
             print(f"Warning: No historical data returned for {symbol} from {self.start} to {self.end}")
             return pd.DataFrame(columns=[symbol], index=pd.to_datetime([])) # Return empty DF with DatetimeIndex

        df = pd.DataFrame(historical_data)

        # Validate necessary columns exist
        if "date" not in df.columns or "close" not in df.columns:
             print(f"Warning: 'date' or 'close' column missing in FMP response for {symbol}. Columns found: {df.columns.tolist()}. Response snippet: {str(data)[:200]}")
             return pd.DataFrame(columns=[symbol], index=pd.to_datetime([]))

        try:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
        except Exception as e:
            print(f"Error processing date column for {symbol}: {e}")
            return pd.DataFrame(columns=[symbol], index=pd.to_datetime([]))

        # Select, rename, and sort
        df_out = df[["close"]].rename(columns={"close": symbol})
        df_out = df_out.sort_index()
        print(f"Fetched {len(df_out)} records for {symbol}")
        return df_out

    @log_and_time
    def fetch_sp500_vix(self, sp500_sym: str, vix_sym: str) -> pd.DataFrame:
        """Fetches S&P 500 and VIX data and joins them."""
        sp500_df = self._fetch_single_symbol(sp500_sym)
        vix_df = self._fetch_single_symbol(vix_sym)

        if sp500_df.empty or vix_df.empty:
            print("Warning: Fetching resulted in empty data for S&P500 or VIX. Join may fail.")
            # Return an empty dataframe with expected columns but allow potential join
            # return pd.DataFrame(columns=[sp500_sym, vix_sym], index=pd.to_datetime([]))

        # Inner join to ensure matching dates; index name should be 'date'
        df_joined = sp500_df.join(vix_df, how="inner")

        if df_joined.empty:
             print(f"Warning: Joining S&P 500 ('{sp500_sym}') and VIX ('{vix_sym}') resulted in an empty DataFrame. Check symbols, date ranges, and API responses.")

        print(f"Joined S&P500 and VIX data. Shape: {df_joined.shape}")
        return df_joined

# --- Main Data Loading Function ---
@log_and_time
def load_and_prepare_data(config):
    """
    Loads and prepares financial data.
    Can either load from a local CSV or fetch from FMP API based on config.
    If fetching, it merges fetched SPX/VIX with SOFR from the local CSV.
    S&P 500 returns are then de-meaned and a positive drift is added.
    S&P 500 prices are reconstructed based on these modified returns.
    """
    # --- Parameter Extraction ---
    data_file = config['data_file']
    load_api = config.get('load_from_api', False)
    force_fetch = config.get('force_fetch', False)
    date_col = config['date_column'] # Expecting 'date' as index name
    sp500_col = config['sp500_column']
    vix_col = config['vix_column']
    sofr_col = config['sofr_column']

    df = None # Initialize df
    data_source = "N/A" # Track where the data came from

    # --- Decision Logic ---
    should_fetch = load_api or force_fetch or (load_api and not os.path.exists(data_file))

    # --- API Fetching Block ---
    if should_fetch:
        print("-" * 20)
        print(f"Attempting API Fetch (load_api={load_api}, force_fetch={force_fetch}, file_exists={os.path.exists(data_file)})...")
        data_source = "FMP API (+ SOFR from CSV)"
        api_key_var = config.get('api_key_env_var')
        api_key = os.environ.get(api_key_var) if api_key_var else None
        start_date = config.get('api_start_date', '2018-01-01') # Fetch buffer
        end_date = config.get('api_end_date', '2026-01-01')     # Fetch buffer
        sp500_api_sym = config.get('api_symbol_sp500', '^GSPC')
        vix_api_sym = config.get('api_symbol_vix', '^VIX')

        if not api_key:
            try:
                from dotenv import load_dotenv
                project_root = os.path.dirname(os.path.abspath(config.get('_config_path_', './config/params.yaml'))) 
                if project_root.endswith('config'): project_root = os.path.dirname(project_root)
                env_path = os.path.join(project_root, '.env')
                if os.path.exists(env_path):
                    load_dotenv(dotenv_path=env_path)
                    api_key = os.environ.get(api_key_var) 
                    print(f"Loaded .env file from {env_path}")
                else:
                    print(f".env file not found at {env_path}")
            except ImportError:
                print("python-dotenv not installed, cannot load .env file.")
            except Exception as e_env:
                print(f"Error loading .env file: {e_env}")

            if not api_key: 
                 raise ValueError(f"API key environment variable '{api_key_var}' not set and could not be loaded from .env.")

        try:
            fmp_loader = FMPDataLoader(api_key=api_key, start=start_date, end=end_date)
            fetched_df = fmp_loader.fetch_sp500_vix(sp500_api_sym, vix_api_sym)

            if not os.path.exists(data_file):
                 raise FileNotFoundError(f"Cannot merge SOFR: Local data file '{data_file}' for SOFR is required but not found.")

            print(f"Loading SOFR data from local file: {data_file}")
            try:
                 local_df_for_sofr = pd.read_csv(data_file, usecols=[date_col, sofr_col], index_col=date_col, parse_dates=True)
            except Exception as e:
                 raise ValueError(f"Error reading local file '{data_file}' for SOFR merge: {e}") from e

            if sofr_col not in local_df_for_sofr.columns:
                 raise ValueError(f"SOFR column '{sofr_col}' not found in local file '{data_file}'")

            sofr_series = local_df_for_sofr[[sofr_col]]
            rename_map = {}
            if sp500_api_sym in fetched_df.columns: rename_map[sp500_api_sym] = sp500_col
            if vix_api_sym in fetched_df.columns: rename_map[vix_api_sym] = vix_col
            if rename_map: fetched_df = fetched_df.rename(columns=rename_map)
            
            fetched_df.index.name = date_col 
            sofr_series.index.name = date_col
            df_merged = fetched_df.join(sofr_series, how='inner')
            print(f"Merged API data with local SOFR. Resulting shape: {df_merged.shape}")

            if df_merged.empty:
                 print("Warning: DataFrame empty after merging API data with local SOFR. Check date alignment / API response.")
                 if os.path.exists(data_file):
                     print("Falling back to loading data entirely from local CSV.")
                     df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
                     data_source = "CSV file (fallback)"
                 else:
                     raise ValueError("Merge failed and local fallback file not found.")
            else:
                 df = df_merged
                 try:
                     os.makedirs(os.path.dirname(data_file), exist_ok=True)
                     df.to_csv(data_file)
                     print(f"Successfully saved fetched and merged data to {data_file}")
                 except Exception as e:
                     print(f"Warning: Could not save fetched data to {data_file}: {e}")

        except Exception as e:
            print(f"ERROR during API fetch or SOFR merge: {e}")
            if os.path.exists(data_file):
                print("Attempting to load data from local CSV as fallback...")
                try:
                    df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
                    data_source = "CSV file (fallback)"
                except Exception as read_e:
                    raise ValueError(f"API fetch failed AND fallback CSV read failed: {read_e}") from read_e
            else:
                raise ValueError(f"API fetch failed and no local file '{data_file}' found for fallback.") from e
        print("-" * 20)

    if df is None:
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file '{data_file}' not found and API fetching not enabled/failed.")
        print(f"Loading data from local CSV file: {data_file}")
        try:
            df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
            data_source = "CSV file"
        except Exception as e:
            print(f"Error reading CSV file '{data_file}': {e}")
            raise

    print("-" * 20)
    print(f"Preparing data loaded from: {data_source}")

    raw_sp500_name_in_csv = config.get('raw_csv_sp500_col', sp500_col) 
    raw_vix_name_in_csv = config.get('raw_csv_vix_col', vix_col)
    raw_sofr_name_in_csv = config.get('raw_csv_sofr_col', sofr_col)

    rename_map_csv = {}
    if raw_sp500_name_in_csv in df.columns and raw_sp500_name_in_csv != sp500_col:
        rename_map_csv[raw_sp500_name_in_csv] = sp500_col
    if raw_vix_name_in_csv in df.columns and raw_vix_name_in_csv != vix_col:
        rename_map_csv[raw_vix_name_in_csv] = vix_col
    if raw_sofr_name_in_csv in df.columns and raw_sofr_name_in_csv != sofr_col:
        rename_map_csv[raw_sofr_name_in_csv] = sofr_col
    if rename_map_csv:
        print(f"Applying defensive rename for CSV columns: {rename_map_csv}")
        df = df.rename(columns=rename_map_csv)

    required_cols = [sp500_col, vix_col, sofr_col]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame missing required columns after loading/fetching: {missing}. Available: {df.columns.tolist()}")

    for col in required_cols:
         df[col] = pd.to_numeric(df[col], errors='coerce')

    df.loc[df[sp500_col] <= 0, sp500_col] = np.nan 
    
    # --- MODIFICATION FOR REALISTIC POSITIVE S&P 500 TREND ---
    # 1. Calculate original S&P500_Return
    df['SP500_Return'] = df[sp500_col].pct_change()
    
    # 2. Define target positive drift
    target_daily_positive_drift = 0.00052  # Approx 14% annualized
    
    valid_return_indices = df['SP500_Return'].notna()
    if not df.loc[valid_return_indices, 'SP500_Return'].empty:
        original_mean_return = df.loc[valid_return_indices, 'SP500_Return'].mean()
        
        # 3. Modify SP500_Return: de-mean original returns, then add target drift
        df.loc[valid_return_indices, 'SP500_Return'] = \
            (df.loc[valid_return_indices, 'SP500_Return'] - original_mean_return) + target_daily_positive_drift

        # 4. Reconstruct S&P500 prices based on modified returns
        indices_to_iterate = df.index # df.index should be DatetimeIndex
        if len(indices_to_iterate) > 1 and pd.notna(df[sp500_col].iloc[0]):
            base_price = df[sp500_col].iloc[0] # Anchor to the first price in the loaded data
            reconstructed_prices_list = [base_price]
            
            for i in range(1, len(df)):
                current_return_val = df['SP500_Return'].iloc[i]
                if pd.notna(current_return_val):
                    new_price_val = reconstructed_prices_list[-1] * (1 + current_return_val)
                    reconstructed_prices_list.append(new_price_val)
                else: 
                    reconstructed_prices_list.append(reconstructed_prices_list[-1]) 
            
            df[sp500_col] = reconstructed_prices_list
        else:
            print("Warning: S&P500 price reconstruction skipped (df too short or invalid initial price).")
    else:
        print("Warning: No valid original returns for drift modification. S&P500 prices not altered from loaded data.")
    # --- END OF MODIFICATION ---
    
    df['Prev_S&P500'] = df[sp500_col].shift(1)

    initial_rows = len(df)
    essential_cols_final = [sp500_col, vix_col, sofr_col, 'SP500_Return', 'Prev_S&P500']
    df = df[df.index.notna()]
    df = df.dropna(subset=essential_cols_final)
    rows_dropped = initial_rows - len(df)

    if df.empty:
        raise ValueError("Dataframe is empty after final cleaning. Check source data and processing steps.")

    print(f"Data prepared: {len(df)} rows remaining after dropping {rows_dropped} rows with NaNs.")
    
    # --- VIX DIAGNOSTIC (to understand original data's crisis characteristics) ---
    if 'analysis_periods' in config and 'covid_19' in config['analysis_periods']: # Check if 'covid_19' exists
        covid_crisis_period_config = config['analysis_periods']['covid_19']
        covid_start_dt = pd.to_datetime(covid_crisis_period_config['start'])
        covid_end_dt = pd.to_datetime(covid_crisis_period_config['end'])
        if isinstance(df.index, pd.DatetimeIndex):
            covid_period_mask = (df.index >= covid_start_dt) & (df.index <= covid_end_dt)
            if covid_period_mask.any() and not df.loc[covid_period_mask].empty:
                vix_during_covid_actual = df.loc[covid_period_mask, vix_col]
                print(f"\n--- VIX Stats (Original Data from CSV) during 'covid_19' ({covid_start_dt.date()} to {covid_end_dt.date()}) ---")
                print(vix_during_covid_actual.describe())
                if 'hedging_strategy' in config and 'vix_threshold' in config['hedging_strategy']:
                    vix_thresh_config = config['hedging_strategy']['vix_threshold']
                    print(f"Number of days VIX > {vix_thresh_config} during crisis: {(vix_during_covid_actual > vix_thresh_config).sum()}")
            else:
                print("Warning: No data for 'covid_19' period in the *cleaned df* for VIX diagnostic.")
        else:
            print("Warning: DataFrame index is not DatetimeIndex, VIX diagnostic for crisis period skipped.")
    # --- END VIX DIAGNOSTIC ---

    df.index.name = date_col
    df = df.sort_index() 
    print("-" * 20)
    return df

# --- Example Usage ---
if __name__ == '__main__':
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from scripts.config_loader import load_config # Adjusted import path
    except ImportError:
        print("Error: Could not import load_config. Ensure config_loader.py is in the parent directory or PYTHONPATH is set.")
        sys.exit(1)
    
    try:
        cfg = load_config(config_path='config/params.yaml') # Pass path to load_config
        cfg['_config_path_'] = 'config/params.yaml' 

        print("\n" + "="*10 + " Testing Load and Prepare Data " + "="*10)
        
        # Create a dummy data_file if it doesn't exist for the test to run
        dummy_data_file_path = cfg['data_file']
        if not os.path.exists(dummy_data_file_path):
            print(f"Creating dummy data file at {dummy_data_file_path} for testing.")
            os.makedirs(os.path.dirname(dummy_data_file_path), exist_ok=True)
            dummy_dates = pd.to_datetime(['2020-03-10', '2020-03-11', '2020-03-12'])
            dummy_data = pd.DataFrame({
                'date': dummy_dates,
                cfg['sp500_column']: [3000, 2900, 2800],
                cfg['vix_column']: [30, 40, 50],
                cfg['sofr_column']: [0.015, 0.015, 0.015]
            })
            dummy_data.to_csv(dummy_data_file_path, index=False)

        test_cfg = cfg.copy()
        test_cfg['load_from_api'] = False 
        data_processed = load_and_prepare_data(test_cfg)
        print("Processed Data Head:\n", data_processed.head())
        print("Processed Data Tail:\n", data_processed.tail())
        print("Processed Data Info:")
        data_processed.info()
        print("Columns after prep:", data_processed.columns.tolist())

    except Exception as e:
        import traceback
        print(f"\n--- An error occurred during testing ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("Traceback:")
        traceback.print_exc()