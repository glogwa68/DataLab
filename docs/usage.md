# DataLab Usage Guide

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -e .[dev]
    ```

## Configuration

Create a `config.json` file:

```json
{
  "collector": {
    "buffer_size": 10000,
    "spread_threshold": 5.0,
    "exchanges": [
      {
        "name": "dydx",
        "symbols": ["BTC-USD"]
      },
      {
        "name": "binance",
        "symbols": ["BTC-USD"]
      },
      {
        "name": "simulated",
        "symbols": ["ETH-USD"]
      }
    ],
    "data_dir": "./market_data"
  }
}
```

## Commands

### Collect Data

Start the data collector:

```bash
datalab collect --config config.json
```

Use `--spread-threshold` to override config:

```bash
datalab collect --config config.json --spread-threshold 10.0
```

### Backtest

Run a backtest (simulation with dummy data in MVP):

```bash
datalab backtest --strategy dca_daily --asset BTC-USD --start 2023-01-01 --end 2023-12-31
```

### Analyze

Generate a spread comparison report from collected data:

```bash
datalab analyze --input ./market_data --output ./spread_report.html
```
