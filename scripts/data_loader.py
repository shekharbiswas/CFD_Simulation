import requests
import pandas as pd
from functools import wraps
import time

def log_and_time(func):
    """Decorator to log and time any method."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Running {func.__name__}...")
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} completed in {duration:.2f}s")
        return result
    return wrapper

class FMPDataLoader:
    def __init__(self, api_key: str, start: str = "2019-01-01", end: str = "2025-12-31"):
        self.api_key = api_key
        self.start = start
        self.end = end

    @log_and_time
    def fetch_price(self, symbol: str) -> pd.DataFrame:
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={self.start}&to={self.end}&apikey={self.api_key}"
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError(f"Error fetching {symbol}: {r.text}")
        data = r.json().get("historical", [])
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        return df[["close"]].rename(columns={"close": symbol})

    @log_and_time
    def load_vix_sp500(self) -> pd.DataFrame:
        sp500 = self.fetch_price("^GSPC")
        vix = self.fetch_price("^VIX")
        df = sp500.join(vix, how="inner")
        df.columns = ["S&P500", "VIX"]
        df["SOFR"] = 0.015  # placeholder
        return df

    def save(self, df: pd.DataFrame, filename: str = "vix_sp500_data.csv"):
        df.to_csv(filename)
        print(f"Saved to {filename}")
