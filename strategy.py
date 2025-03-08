import pandas as pd
from trading import check_position, place_limit_order, average_buy_price, position_qty, stop_loss_percentage
from config import SYMBOL

price_history = []

def calculate_macd(prices):
    """Calculate MACD and Signal Line for price history."""
    df = pd.DataFrame(prices, columns=["close"])
    df["12EMA"] = df["close"].ewm(span=12, adjust=False).mean()
    df["26EMA"] = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["12EMA"] - df["26EMA"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

async def handle_trade(data):
    """Handles real-time trade data."""
    global average_buy_price, position_qty

    latest_price = data.price
    price_history.append(latest_price)

    # Keep last 50 prices
    if len(price_history) > 50:
        price_history.pop(0)

    if len(price_history) >= 26:
        df = calculate_macd(price_history)

        macd, prev_macd = df.iloc[-1]["MACD"], df.iloc[-2]["MACD"]
        signal, prev_signal = df.iloc[-1]["Signal"], df.iloc[-2]["Signal"]

        macd_crossover_up = prev_macd < prev_signal and macd > signal  # Bullish
        macd_crossover_down = prev_macd > prev_signal and macd < signal  # Bearish

        await check_position()

        # BUY if MACD crosses Signal line upwards
        if macd_crossover_up:
            print(f"✅ BUY at ${latest_price:.2f} (MACD crossover)")
            await place_limit_order(SYMBOL, "buy", latest_price)

        # SELL if MACD crosses down or stop-loss triggers
        elif macd_crossover_down and position_qty > 0:
            if latest_price > average_buy_price:
                print(f"✅ SELL at profit: ${latest_price:.2f} (Bought at ${average_buy_price:.2f})")
                await place_limit_order(SYMBOL, "sell", latest_price)
            
            elif latest_price < average_buy_price * stop_loss_percentage:
                print(f"⚠️ STOP-LOSS SELL at ${latest_price:.2f} (Bought at ${average_buy_price:.2f})")
                await place_limit_order(SYMBOL, "sell", latest_price)
