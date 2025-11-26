from datalab.strategy.base import BaseDCAStrategy
from datetime import datetime, timedelta

class PeriodicDCA(BaseDCAStrategy):
    """
    Invests a fixed budget every N days.
    """
    def __init__(self, budget_per_period: float, period_days: int):
        super().__init__(budget_per_period, period_days)
        self.last_invest_date = None

    def should_invest(self, date: datetime, price: float, indicators: dict) -> bool:
        if self.last_invest_date is None:
            self.last_invest_date = date
            return True
        
        if (date - self.last_invest_date).days >= self.period:
            self.last_invest_date = date
            return True
            
        return False

    def get_investment_amount(self, date: datetime, available_cash: float) -> float:
        # Try to invest budget, capped by available
        return min(self.budget, available_cash)
