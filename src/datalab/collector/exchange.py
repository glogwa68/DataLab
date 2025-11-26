from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, AsyncGenerator, Dict, Optional

@dataclass(frozen=True)
class StandardizedTick:
    """
    Represents a normalized snapshot of market state from any exchange.
    """
    timestamp: int  # Unix timestamp of receipt (nanoseconds)
    exchange: str   # Normalized exchange name
    symbol: str     # Normalized symbol pair
    bid_price: float
    ask_price: float
    spread_10k: float
    spread_50k: float
    spread_100k: float
    spread_500k: float
    liquidity_bid: float
    liquidity_ask: float
    
    # Optional metadata for debugging/latency tracking
    latency_ms: Optional[float] = None

class Exchange(ABC):
    """
    Interface for exchange connectors.
    """
    
    def __init__(self, name: str, symbols: List[str], api_key: str = None, api_secret: str = None):
        self.name = name
        self.symbols = symbols
        self.api_key = api_key
        self.api_secret = api_secret

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
