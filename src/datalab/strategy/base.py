from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

class BaseDCAStrategy(ABC):
    """
    Interface for implementing investment strategies.
    """
    def __init__(self, budget_per_period: float, period_days: int):
        self.budget = budget_per_period
        self.period = period_days
        self.accumulated_cash = 0.0

    @abstractmethod
    def should_invest(self, date: datetime, price: float, indicators: Dict[str, Any]) -> bool:
        """Return True if investment should be made on this date."""
        pass

    @abstractmethod
    def get_investment_amount(self, date: datetime, available_cash: float) -> float:
        """Return amount to invest. Default is budget + accumulated."""
        # Default implementation can be provided or left abstract.
        # Based on spec: "Default is budget + accumulated"
        pass
