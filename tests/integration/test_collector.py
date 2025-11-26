import pytest
import asyncio
import os
import shutil
from unittest.mock import MagicMock, patch, AsyncMock
from datalab.collector.manager import MultiExchangeCollector
from datalab.utils.config import load_config

@pytest.fixture
def data_dir():
    path = "/tmp/test_datalab_integration"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.mark.asyncio
async def test_full_collection_flow(data_dir):
    config = {
        "buffer_size": 5,
        "data_dir": data_dir,
        "exchanges": [
            {
                "name": "dydx",
                "symbols": ["BTC-USD"],
                "api_key": "",
                "api_secret": ""
            }
        ]
    }
    
    collector = MultiExchangeCollector(config)
    
    # Mock the exchange connect/listen to avoid real network
    # We patch the DydxExchange instance in the collector
    dydx = collector.exchanges[0]
    dydx.connect = AsyncMock()
    dydx.subscribe = AsyncMock()
    
    async def mock_listen():
        from datalab.collector.exchange import StandardizedTick
        import time
        for i in range(10):
            yield StandardizedTick(time.time_ns(), "dydx", "BTC-USD", 100, 101, 1, 1, 1, 1, 100, 100)
            await asyncio.sleep(0.01)
            
    dydx.listen = mock_listen
    
    # Run for a bit
    task = asyncio.create_task(collector.start())
    await asyncio.sleep(0.2)
    await collector.stop()
    await task
    
    # Check if data was flushed
    files = os.listdir(data_dir)
    parquet_files = [f for f in files if f.endswith(".parquet")]
    assert len(parquet_files) >= 1

@pytest.mark.asyncio
async def test_simulated_exchange_integration(data_dir):
    config = {
        "buffer_size": 5,
        "data_dir": data_dir,
        "exchanges": [
            {
                "name": "simulated",
                "symbols": ["ETH-USD"]
            }
        ]
    }
    
    collector = MultiExchangeCollector(config)
    
    # No need to mock, SimulatedExchange works autonomously
    
    task = asyncio.create_task(collector.start())
    await asyncio.sleep(0.3)
    await collector.stop()
    await task
    
    files = os.listdir(data_dir)
    parquet_files = [f for f in files if f.endswith(".parquet")]
    assert len(parquet_files) >= 1
