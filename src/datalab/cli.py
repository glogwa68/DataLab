import argparse
import sys
from datalab.utils.config import load_config

import asyncio
import logging
from datalab.collector.manager import MultiExchangeCollector

logging.basicConfig(level=logging.ERROR)

def collect_command(args):
    config = load_config(args.config)
    # Use 'collector' section if present, else assume root (based on schema it's under 'collector')
    collector_config = config.get("collector", config)
    
    if args.spread_threshold:
        collector_config["spread_threshold"] = args.spread_threshold
    
    collector = MultiExchangeCollector(collector_config)
    
    try:
        asyncio.run(collector.start())
    except KeyboardInterrupt:
        # Run stop logic
        asyncio.run(collector.stop())

from datalab.strategy.library.dca import PeriodicDCA
from datalab.backtest.engine import BacktestEngine
import pandas as pd
from datetime import datetime

from datalab.analysis.plotting import plot_backtest_results

def backtest_command(args):
    print(f"Starting backtest: Strategy={args.strategy}, Asset={args.asset}, Range={args.start} to {args.end}")
    
    # TODO: Load real data
    # For MVP/Prototype, generate dummy data if no file found
    dates = pd.date_range(start=args.start, end=args.end, freq="D")
    data = pd.DataFrame({
        "timestamp": dates,
        "bid_price": [100.0] * len(dates),
        "ask_price": [101.0] * len(dates)
    })
    
    if args.strategy == "dca_daily":
        strategy = PeriodicDCA(100.0, 1)
    elif args.strategy == "dca_weekly":
        strategy = PeriodicDCA(100.0, 7)
    else:
        strategy = PeriodicDCA(100.0, 30) # Default monthly
        
    engine = BacktestEngine()
    result = engine.run(strategy, data)
    
    print("\n=== Backtest Results ===")
    print(f"Strategy:       {result.strategy_name}")
    print(f"Total Invested: ${result.total_invested:,.2f}")
    print(f"Final Value:    ${result.final_value:,.2f}")
    print(f"Net Profit:     ${result.net_profit:,.2f} ({result.return_pct:.2f}%)")
    print(f"CAGR:           {result.cagr:.2f}%")
    print("-" * 24)
    print(f"Volatility:     {result.volatility:.2f}%")
    print(f"Max Drawdown:   {result.max_drawdown:.2f}%")
    print(f"Sharpe Ratio:   {result.sharpe_ratio:.2f}")
    print(f"Sortino Ratio:  {result.sortino_ratio:.2f}")
    print(f"Calmar Ratio:   {result.calmar_ratio:.2f}")
    print("-" * 24)
    print(f"Win Rate:       {result.win_rate:.2f}%")
    print(f"Best Day:       {result.best_day:.2f}%")
    print(f"Worst Day:      {result.worst_day:.2f}%")
    print(f"VaR (95%):      {result.value_at_risk:.2f}%")
    print(f"Trades:         {len(result.history)}")
    
    # Generate Report
    report_path = f"backtest_report_{args.strategy}_{args.start}_{args.end}.html"
    plot_backtest_results(result, report_path)
    print(f"\nDetailed HTML report generated: {report_path}")

from datalab.analysis.plotting import plot_spreads
import os

def analyze_command(args):
    print(f"Starting analysis: Input={args.input}, Output={args.output}")
    
    if os.path.isdir(args.input) or os.path.isfile(args.input):
        # Load all parquet files
        # For MVP, simplified loading
        try:
            df = pd.read_parquet(args.input)
            # Ensure timestamp is datetime for plotting
            if df['timestamp'].dtype == 'int64':
                # Convert ns to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
                
            plot_spreads(df, args.output)
            print(f"Report generated at {args.output}")
        except Exception as e:
            print(f"Error loading data: {e}")
    else:
        print(f"Input path not found: {args.input}")

def main():
    parser = argparse.ArgumentParser(description="DataLab Financial Analysis Platform")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Collect Command
    collect_parser = subparsers.add_parser("collect", help="Start data collection")
    collect_parser.add_argument("--config", required=True, help="Path to configuration JSON")
    collect_parser.add_argument("--spread-threshold", type=float, help="Alert threshold for spread")
    collect_parser.set_defaults(func=collect_command)

    # Backtest Command
    backtest_parser = subparsers.add_parser("backtest", help="Run strategy backtest")
    backtest_parser.add_argument("--strategy", required=True, help="Strategy name")
    backtest_parser.add_argument("--asset", required=True, help="Asset symbol (e.g. BTC-USD)")
    backtest_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    backtest_parser.set_defaults(func=backtest_command)

    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze collected data")
    analyze_parser.add_argument("--input", required=True, help="Input directory or file")
    analyze_parser.add_argument("--output", required=True, help="Output report path")
    analyze_parser.set_defaults(func=analyze_command)

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)

if __name__ == "__main__":
    main()
