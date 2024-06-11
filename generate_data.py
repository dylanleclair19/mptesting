import yfinance as yf
import pandas as pd
import numpy as np
import json
import datetime

# Mapping tickers to human-readable names
ticker_names = {
    "3350.T": "Metaplanet",
    "BTC-USD": "Bitcoin",
    "GC=F": "Gold",
    "NIY=F": "Nikkei",
    "JPY=X": "USD"
}

# Define the tickers to analyze, excluding JPYUSD
tickers = list(ticker_names.keys())
# Adding JPYUSD for calculations only
tickers_for_conversion = tickers + ["JPYUSD=X"]

# Define the date range
start_date = "2024-04-08"
end_date = datetime.datetime.today().strftime('%Y-%m-%d')

# Function to calculate the percentage change
def percentage_change(start, end):
    return ((end - start) / start) * 100

# Function to convert USD to JPY
def to_jpy(usd_price, jpyusd_rate):
    return usd_price * jpyusd_rate

# Create an empty dictionary to store percentage changes
percent_changes = {}

# Fetch JPY/USD exchange rate data for conversion
jpyusd_data = yf.download("JPYUSD=X", start=start_date, end=end_date)
jpyusd_rate_start = jpyusd_data['Close'].iloc[0]
jpyusd_rate_end = jpyusd_data['Close'].iloc[-1]

# Fetch data for Metaplanet and get the last known price
metaplanet_ticker = "3350.T"
metaplanet_data = yf.download(metaplanet_ticker, start=start_date, end=end_date)
if not metaplanet_data.empty:
    metaplanet_start_price = metaplanet_data['Close'].iloc[0]
    metaplanet_ticker_data = yf.Ticker(metaplanet_ticker)
    metaplanet_last_known_price = metaplanet_ticker_data.history(period="1d")['Close'].iloc[-1]

    metaplanet_percent_change = percentage_change(metaplanet_start_price, metaplanet_last_known_price)
    percent_changes[ticker_names[metaplanet_ticker]] = metaplanet_percent_change

# Fetch data for each ticker and convert to JPY where needed
for ticker in tickers:
    if ticker == metaplanet_ticker:
        continue
    data = yf.download(ticker, start=start_date, end=end_date)
    if not data.empty:
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]

        if ticker in ["BTC-USD", "GC=F"]:  # Convert to JPY if in USD
            start_price = to_jpy(start_price, jpyusd_rate_start)
            end_price = to_jpy(end_price, jpyusd_rate_end)

        percent_change = percentage_change(start_price, end_price)
        percent_changes[ticker_names[ticker]] = percent_change

# Define the tickers and date range for hourly data
ticker_stock = "3350.T"
ticker_bitcoin = "BTC-USD"
start_date = "2022-01-01"

# Fetch the data using yfinance
data_stock = yf.download(ticker_stock, start=start_date)
data_bitcoin = yf.download(ticker_bitcoin, start=start_date)

# Calculate daily returns
data_stock['Returns'] = data_stock['Adj Close'].pct_change()
data_bitcoin['Returns'] = data_bitcoin['Adj Close'].pct_change()

# Calculate realized volatility
def realized_volatility(returns, window, annual_factor):
    return returns.rolling(window=window).std() * np.sqrt(annual_factor)

data_stock['7d RV'] = realized_volatility(data_stock['Returns'], 7, 252)
data_stock['14d RV'] = realized_volatility(data_stock['Returns'], 14, 252)
data_stock['30d RV'] = realized_volatility(data_stock['Returns'], 30, 252)
data_stock['90d RV'] = realized_volatility(data_stock['Returns'], 90, 252)
data_stock['180d RV'] = realized_volatility(data_stock['Returns'], 180, 252)
data_stock['365d RV'] = realized_volatility(data_stock['Returns'], 365, 252)

data_bitcoin['7d RV'] = realized_volatility(data_bitcoin['Returns'], 7, 365)
data_bitcoin['14d RV'] = realized_volatility(data_bitcoin['Returns'], 14, 365)
data_bitcoin['30d RV'] = realized_volatility(data_bitcoin['Returns'], 30, 365)
data_bitcoin['90d RV'] = realized_volatility(data_bitcoin['Returns'], 90, 365)
data_bitcoin['180d RV'] = realized_volatility(data_bitcoin['Returns'], 180, 365)
data_bitcoin['365d RV'] = realized_volatility(data_bitcoin['Returns'], 365, 365)

# Fetch hourly data for VWAP calculation
data_hourly = yf.download(ticker_stock, start='2024-04-09', end=datetime.datetime.now().strftime('%Y-%m-%d'), interval='1h')

# Calculate the volume-weighted average price (VWAP)
data_hourly['VWAP'] = (data_hourly['Close'] * data_hourly['Volume']).cumsum() / data_hourly['Volume'].cumsum()

# Prepare data for JSON
data_stock = data_stock.dropna()
data_bitcoin = data_bitcoin.dropna()
data_hourly = data_hourly.dropna()

data_json = {
    'dates': data_stock.index.strftime('%Y-%m-%d').tolist(),
    'prices': data_stock['Adj Close'].tolist(),
    'vol_7d': data_stock['7d RV'].tolist(),
    'vol_14d': data_stock['14d RV'].tolist(),
    'vol_30d': data_stock['30d RV'].tolist(),
    'vol_90d': data_stock['90d RV'].tolist(),
    'vol_180d': data_stock['180d RV'].tolist(),
    'vol_365d': data_stock['365d RV'].tolist(),
    'btc_dates': data_bitcoin.index.strftime('%Y-%m-%d').tolist(),
    'btc_prices': data_bitcoin['Adj Close'].tolist(),
    'btc_vol_7d': data_bitcoin['7d RV'].tolist(),
    'btc_vol_14d': data_bitcoin['14d RV'].tolist(),
    'btc_vol_30d': data_bitcoin['30d RV'].tolist(),
    'btc_vol_90d': data_bitcoin['90d RV'].tolist(),
    'btc_vol_180d': data_bitcoin['180d RV'].tolist(),
    'btc_vol_365d': data_bitcoin['365d RV'].tolist(),
    'hourly_dates': data_hourly.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
    'hourly_close': data_hourly['Close'].tolist(),
    'hourly_vwap': data_hourly['VWAP'].tolist(),
    'percent_changes': percent_changes
}

# Save to JSON file
with open('data1.json', 'w') as f:
    json.dump(data_json, f)
