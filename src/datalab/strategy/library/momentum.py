from datalab.strategy.base import BaseDCAStrategy
from datetime import datetime
from collections import deque
import numpy as np

class MomentumDCA(BaseDCAStrategy):
    """
    Invests only when price is above N-day SMA.
    """
    def __init__(self, budget_per_period: float, period_days: int, sma_period: int = 10):
        super().__init__(budget_per_period, period_days)
        self.sma_period = sma_period
        self.prices = deque(maxlen=sma_period)
        self.last_invest_date = None

    def should_invest(self, date: datetime, price: float, indicators: dict) -> bool:
        self.prices.append(price)
        
        # Need full history for SMA
        if len(self.prices) < self.sma_period:
            return False
            
        sma = np.mean(self.prices)
        
        # Momentum condition: Price > SMA
        if price > sma:
            # Also respect period
            if self.last_invest_date is None:
                self.last_invest_date = date
                return True
            
            if (date - self.last_invest_date).days >= self.period:
                self.last_invest_date = date
                return True
                
        return False

    def get_investment_amount(self, date: datetime, available_cash: float) -> float:
        return min(self.budget, available_cash)
