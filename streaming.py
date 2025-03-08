from alpaca.data.live import StockDataStream
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, SYMBOL
from strategy import handle_trade

# Initialize Alpaca WebSocket Client
stream = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# Subscribe to Live Trades
stream.subscribe_trades(handle_trade, SYMBOL)

async def start_stream():
    """Start real-time data streaming"""
    await stream._run_forever()
