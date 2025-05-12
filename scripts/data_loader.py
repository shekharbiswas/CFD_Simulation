import pandas as pd
import os
import numpy as np
import requests
from functools import wraps
import time
import os



class FMPDataLoader:
    # ... (init, _fetch_single_symbol, fetch_sp500_vix) ...
    pass 

# In the main load_and_prepare_data function:
@log_and_time
def load_and_prepare_data(config):
    # ... (other setup) ...

    if should_fetch:
        # ...
        api_key_var = config.get('api_key_env_var')
        api_key = None # Initialize api_key
        if api_key_var:
            api_key = os.environ.get(api_key_var) # Read from environment

        if not api_key: # Check if key was actually found
            raise ValueError(f"API key environment variable '{api_key_var}' not set or not found.")
        # ... rest of fetch logic using the 'api_key' variable ...
        try:
            fmp_loader = FMPDataLoader(api_key=api_key, start=start_date, end=end_date)
            # ... fetch, merge, save ...
        except Exception as e:
            # ... error handling ...
    # ... (rest of function) ...
    return df
    
# --- Decorator (from your original script) ---
def log_and_time(func):
    """Decorator to log and time method execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        instance_name = ""
        if args and hasattr(args[0], '__class__'):
             instance_name = f"{args[0].__class__.__name__}."
        start = time.time()
        print(f"Running {instance_name}{func.__name__}...")
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{instance_name}{func.__name__} completed in {duration:.2f}s")
        return result
    return wrapper

# --- FMPDataLoader Class (integrated) ---
class FMPDataLoader:
    """Class to fetch data specifically from Financial Modeling Prep API."""
    def __init__(self, api_key: str, start: str, end: str):
        if not api_key:
             raise ValueError("FMP API key is required.")
        self.api_key = api_key
        self.start = start
        self.end = end
        self.base_url = "https://financialmodelingprep.com/api/v3"

    @log_and_time
    def _fetch_single_symbol(self, symbol: str) -> pd.DataFrame:
        """Fetches historical price data for a single symbol from FMP."""
        url = f"{self.base_url}/historical-price-full/{symbol}?from={self.start}&to={self.end}&apikey={self.api_key}"
        try:
            r = requests.get(url, timeout=30) # Add timeout
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {symbol}: {e}")
            raise ValueError(f"Network or API error fetching {symbol}: {e}") from e

        data = r.json()
        # Check for API error message
        if isinstance(data, dict) and 'Error Message' in data:
             raise ValueError(f"FMP API error for {symbol}: {data['Error Message']}")

        historical_data = data.get("historical", [])
        if not historical_data:
             print(f"Warning: No historical data returned for {symbol} from {self.start} to {self.end}")
             return pd.DataFrame(columns=[symbol]) # Return empty DataFrame with correct column

        df = pd.DataFrame(historical_data)
        if "date" not in df.columns or "close" not in df.columns:
             print(f"Warning: 'date' or 'close' column missing in FMP response for {symbol}. Response snippet: {str(data)[:200]}")
             return pd.DataFrame(columns=[symbol])

        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        # Select and rename immediately
        df_out = df[["close"]].rename(columns={"close": symbol})
        # Sort by date just in case API doesn't guarantee order
        df_out = df_out.sort_index()
        return df_out

    @log_and_time
    def fetch_sp500_vix(self, sp500_sym: str, vix_sym: str) -> pd.DataFrame:
        """Fetches S&P 500 and VIX data and joins them."""
        sp500_df = self._fetch_single_symbol(sp500_sym)
        vix_df = self._fetch_single_symbol(vix_sym)

        # Inner join to ensure matching dates
        df_joined = sp500_df.join(vix_df, how="inner")

        if df_joined.empty:
             print("Warning: Joining S&P 500 and VIX resulted in an empty DataFrame. Check symbols and date ranges.")

        return df_joined

# --- Main Data Loading Function ---
@log_and_time
def load_and_prepare_data(config):
    """
    Loads and prepares financial data.
    Can either load from a local CSV or fetch from FMP API based on config.
    If fetching, it merges fetched SPX/VIX with SOFR from the local CSV.
    """
    data_file = config['data_file']
    load_api = config.get('load_from_api', False)
    force_fetch = config.get('force_fetch', False)
    date_col = config['date_column'] # Should always be 'date' after processing
    sp500_col = config['sp500_column'] # Target column name
    vix_col = config['vix_column']     # Target column name
    sofr_col = config['sofr_column']   # Target column name

    df = None
    data_source = "CSV file"

    # --- Decide whether to fetch or load ---
    should_fetch = load_api or force_fetch or (load_api and not os.path.exists(data_file))

    if should_fetch:
        print(f"Fetching data from API (load_from_api={load_api}, force_fetch={force_fetch}, file_exists={os.path.exists(data_file)})...")
        data_source = "FMP API (+ SOFR from CSV)"
        api_key_var = config.get('api_key_env_var')
        api_key = os.environ.get(api_key_var) if api_key_var else None
        start_date = config.get('api_start_date', '2018-01-01')
        end_date = config.get('api_end_date', '2026-01-01')
        sp500_api_sym = config.get('api_symbol_sp500', '^GSPC')
        vix_api_sym = config.get('api_symbol_vix', '^VIX')

        if not api_key:
            raise ValueError(f"API key environment variable '{api_key_var}' not set.")

        try:
            # Initialize FMP Loader
            fmp_loader = FMPDataLoader(api_key=api_key, start=start_date, end=end_date)
            # Fetch SPX and VIX
            fetched_df = fmp_loader.fetch_sp500_vix(sp500_api_sym, vix_api_sym)

            # --- IMPORTANT: Merge with SOFR from local file ---
            if not os.path.exists(data_file):
                 raise FileNotFoundError(f"Cannot merge SOFR: Local data file '{data_file}' not found. Run once with load_from_api=False or provide SOFR.")

            print(f"Loading SOFR data from local file: {data_file}")
            try:
                 local_df_for_sofr = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
            except Exception as e:
                 raise ValueError(f"Error reading local file {data_file} for SOFR merge: {e}") from e

            if sofr_col not in local_df_for_sofr.columns:
                 raise ValueError(f"SOFR column '{sofr_col}' not found in local file '{data_file}'")

            sofr_series = local_df_for_sofr[[sofr_col]]

            # Rename fetched columns to match config targets BEFORE join
            fetched_df = fetched_df.rename(columns={sp500_api_sym: sp500_col, vix_api_sym: vix_col})

            # Join fetched data with SOFR Series (inner join ensures dates exist in both)
            df_merged = fetched_df.join(sofr_series, how='inner')
            print(f"Merged API data (SPX, VIX) with local SOFR. Resulting shape: {df_merged.shape}")

            if df_merged.empty:
                 print("Warning: DataFrame empty after merging API data with local SOFR. Check date alignment.")
                 # Fallback to loading local file entirely if merge fails badly
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
            print(f"Error during API fetch or SOFR merge: {e}")
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

    # --- Load from file if not fetching ---
    if df is None:
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file '{data_file}' not found and API fetching not enabled/failed.")
        print(f"Loading data from local CSV file: {data_file}")
        try:
            df = pd.read_csv(data_file, index_col=date_col, parse_dates=True)
            data_source = "CSV file"
        except Exception as e:
            print(f"Error reading CSV file {data_file}: {e}")
            raise

    # --- Common Preparation Steps ---
    print(f"Preparing data loaded from: {data_source}")

    # Ensure target column names exist (might already be correct if loaded from CSV)
    # This rename is mainly important if API symbols differ from target names
    df = df.rename(columns={
        config.get('api_symbol_sp500', '^GSPC'): sp500_col, # Rename if needed
        config.get('api_symbol_vix', '^VIX'): vix_col,       # Rename if needed
    })

    # Check required columns after potential rename/load
    required_cols = [sp500_col, vix_col, sofr_col]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame missing required columns after loading/fetching: {missing}. Available: {df.columns.tolist()}")

    # Ensure numeric types AFTER loading/merging
    for col in [sp500_col, vix_col, sofr_col]:
         df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate necessary metrics (handle potential division by zero if price is 0)
    df['SP500_Return'] = df[sp500_col].pct_change()
    df['Prev_S&P500'] = df[sp500_col].shift(1)

    # Drop rows with NaN in essential columns AFTER calculations
    initial_rows = len(df)
    essential_cols_final = [sp500_col, vix_col, sofr_col, 'SP500_Return', 'Prev_S&P500']
    df = df.dropna(subset=essential_cols_final)
    rows_dropped = initial_rows - len(df)

    if df.empty:
        raise ValueError("Dataframe is empty after final cleaning. Check source data and processing steps.")

    print(f"Data prepared: {len(df)} rows remaining after dropping {rows_dropped} rows with NaNs in essential columns.")
    # Ensure index is DatetimeIndex
    df.index.name = date_col # Set index name explicitly
    df = df.sort_index() # Ensure final sort
    return df

# --- Example Usage ---
if __name__ == '__main__':
    # Example requires config_loader to be accessible and environment variable set
    # Make sure to set FMP_API_KEY environment variable first
    # Or replace os.environ.get below with your actual key for quick testing (NOT recommended for production)
    from config_loader import load_config
    try:
        # Load config relative to this script's location assuming standard structure
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir) # Go up one level
        config_path = os.path.join(project_root, 'config/params.yaml')
        cfg = load_config(config_path)

        # --- Test Case 1: Load from existing CSV ---
        print("\n--- Testing Load from CSV ---")
        cfg['load_from_api'] = False # Ensure loading from file
        # Make sure 'data/vix_sp500_data.csv' exists from previous runs or manually
        if os.path.exists(os.path.join(project_root, cfg['data_file'])):
             data_csv = load_and_prepare_data(cfg)
             print("CSV Load Head:\n", data_csv.head())
             print("CSV Load Info:")
             data_csv.info()
        else:
             print(f"Skipping CSV load test: File not found at {os.path.join(project_root, cfg['data_file'])}")

        # --- Test Case 2: Fetch from API ---
        print("\n--- Testing Fetch from API ---")
        cfg['load_from_api'] = True # Force API fetch
        cfg['force_fetch'] = True   # Ensure it fetches even if file exists
        # Ensure FMP_API_KEY env var is set before running
        if os.environ.get(cfg['api_key_env_var']):
             # Need the original file to merge SOFR
             if os.path.exists(os.path.join(project_root, cfg['data_file'])):
                 data_api = load_and_prepare_data(cfg)
                 print("API Fetch (+SOFR Merge) Head:\n", data_api.head())
                 print("API Fetch (+SOFR Merge) Info:")
                 data_api.info()
                 # Check if columns match config targets
                 print("Columns after fetch/prep:", data_api.columns.tolist())
             else:
                  print(f"Skipping API fetch test: Original data file '{cfg['data_file']}' needed for SOFR merge is missing.")
        else:
            print(f"Skipping API fetch test: Environment variable '{cfg['api_key_env_var']}' not set.")


    except Exception as e:
        import traceback
        print(f"\n--- An error occurred during testing ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("Traceback:")
        traceback.print_exc()
