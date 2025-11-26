from dataclasses import dataclass, field
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datalab.strategy.base import BaseDCAStrategy

@dataclass
class Trade:
    date: pd.Timestamp
    amount: float
    price: float
    fee: float
    asset_amount: float

@dataclass
class BacktestResult:
    strategy_name: str
    total_invested: float
    final_value: float
    total_fees: float
    net_profit: float
    return_pct: float
    cagr: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    win_rate: float
    best_day: float
    worst_day: float
    value_at_risk: float
    history: List[Trade]
    daily_values: List[float] = field(default_factory=list)

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, commission_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate

    def run(self, strategy: BaseDCAStrategy, data: pd.DataFrame) -> BacktestResult:
        cash = self.initial_capital
        holdings = 0.0
        total_invested = 0.0
        total_fees = 0.0
        history = []
        portfolio_values = []
        
        # Ensure sorting
        if 'timestamp' not in data.columns:
             if isinstance(data.index, pd.DatetimeIndex):
                 data = data.reset_index().rename(columns={"index": "timestamp"})
             else:
                 raise ValueError("Data must have timestamp column")
                 
        data = data.sort_values("timestamp")
        
        for _, row in data.iterrows():
            date = row["timestamp"]
            price = row["ask_price"] # Buy price
            
            # Strategy Decision
            indicators = {} 
            
            if strategy.should_invest(date, price, indicators):
                amount = strategy.get_investment_amount(date, cash)
                if amount > 0 and cash >= amount:
                    fee = amount * self.commission_rate
                    net_amount = amount - fee
                    asset_bought = net_amount / price
                    
                    cash -= amount
                    holdings += asset_bought
                    total_invested += amount
                    total_fees += fee
                    
                    history.append(Trade(date, amount, price, fee, asset_bought))
            
            # Mark to market
            valuation_price = row["bid_price"]
            current_val = cash + (holdings * valuation_price)
            portfolio_values.append(current_val)

        final_value = portfolio_values[-1] if portfolio_values else self.initial_capital
        net_profit = final_value - self.initial_capital
        return_pct = (net_profit / self.initial_capital) * 100.0
        
        # Metrics Calculation
        series = pd.Series(portfolio_values)
        returns = series.pct_change().dropna()
        
        days = (data["timestamp"].iloc[-1] - data["timestamp"].iloc[0]).days
        years = days / 365.25 if days > 0 else 0

        # CAGR
        if years > 0 and final_value > 0 and self.initial_capital > 0:
            cagr = (final_value / self.initial_capital) ** (1 / years) - 1
        else:
            cagr = 0.0

        # Volatility (Annualized)
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.0

        # Max Drawdown
        max_dd = self._compute_drawdown(portfolio_values)

        # Sharpe Ratio (Risk Free Rate assumed 0 for simplicity)
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0.0

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino = (returns.mean() * 252) / downside_std if downside_std != 0 else 0.0

        # Calmar Ratio
        calmar = (cagr / max_dd) if max_dd > 0 else 0.0

        # Win Rate (Daily)
        win_rate = (len(returns[returns > 0]) / len(returns)) * 100 if len(returns) > 0 else 0.0

        # Best/Worst Day
        best_day = returns.max() * 100 if len(returns) > 0 else 0.0
        worst_day = returns.min() * 100 if len(returns) > 0 else 0.0
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5) * 100 if len(returns) > 0 else 0.0

        return BacktestResult(
            strategy_name=strategy.__class__.__name__,
            total_invested=total_invested,
            final_value=final_value,
            total_fees=total_fees,
            net_profit=net_profit,
            return_pct=return_pct,
            cagr=cagr * 100,
            volatility=volatility * 100,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            max_drawdown=max_dd * 100,
            win_rate=win_rate,
            best_day=best_day,
            worst_day=worst_day,
            value_at_risk=var_95,
            history=history,
            daily_values=portfolio_values
        )

    def _compute_drawdown(self, values: List[float]) -> float:
        if not values: return 0.0
        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd
