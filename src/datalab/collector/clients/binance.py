import asyncio
import json
import logging
import time
import aiohttp
from typing import List, AsyncGenerator
from datalab.collector.exchange import Exchange, StandardizedTick

logger = logging.getLogger(__name__)

class BinanceExchange(Exchange):
    WS_BASE_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self, symbols: List[str], api_key: str = None, api_secret: str = None):
        super().__init__("binance", symbols, api_key, api_secret)
        self.session = None
        self.ws = None

    async def connect(self):
        # Binance streams are often part of URL
        # e.g. /ws/btcusdt@depth5
        # But for multi-stream we subscribe after connect
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(self.WS_BASE_URL)
        logger.info("Connected to Binance WebSocket")

    async def subscribe(self, symbols: List[str]):
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        # Convert symbols to binance format (lowercase, no hyphen)
        params = [f"{s.lower().replace('-', '')}@bookTicker" for s in symbols]
        
        msg = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": 1
        }
        await self.ws.send_json(msg)
        logger.info(f"Subscribed to {symbols} on Binance")

    async def listen(self) -> AsyncGenerator[StandardizedTick, None]:
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Handle bookTicker event
                    # {"u":400900217,"s":"BNBBTC","b":"25.35190000","B":"31.21000000","a":"25.36520000","A":"40.66000000"}
                    if "s" in data and "b" in data and "a" in data:
                        bid = float(data["b"])
                        ask = float(data["a"])
                        
                        yield StandardizedTick(
                            timestamp=time.time_ns(),
                            exchange=self.name,
                            symbol=data["s"],
                            bid_price=bid,
                            ask_price=ask,
                            spread_10k=ask - bid, # Placeholder
                            spread_50k=ask - bid,
                            spread_100k=ask - bid,
                            spread_500k=ask - bid,
                            liquidity_bid=float(data["B"]),
                            liquidity_ask=float(data["A"])
                        )
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        except Exception as e:
            logger.error(f"Error in Binance listen: {e}")
        finally:
            if self.session:
                await self.session.close()
