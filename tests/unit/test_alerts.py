import pytest
from unittest.mock import MagicMock
from datalab.collector.manager import MultiExchangeCollector
from datalab.collector.exchange import StandardizedTick

@pytest.mark.asyncio
async def test_alert_threshold():
    config = {"buffer_size": 10, "spread_threshold": 5.0}
    collector = MultiExchangeCollector(config)
    
    # Mock logger to verify alert
    # In implementation, we might use a specific AlertService, but for now check if it logs or calls a method
    # We can spy on a '_send_alert' method we'll add
    collector._send_alert = MagicMock()
    
    # Tick with spread 1.0 (Low)
    tick_low = StandardizedTick(1, "ex", "sym", 100, 101, 1.0, 1, 1, 1, 100, 100)
    await collector._process_tick(tick_low)
    collector._send_alert.assert_not_called()
    
    # Tick with spread 10.0 (High)
    tick_high = StandardizedTick(2, "ex", "sym", 100, 110, 10.0, 1, 1, 1, 100, 100)
    await collector._process_tick(tick_high)
    collector._send_alert.assert_called_once()
