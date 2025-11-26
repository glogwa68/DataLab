import asyncio
import json
import logging
import time
import aiohttp
from typing import List, AsyncGenerator
from datalab.collector.exchange import Exchange, StandardizedTick

logger = logging.getLogger(__name__)

class DydxExchange(Exchange):
    WS_URL = "wss://api.dydx.exchange/v3/ws"

    def __init__(self, symbols: List[str], api_key: str = None, api_secret: str = None):
        super().__init__("dydx", symbols, api_key, api_secret)
        self.session = None
        self.ws = None

    async def connect(self):
        self.session = aiohttp.ClientSession()
        try:
            self.ws = await self.session.ws_connect(self.WS_URL)
            logger.info("Connected to dYdX WebSocket")
        except Exception as e:
            logger.error(f"Failed to connect to dYdX: {e}")
            raise

    async def subscribe(self, symbols: List[str]):
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        for symbol in symbols:
            # dYdX v3 subscription message
            msg = {
                "type": "subscribe",
                "channel": "v3_orderbook",
                "id": symbol,
                "includeOffsets": True
            }
            await self.ws.send_json(msg)
            logger.info(f"Subscribed to {symbol} on dYdX")

    async def listen(self) -> AsyncGenerator[StandardizedTick, None]:
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "channel_data":
                        # Parse orderbook data
                        # This is simplified for prototype
                        contents = data.get("contents", {})
                        bids = contents.get("bids", [])
                        asks = contents.get("asks", [])
                        
                        if bids and asks:
                            bid_price = float(bids[0]["price"])
                            ask_price = float(asks[0]["price"])
                            
                            yield StandardizedTick(
                                timestamp=time.time_ns(),
                                exchange=self.name,
                                symbol=data.get("id", "unknown"),
                                bid_price=bid_price,
                                ask_price=ask_price,
                                spread_10k=abs(ask_price - bid_price), # Placeholder calculation
                                spread_50k=abs(ask_price - bid_price),
                                spread_100k=abs(ask_price - bid_price),
                                spread_500k=abs(ask_price - bid_price),
                                liquidity_bid=100000.0, # Placeholder
                                liquidity_ask=100000.0
                            )
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error("WebSocket connection closed with error")
                    break
        except Exception as e:
            logger.error(f"Error in dYdX listen: {e}")
        finally:
            if self.session:
                await self.session.close()
