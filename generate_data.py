import yfinance as yf
import pandas as pd
import numpy as np
import json

# Define the ticker symbols and the start date
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

# Prepare data for JSON
data_stock = data_stock.dropna()
data_bitcoin = data_bitcoin.dropna()

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
    'btc_vol_365d': data_bitcoin['365d RV'].tolist()
}

# Save to JSON file
with open('data1.json', 'w') as f:
    json.dump(data_json, f)
