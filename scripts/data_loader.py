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
            # Try to load .env file if python-dotenv is installed
            try:
                from dotenv import load_dotenv
                # Assume .env is in the project root relative to config file
                project_root = os.path.dirname(os.path.abspath(config.get('_config_path_', './config/params.yaml'))) # Requires passing config path or better discovery
                if project_root.endswith('config'): project_root = os.path.dirname(project_root)
                env_path = os.path.join(project_root, '.env')
                if os.path.exists(env_path):
                    load_dotenv(dotenv_path=env_path)
                    api_key = os.environ.get(api_key_var) # Try again
                    print(f"Loaded .env file from {env_path}")
                else:
                    print(f".env file not found at {env_path}")
            except ImportError:
                print("python-dotenv not installed, cannot load .env file.")
            except Exception as e_env:
                print(f"Error loading .env file: {e_env}")

            if not api_key: # Still no key
                 raise ValueError(f"API key environment variable '{api_key_var}' not set and could not be loaded from .env.")

        try:
            # Initialize FMP Loader
            fmp_loader = FMPDataLoader(api_key=api_key, start=start_date, end=end_date)
            # Fetch SPX and VIX
            fetched_df = fmp_loader.fetch_sp500_vix(sp500_api_sym, vix_api_sym)

            # --- Merge with SOFR from local file ---
            if not os.path.exists(data_file):
                 raise FileNotFoundError(f"Cannot merge SOFR: Local data file '{data_file}' for SOFR is required but not found.")

            print(f"Loading SOFR data from local file: {data_file}")
            try:
                 # Load only necessary columns for merge
                 local_df_for_sofr = pd.read_csv(data_file, usecols=[date_col, sofr_col], index_col=date_col, parse_dates=True)
            except Exception as e:
                 raise ValueError(f"Error reading local file '{data_file}' for SOFR merge: {e}") from e

            if sofr_col not in local_df_for_sofr.columns:
                 raise ValueError(f"SOFR column '{sofr_col}' not found in local file '{data_file}'")

            sofr_series = local_df_for_sofr[[sofr_col]]

            # Rename fetched columns to match config targets BEFORE join
            # Ensure the API symbols are actually present if fetch returned partially
            rename_map = {}
            if sp500_api_sym in fetched_df.columns: rename_map[sp500_api_sym] = sp500_col
            if vix_api_sym in fetched_df.columns: rename_map[vix_api_sym] = vix_col
            if rename_map: fetched_df = fetched_df.rename(columns=rename_map)

            # Join fetched data with SOFR Series (inner join requires index names to match or be None)
            fetched_df.index.name = date_col # Ensure index has the target name
            sofr_series.index.name = date_col
            df_merged = fetched_df.join(sofr_series, how='inner')
            print(f"Merged API data with local SOFR. Resulting shape: {df_merged.shape}")

            if df_merged.empty:
                 print("Warning: DataFrame empty after merging API data with local SOFR. Check date alignment / API response.")
                 # Fallback logic
                 if os.path.exists(data_file):
                     print("Falling back to loading data entirely from local CSV.")
                     df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
                     data_source = "CSV file (fallback)"
                 else:
                     raise ValueError("Merge failed and local fallback file not found.")
            else:
                 df = df_merged
                 # Optionally save the newly fetched/merged data
                 try:
                     os.makedirs(os.path.dirname(data_file), exist_ok=True)
                     df.to_csv(data_file)
                     print(f"Successfully saved fetched and merged data to {data_file}")
                 except Exception as e:
                     print(f"Warning: Could not save fetched data to {data_file}: {e}")

        except Exception as e:
            print(f"ERROR during API fetch or SOFR merge: {e}")
            # Fallback to loading local file if API fails
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

    # --- Load from file if not fetching ---
    if df is None:
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file '{data_file}' not found and API fetching not enabled/failed.")
        print(f"Loading data from local CSV file: {data_file}")
        try:
            # Attempt to load with specified date column as index
            df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
            data_source = "CSV file"
        except Exception as e:
            print(f"Error reading CSV file '{data_file}': {e}")
            raise

    # --- Common Preparation Steps ---
    print("-" * 20)
    print(f"Preparing data loaded from: {data_source}")

    # Ensure target column names exist (defensive rename)
    # Necessary if loading CSV that doesn't already have the target names
    # This assumes the raw CSV has *some* consistent name for S&P500, VIX, SOFR
    # Adjust the keys here if your raw CSV uses different names than the API symbols
    raw_sp500_name_in_csv = config.get('raw_csv_sp500_col', sp500_col) # Example: add config for raw names
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


    # Check required columns after potential rename/load
    required_cols = [sp500_col, vix_col, sofr_col]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame missing required columns after loading/fetching: {missing}. Available: {df.columns.tolist()}")

    # Ensure numeric types AFTER loading/merging/renaming
    for col in required_cols:
         # Use errors='coerce' to turn problematic values into NaN
         df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate necessary metrics
    # Ensure S&P500 price is not zero or negative before calculating return to avoid inf/-inf
    df.loc[df[sp500_col] <= 0, sp500_col] = np.nan # Replace 0 or negative prices with NaN
    df['SP500_Return'] = df[sp500_col].pct_change()
    df['Prev_S&P500'] = df[sp500_col].shift(1)

    # Drop rows with NaN in essential columns AFTER calculations
    initial_rows = len(df)
    essential_cols_final = [sp500_col, vix_col, sofr_col, 'SP500_Return', 'Prev_S&P500']
    # Additionally, check for NaN index
    df = df[df.index.notna()]
    df = df.dropna(subset=essential_cols_final)
    rows_dropped = initial_rows - len(df)

    if df.empty:
        raise ValueError("Dataframe is empty after final cleaning. Check source data and processing steps.")

    print(f"Data prepared: {len(df)} rows remaining after dropping {rows_dropped} rows with NaNs.")
    # Ensure index is DatetimeIndex and named correctly
    df.index.name = date_col
    df = df.sort_index() # Ensure final sort
    print("-" * 20)
    return df

