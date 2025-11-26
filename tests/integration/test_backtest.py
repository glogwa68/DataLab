import pytest
import pandas as pd
from datalab.backtest.engine import BacktestEngine
from datalab.strategy.library.dca import PeriodicDCA

def test_backtest_integration():
    # 1. Setup Data
    dates = pd.date_range(start="2023-01-01", end="2023-01-31", freq="D") # 31 days
    data = pd.DataFrame({
        "timestamp": dates,
        "bid_price": [100.0] * 31,
        "ask_price": [100.0] * 31
    })
    
    # 2. Setup Strategy (Daily DCA)
    strategy = PeriodicDCA(budget_per_period=10.0, period_days=1)
    
    # 3. Run Engine
    engine = BacktestEngine(initial_capital=1000.0, commission_rate=0.0)
    result = engine.run(strategy, data)
    
    # 4. Verify
    # Should invest every day (31 times) -> 310.0 invested
    assert len(result.history) == 31
    assert result.total_invested == 310.0
    
    # Final value should be remaining cash + asset value
    # Cash = 1000 - 310 = 690
    # Assets = 310 / 100 = 3.1 units
    # Value = 690 + (3.1 * 100) = 1000
    assert result.final_value == pytest.approx(1000.0)
    assert result.net_profit == pytest.approx(0.0) # No price change, so no profit
    assert result.cagr == pytest.approx(0.0, abs=1e-9)
