import pandas as pd
import numpy as np
import time
import os

os.makedirs("example_data", exist_ok=True)

# Generate dummy data matching StandardizedTick schema
dates = pd.date_range(start="2023-01-01", periods=100, freq="H")
df = pd.DataFrame({
    "timestamp": dates.astype(np.int64), # ns
    "exchange": ["simulated"] * 100,
    "symbol": ["BTC-USD"] * 100,
    "bid_price": np.random.normal(20000, 100, 100),
    "ask_price": np.random.normal(20000, 100, 100) + 10,
    "spread_10k": np.random.random(100) * 5,
    "spread_50k": np.random.random(100) * 10,
    "spread_100k": np.random.random(100) * 20,
    "spread_500k": np.random.random(100) * 50,
    "liquidity_bid": [100000] * 100,
    "liquidity_ask": [100000] * 100
})

df.to_parquet("example_data/sample_ticks.parquet")
print("Created example_data/sample_ticks.parquet")
