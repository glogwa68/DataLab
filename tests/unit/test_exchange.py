import pytest
from datalab.collector.exchange import Exchange, StandardizedTick
from typing import List, AsyncGenerator
import asyncio
import time

class MockExchange(Exchange):
    async def connect(self):
        pass

    async def subscribe(self, symbols: List[str]):
        pass

    async def listen(self) -> AsyncGenerator[StandardizedTick, None]:
        # Yield 3 ticks
        for i in range(3):
            yield StandardizedTick(
                timestamp=time.time_ns(),
                exchange=self.name,
                symbol=self.symbols[0],
                bid_price=100.0 + i,
                ask_price=101.0 + i,
                spread_10k=1.0,
                spread_50k=1.1,
                spread_100k=1.2,
                spread_500k=1.5,
                liquidity_bid=1000000,
                liquidity_ask=1000000
            )
            await asyncio.sleep(0.01)

@pytest.mark.asyncio
async def test_exchange_contract():
    exchange = MockExchange("mock", ["BTC-USD"])
    await exchange.connect()
    await exchange.subscribe(["BTC-USD"])
    
    ticks = []
    async for tick in exchange.listen():
        ticks.append(tick)
        
    assert len(ticks) == 3
    assert ticks[0].exchange == "mock"
    assert ticks[0].symbol == "BTC-USD"
    assert ticks[0].bid_price == 100.0
