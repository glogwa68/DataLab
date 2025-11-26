import pytest
import asyncio
from collections import deque
from datalab.collector.manager import MultiExchangeCollector
from datalab.collector.exchange import StandardizedTick, Exchange

class MockExchange(Exchange):
    async def connect(self): pass
    async def subscribe(self, s): pass
    async def listen(self):
        yield StandardizedTick(0, "mock", "BTC", 100, 101, 1, 1, 1, 1, 100, 100)

@pytest.mark.asyncio
async def test_collector_buffering():
    # Setup
    config = {
        "buffer_size": 10,
        "exchanges": [],
        "data_dir": "/tmp/test"
    }
    collector = MultiExchangeCollector(config)
    
    # Inject mock exchange
    mock_ex = MockExchange("mock", ["BTC"])
    collector.exchanges.append(mock_ex)
    
    # Manually trigger processing of one tick (simulated)
    tick = StandardizedTick(123, "mock", "BTC", 100, 101, 1, 1, 1, 1, 100, 100)
    await collector._process_tick(tick)
    
    assert len(collector.buffer) == 1
    assert collector.buffer[0] == tick

@pytest.mark.asyncio
async def test_collector_flush():
    config = {"buffer_size": 2, "data_dir": "/tmp/test"} # Low buffer for flush
    collector = MultiExchangeCollector(config)
    
    tick1 = StandardizedTick(1, "mock", "BTC", 100, 101, 1, 1, 1, 1, 100, 100)
    tick2 = StandardizedTick(2, "mock", "BTC", 100, 101, 1, 1, 1, 1, 100, 100)
    
    # Should not flush yet
    await collector._process_tick(tick1)
    assert len(collector.buffer) == 1
    
    # Should flush now (buffer_size=2 reached? or after? Usually >= size)
    # Implementation detail: if len >= size -> flush
    # We'll mock the storage save function to verify
    
    called = False
    async def mock_flush():
        nonlocal called
        called = True
        collector.buffer.clear()

    collector._flush_buffer = mock_flush
    
    await collector._process_tick(tick2)
    
    assert called
    assert len(collector.buffer) == 0
