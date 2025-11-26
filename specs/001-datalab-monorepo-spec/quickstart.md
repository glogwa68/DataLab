# DataLab Quickstart

## Installation

Requirements: Python 3.10+

```bash
# Clone the repository
git clone <repo_url>
cd datalab

# Install in editable mode with dev dependencies
pip install -e .[dev]
```

## Configuration

Create a `config.json` file in the root directory:

```json
{
  "collector": {
    "buffer_size": 50000,
    "exchanges": [
      {
        "name": "dydx",
        "symbols": ["BTC-USD", "ETH-USD"]
      },
      {
        "name": "binance",
        "symbols": ["BTCUSDT", "ETHUSDT"]
      }
    ],
    "data_dir": "./market_data"
  }
}
```

## Usage

### 1. Collect Data

Start the data collector to stream and save market data:

```bash
datalab collect --config config.json
```

The collector will:
- Connect to configured exchanges via WebSocket
- Normalize ticks to standard format
- Buffer data in memory
- Periodically flush to Parquet files in `./market_data`

### 2. Run Backtest

Run a Dollar Cost Averaging (DCA) backtest on collected or historical data:

```bash
datalab backtest --strategy dca_daily --asset BTC-USD --start 2023-01-01 --end 2023-12-31
```

### 3. Analyze & Visualize

Generate comparison charts for collected spreads:

```bash
datalab analyze spreads --input ./market_data --output ./report.html
```

## Development

Run tests:

```bash
pytest tests/
```
