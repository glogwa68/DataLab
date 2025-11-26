import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datalab.backtest.engine import BacktestResult

def plot_backtest_results(result: BacktestResult, output_path: str):
    """
    Generate interactive HTML report for backtest results with comprehensive statistics.
    """
    # Create layout with 3 rows: Metrics Table, Portfolio Value, Drawdown
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        row_heights=[0.2, 0.5, 0.3],
        specs=[[{"type": "table"}], [{"type": "xy"}], [{"type": "xy"}]],
        subplot_titles=("Performance Metrics", "Portfolio Value", "Drawdown")
    )

    # --- Row 1: Metrics Table ---
    # Format metrics for display
    metrics = [
        ["Total Invested", f"${result.total_invested:,.2f}"],
        ["Final Value", f"${result.final_value:,.2f}"],
        ["Net Profit", f"${result.net_profit:,.2f} ({result.return_pct:.2f}%)"],
        ["CAGR", f"{result.cagr:.2f}%"],
        ["Volatility (Ann.)", f"{result.volatility:.2f}%"],
        ["Max Drawdown", f"{result.max_drawdown:.2f}%"],
        ["Sharpe Ratio", f"{result.sharpe_ratio:.2f}"],
        ["Sortino Ratio", f"{result.sortino_ratio:.2f}"],
        ["Calmar Ratio", f"{result.calmar_ratio:.2f}"],
        ["Win Rate", f"{result.win_rate:.2f}%"],
        ["Best Day", f"{result.best_day:.2f}%"],
        ["Worst Day", f"{result.worst_day:.2f}%"],
        ["VaR (95%)", f"{result.value_at_risk:.2f}%"],
        ["Total Trades", f"{len(result.history)}"]
    ]
    
    # Split into columns for compactness (2 columns of metrics)
    mid = (len(metrics) + 1) // 2
    col1 = metrics[:mid]
    col2 = metrics[mid:]
    
    # Add empty rows to balance if needed
    if len(col2) < len(col1):
        col2.append(["", ""])

    headers = ["Metric", "Value", "Metric", "Value"]
    cells_matrix = [[], [], [], []]
    
    for i in range(len(col1)):
        cells_matrix[0].append(col1[i][0])
        cells_matrix[1].append(col1[i][1])
        cells_matrix[2].append(col2[i][0])
        cells_matrix[3].append(col2[i][1])

    fig.add_trace(
        go.Table(
            header=dict(
                values=headers,
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=cells_matrix,
                fill_color='lavender',
                align='left'
            )
        ),
        row=1, col=1
    )

    # --- Row 2: Portfolio Value ---
    fig.add_trace(
        go.Scatter(y=result.daily_values, mode='lines', name='Portfolio Value', line=dict(color='blue')), 
        row=2, col=1
    )
    
    # --- Row 3: Drawdown ---
    # Recompute drawdown series for plotting
    values = pd.Series(result.daily_values)
    peak = values.cummax()
    drawdown = (values - peak) / peak
    
    fig.add_trace(
        go.Scatter(y=drawdown, mode='lines', name='Drawdown', fill='tozeroy', line=dict(color='red')), 
        row=3, col=1
    )

    # --- Layout Polish ---
    fig.update_layout(
        height=1000, 
        title_text=f"Backtest Report: {result.strategy_name}",
        showlegend=False
    )
    
    # Update axes titles
    fig.update_yaxes(title_text="Value ($)", row=2, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1, tickformat=".1%")

    fig.write_html(output_path)

def plot_spreads(data: pd.DataFrame, output_path: str):
    """
    Plot spread comparison.
    """
    fig = go.Figure()
    
    for exchange in data['exchange'].unique():
        subset = data[data['exchange'] == exchange]
        fig.add_trace(go.Scatter(x=subset['timestamp'], y=subset['spread_10k'], mode='lines', name=f"{exchange} 10k Spread"))

    fig.update_layout(title="Spread Comparison", xaxis_title="Time", yaxis_title="Spread")
    fig.write_html(output_path)