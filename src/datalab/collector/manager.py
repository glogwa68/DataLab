import asyncio
import logging
from collections import deque
from typing import Dict, Any, List
from datalab.collector.exchange import Exchange, StandardizedTick
from datalab.collector.clients.dydx import DydxExchange
from datalab.collector.clients.binance import BinanceExchange
from datalab.collector.clients.hyperliquid import SimulatedExchange
from datalab.utils.storage import save_to_parquet, get_timestamped_filename
import os

logger = logging.getLogger(__name__)

class MultiExchangeCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.buffer_size = config.get("buffer_size", 100000)
        self.data_dir = config.get("data_dir", "./data")
        self.spread_threshold = config.get("spread_threshold", 0.0)
        self.buffer: deque = deque(maxlen=self.buffer_size)
        self.exchanges: List[Exchange] = []
        self._running = False
        
        self._init_exchanges()

    def _init_exchanges(self):
        ex_configs = self.config.get("exchanges", [])
        for ex_conf in ex_configs:
            name = ex_conf.get("name")
            symbols = ex_conf.get("symbols", [])
            api_key = ex_conf.get("api_key")
            api_secret = ex_conf.get("api_secret")
            
            if name == "dydx":
                self.exchanges.append(DydxExchange(symbols, api_key, api_secret))
            elif name == "binance":
                self.exchanges.append(BinanceExchange(symbols, api_key, api_secret))
            elif name == "simulated" or name == "hyperliquid":
                self.exchanges.append(SimulatedExchange(symbols, api_key, api_secret))
            else:
                logger.warning(f"Unknown exchange: {name}")

    async def start(self):
        self._running = True
        tasks = []
        for ex in self.exchanges:
            tasks.append(self._run_exchange(ex))
            
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_exchange(self, exchange: Exchange):
        while self._running:
            try:
                await exchange.connect()
                await exchange.subscribe(exchange.symbols)
                async for tick in exchange.listen():
                    if not self._running:
                        break
                    await self._process_tick(tick)
            except Exception as e:
                logger.error(f"Error in exchange {exchange.name}: {e}")
                await asyncio.sleep(5) # Backoff

    async def _process_tick(self, tick: StandardizedTick):
        # Check alerts
        if self.spread_threshold > 0 and tick.spread_10k > self.spread_threshold:
            self._send_alert(tick)

        self.buffer.append(tick)
        if len(self.buffer) >= self.buffer_size:
            await self._flush_buffer()
            
    def _send_alert(self, tick: StandardizedTick):
        logger.warning(f"ALERT: High Spread detected on {tick.exchange} {tick.symbol}: {tick.spread_10k}")

    async def _flush_buffer(self):
        if not self.buffer:
            return
            
        ticks = list(self.buffer)
        self.buffer.clear()
        
        filename = get_timestamped_filename()
        filepath = os.path.join(self.data_dir, filename)
        
        # Offload blocking I/O to thread
        await asyncio.to_thread(save_to_parquet, ticks, filepath)
        logger.info(f"Flushed {len(ticks)} ticks to {filepath}")

    async def stop(self):
        self._running = False
        await self._flush_buffer()
