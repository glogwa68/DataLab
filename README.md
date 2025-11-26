# DataLab

A Python-based monorepo for financial data analysis, featuring a high-performance WebSocket collector for DEX perpetuals, a backtesting framework for DCA strategies, and visualization tools.

## Installation

```bash
pip install -e .[dev]
```

## Usage

### Data Collection

```bash
datalab collect --config config.json
```

### Backtesting

```bash
datalab backtest --strategy dca_daily --asset BTC-USD --start 2023-01-01 --end 2023-12-31
```

## Testing

```bash
pytest
```
