import pytest
import pandas as pd
from datetime import datetime
from datalab.backtest.engine import BacktestEngine, BacktestResult
from datalab.strategy.base import BaseDCAStrategy

class MockStrategy(BaseDCAStrategy):
    def should_invest(self, date, price, indicators):
        return True
    
    def get_investment_amount(self, date, available_cash):
        return 100.0

def test_backtest_simple():
    # Create mock market data
    dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
    data = pd.DataFrame({
        "timestamp": dates,
        "bid_price": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "ask_price": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110] # Buy at ask
    })
    
    strategy = MockStrategy(100.0, 1)
    engine = BacktestEngine(initial_capital=1000.0)
    
    result = engine.run(strategy, data)
    
    assert isinstance(result, BacktestResult)
    assert result.total_invested == 1000.0 # 10 days * 100
    assert len(result.history) == 10
    assert result.final_value > 0
    # Check that new metrics are calculated
    assert result.max_drawdown >= 0
    assert result.volatility >= 0
    assert result.cagr is not None
