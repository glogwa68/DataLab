# Data Model: DataLab

**Feature**: DataLab Financial Analysis Platform
**Date**: 2025-11-26

## Core Entities

### 1. StandardizedTick
**Type**: Immutable Dataclass
**Purpose**: Represents a normalized snapshot of market state from any exchange.
**Storage**: Row in Parquet file.

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `int` (ns) | Unix timestamp of receipt (nanoseconds) |
| `exchange` | `str` | Normalized exchange name (e.g., "binance", "dydx") |
| `symbol` | `str` | Normalized symbol pair (e.g., "BTC-USD") |
| `bid_price` | `float` | Top of book bid price |
| `ask_price` | `float` | Top of book ask price |
| `spread_10k` | `float` | Effective spread for $10k notional |
| `spread_50k` | `float` | Effective spread for $50k notional |
| `spread_100k` | `float` | Effective spread for $100k notional |
| `spread_500k` | `float` | Effective spread for $500k notional |
| `liquidity_bid` | `float` | Total available bid liquidity within tracked depth |
| `liquidity_ask` | `float` | Total available ask liquidity within tracked depth |

### 2. BaseDCAStrategy
**Type**: Abstract Base Class (Python)
**Purpose**: Interface for implementing investment strategies.

```python
class BaseDCAStrategy(ABC):
    def __init__(self, budget_per_period: float, period_days: int):
        self.budget = budget_per_period
        self.period = period_days
        self.accumulated_cash = 0.0

    @abstractmethod
    def should_invest(self, date: datetime, price: float, indicators: dict) -> bool:
        """Return True if investment should be made on this date."""
        pass

    @abstractmethod
    def get_investment_amount(self, date: datetime, available_cash: float) -> float:
        """Return amount to invest. Default is budget + accumulated."""
        pass
```

### 3. BacktestResult
**Type**: Dataclass
**Purpose**: output of a backtest run.

| Field | Type | Description |
|-------|------|-------------|
| `strategy_name` | `str` | Name of strategy tested |
| `total_invested` | `float` | Total cash put into the system |
| `final_value` | `float` | Final portfolio value (assets * price + cash) |
| `total_fees` | `float` | Total fees paid |
| `twr` | `float` | Time-Weighted Return |
| `mwr` | `float` | Money-Weighted Return |
| `max_drawdown` | `float` | Maximum percentage drop from peak |
| `sharpe_ratio` | `float` | Risk-adjusted return metric |
| `history` | `List[Trade]` | List of executed trades |

### 4. Exchange
**Type**: Abstract Base Class (Python)
**Purpose**: Interface for exchange connectors.

```python
class Exchange(ABC):
    @abstractmethod
    async def connect(self):
        """Establish WebSocket connection."""
        pass

    @abstractmethod
    async def subscribe(self, symbols: List[str]):
        """Subscribe to orderbook channels."""
        pass

    @abstractmethod
    async def listen(self) -> AsyncGenerator[StandardizedTick, None]:
        """Yield standardized ticks indefinitely."""
        pass
```
