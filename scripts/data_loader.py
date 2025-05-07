# data_loader.py
import requests
import pandas as pd

def get_fmp_price_history(symbol, api_key, start="2019-01-01", end="2025-12-31"):
    """
    Fetch historical close prices for a given symbol from FMP API.
    """
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={start}&to={end}&apikey={api_key}"
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Error fetching {symbol}: {r.text}")
    data = r.json().get("historical", [])
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df[["close"]].rename(columns={"close": symbol})

def load_vix_sp500_data(api_key, start="2019-01-01", end="2025-12-31"):
    """
    Load S&P500 and VIX data from FMP and add placeholder SOFR rate.
    """
    sp500 = get_fmp_price_history("^GSPC", api_key, start, end)
    vix = get_fmp_price_history("^VIX", api_key, start, end)

    df = sp500.join(vix, how="inner")
    df.columns = ["S&P500", "VIX"]
    df["SOFR"] = 0.015  # Placeholder
    return df

def save_to_csv(df, filename="vix_sp500_data.csv"):
    df.to_csv(filename)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Replace with your actual API key when running locally
    API_KEY = "YOUR_API_KEY_HERE"

    df = load_vix_sp500_data(API_KEY)
    save_to_csv(df)
