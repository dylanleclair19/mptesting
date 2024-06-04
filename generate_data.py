import yfinance as yf
import pandas as pd
import numpy as np
import json

# Define the ticker symbol and the start date
ticker = "3350.T"
start_date = "2022-01-01"

# Fetch the data using yfinance
data = yf.download(ticker, start=start_date)

# Calculate daily returns
data['Returns'] = data['Adj Close'].pct_change()

# Calculate realized volatility
def realized_volatility(returns, window):
    return returns.rolling(window=window).std() * np.sqrt(252)  # Annualize the volatility

data['7d RV'] = realized_volatility(data['Returns'], 7)
data['14d RV'] = realized_volatility(data['Returns'], 14)
data['30d RV'] = realized_volatility(data['Returns'], 30)
data['90d RV'] = realized_volatility(data['Returns'], 90)

# Prepare data for JSON
data = data.dropna()
data_json = {
    'dates': data.index.strftime('%Y-%m-%d').tolist(),
    'prices': data['Adj Close'].tolist(),
    'vol_7d': data['7d RV'].tolist(),
    'vol_14d': data['14d RV'].tolist(),
    'vol_30d': data['30d RV'].tolist(),
    'vol_90d': data['90d RV'].tolist()
}

# Save to JSON file
with open('data.json', 'w') as f:
    json.dump(data_json, f)
