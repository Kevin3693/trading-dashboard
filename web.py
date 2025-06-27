import time
import requests

def fetch_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        res = requests.get(url, timeout=5)
        return float(res.json()["price"])
    except:
        return None

def analyze_symbol(symbol):
    price = fetch_price(symbol)
    if price is None:
        return None

    # Dummy % change for simulation (replace with real logic later)
    change = round((price % 10 - 5) / 5 * 100, 2)  # Simulates ±100% change

    if change <= strategy["BUY_THRESHOLD"]:
        action = "BUY"
    elif change >= strategy["SELL_THRESHOLD"]:
        action = "SELL"
    else:
        action = "HOLD"

    return {"symbol": symbol, "price": price, "action": action}

def start_price_watcher():
    def run():
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        while True:
            results = []
            for sym in symbols:
                result = analyze_symbol(sym)
                if result:
                    results.append(result)
            strategy["TRACKED_SYMBOLS"] = results
            time.sleep(10)

    threading.Thread(target=run, daemon=True).start()

start_price_watcher()
