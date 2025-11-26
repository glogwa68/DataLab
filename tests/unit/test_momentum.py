import pytest
from datetime import datetime, timedelta
from datalab.strategy.library.momentum import MomentumDCA

def test_momentum_logic():
    strategy = MomentumDCA(100.0, 1, sma_period=3)
    
    start = datetime(2023, 1, 1)
    
    # 1. Not enough data (need 3)
    assert strategy.should_invest(start, 100, {}) is False
    assert strategy.should_invest(start + timedelta(days=1), 100, {}) is False
    
    # 2. Enough data, Price (110) > SMA(100, 100, 110) = 103.3 -> True
    assert strategy.should_invest(start + timedelta(days=2), 110, {}) is True
    
    # 3. Next day, period constraint passed (1 day), Price (90)
    # History: 100, 110, 90. SMA = 100. Price (90) < SMA (100) -> False
    assert strategy.should_invest(start + timedelta(days=3), 90, {}) is False
