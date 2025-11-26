import asyncio
import time
import random
from typing import List, AsyncGenerator
from datalab.collector.exchange import Exchange, StandardizedTick

class SimulatedExchange(Exchange):
    """
    Generates random market data for testing.
    """
    def __init__(self, symbols: List[str], api_key: str = None, api_secret: str = None):
        super().__init__("simulated", symbols, api_key, api_secret)

    async def connect(self):
        pass

    async def subscribe(self, symbols: List[str]):
        pass

    async def listen(self) -> AsyncGenerator[StandardizedTick, None]:
        while True:
            for symbol in self.symbols:
                price = 100.0 + random.random() * 10
                spread = random.random() * 0.5
                
                yield StandardizedTick(
                    timestamp=time.time_ns(),
                    exchange=self.name,
                    symbol=symbol,
                    bid_price=price,
                    ask_price=price + spread,
                    spread_10k=spread,
                    spread_50k=spread * 1.1,
                    spread_100k=spread * 1.2,
                    spread_500k=spread * 1.5,
                    liquidity_bid=1000000.0,
                    liquidity_ask=1000000.0
                )
            await asyncio.sleep(0.1) # 100ms
