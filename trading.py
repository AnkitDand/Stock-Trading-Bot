from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, SYMBOL

# Initialize Trading Client
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Track position
average_buy_price = None
position_qty = 0
stop_loss_percentage = 0.98  # Sell if price drops below 2% of buy price

async def check_position():
    """Check if we already hold the stock"""
    global average_buy_price, position_qty

    try:
        positions = trading_client.get_all_positions()
        for pos in positions:
            if pos.symbol == SYMBOL:
                position_qty = int(pos.qty)
                average_buy_price = float(pos.avg_entry_price)
                return
        position_qty = 0
        average_buy_price = None
    except Exception as e:
        print(f"⚠️ Error fetching positions: {e}")

async def place_limit_order(symbol, side, market_price, qty=1):
    """Place a limit order at a reasonable price."""
    global average_buy_price, position_qty

    if side == "buy":
        limit_price = round(market_price, 2)
    elif side == "sell":
        limit_price = round(market_price * 1.001, 2)
    else:
        return

    try:
        order = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
            limit_price=limit_price
        )
        trading_client.submit_order(order)
        print(f"✅ Limit {side.upper()} order placed for {qty} {symbol} at ${limit_price:.2f}")

        # Update position tracking
        if side == "buy":
            if position_qty == 0:
                average_buy_price = limit_price
            else:
                average_buy_price = (average_buy_price * position_qty + limit_price * qty) / (position_qty + qty)
            position_qty += qty

        elif side == "sell":
            position_qty -= qty
            if position_qty <= 0:
                average_buy_price = None

    except Exception as e:
        print(f"❌ Order failed: {e}")