# --- Example Usage ---
if __name__ == '__main__':
    # This block now better simulates running from the project root perspective
    # It requires config_loader.py to be importable
    try:
        # Assuming the script is run from project root or PYTHONPATH is set
        from config_loader import load_config
    except ImportError:
        # Basic fallback if running script directly within scripts/
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from scripts.config_loader import load_config


    try:
        # Load config from standard location relative to project root
        cfg = load_config() # Assumes config/params.yaml exists
        cfg['_config_path_'] = 'config/params.yaml' # Add path info if needed by other funcs

        # --- Test Case 1: Load from existing CSV ---
        print("\n" + "="*10 + " Testing Load from CSV " + "="*10)
        test_cfg_csv = cfg.copy()
        test_cfg_csv['load_from_api'] = False # Ensure loading from file
        if os.path.exists(test_cfg_csv['data_file']):
             data_csv = load_and_prepare_data(test_cfg_csv)
             print("CSV Load Head:\n", data_csv.head())
             print("CSV Load Info:")
             data_csv.info()
        else:
             print(f"SKIPPING CSV load test: File not found at {test_cfg_csv['data_file']}")

        # --- Test Case 2: Fetch from API ---
        print("\n" + "="*10 + " Testing Fetch from API " + "="*10)
        test_cfg_api = cfg.copy()
        test_cfg_api['load_from_api'] = True # Force API fetch
        test_cfg_api['force_fetch'] = True   # Ensure it fetches even if file exists

        # Check if API key var exists in env or .env loaded it
        if os.environ.get(test_cfg_api['api_key_env_var']):
             # Need the original file to merge SOFR
             if os.path.exists(test_cfg_api['data_file']):
                 data_api = load_and_prepare_data(test_cfg_api)
                 print("API Fetch (+SOFR Merge) Head:\n", data_api.head())
                 print("API Fetch (+SOFR Merge) Info:")
                 data_api.info()
                 print("Columns after fetch/prep:", data_api.columns.tolist())
             else:
                  print(f"SKIPPING API fetch test: Original data file '{test_cfg_api['data_file']}' needed for SOFR merge is missing.")
        else:
            print(f"SKIPPING API fetch test: Environment variable '{test_cfg_api['api_key_env_var']}' not set or loadable from .env.")


    except Exception as e:
        import traceback
        print(f"\n--- An error occurred during testing ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("Traceback:")
        traceback.print_exc()
