from flask import Flask, render_template_string, request, jsonify
import requests
import threading
import time
import random

app = Flask(__name__)

# Strategy Configuration
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

# Fetch price from CoinGecko
def fetch_price(symbol):
    symbol_map = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum",
        "BNBUSDT": "binancecoin"
    }
    coingecko_id = symbol_map.get(symbol)
    if not coingecko_id:
        print(f"[fetch_price] Unknown symbol: {symbol}")
        return None

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        print(f"[fetch_price] API raw response for {symbol}: {data}")
        coin_data = data.get(coingecko_id, {})
        price = coin_data.get("usd")
        if price is not None:
            print(f"[fetch_price] {symbol} => {price}")
            return float(price)
        else:
            print(f"[fetch_price] No 'usd' key for {symbol}")
            return None
    except Exception as e:
        print(f"[fetch_price] Error for {symbol}: {e}")
        return None

# Analyze price to decide signal
def analyze_symbol(symbol):
    price = fetch_price(symbol)
    if price is None:
        print(f"[analyze_symbol] Skipping {symbol}, no price.")
        return None

    change = random.uniform(-2, 2)
    print(f"[analyze_symbol] {symbol} change: {change}")

    if change <= strategy["BUY_THRESHOLD"]:
        action = "BUY"
    elif change >= strategy["SELL_THRESHOLD"]:
        action = "SELL"
    else:
        action = "HOLD"

    return {"symbol": symbol, "price": price, "action": action}

# Periodically update tracked prices
def watch_prices():
    print("🔄 Running price check...")
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    results = []
    for sym in symbols:
        result = analyze_symbol(sym)
        print(f"[Watcher] {sym} => {result}")
        if result:
            results.append(result)
    strategy["TRACKED_SYMBOLS"] = results
    threading.Timer(10, watch_prices).start()

# HTML Template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Dashboard</title>
</head>
<body>
    <h2>📊 Trading Bot Strategy</h2>
    <form method="POST">
        <label>BUY_THRESHOLD (%):</label><br>
        <input name="BUY_THRESHOLD" value="{{ s.BUY_THRESHOLD }}"><br>
        <label>SELL_THRESHOLD (%):</label><br>
        <input name="SELL_THRESHOLD" value="{{ s.SELL_THRESHOLD }}"><br>
        <label>TAKE_PROFIT (%):</label><br>
        <input name="TAKE_PROFIT" value="{{ s.TAKE_PROFIT }}"><br>
        <label>STOP_LOSS (%):</label><br>
        <input name="STOP_LOSS" value="{{ s.STOP_LOSS }}"><br><br>
        <input type="submit" value="✅ Update Strategy">
    </form>

    <h3>📉 Live Coin Signals</h3>
    <table border="1">
        <tr><th>Symbol</th><th>Price</th><th>Action</th></tr>
        {% for signal in s.TRACKED_SYMBOLS %}
        <tr>
            <td>{{ signal.symbol }}</td>
            <td>{{ signal.price }}</td>
            <td>{{ signal.action }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        strategy["BUY_THRESHOLD"] = float(request.form["BUY_THRESHOLD"])
        strategy["SELL_THRESHOLD"] = float(request.form["SELL_THRESHOLD"])
        strategy["TAKE_PROFIT"] = float(request.form["TAKE_PROFIT"])
        strategy["STOP_LOSS"] = float(request.form["STOP_LOSS"])
        print("[Strategy Updated]", strategy)

    return render_template_string(HTML, s=strategy)

@app.route("/data")
def data():
    return jsonify(strategy["TRACKED_SYMBOLS"])

if __name__ == "__main__":
    watch_prices()
    app.run(host="0.0.0.0", port=10000)
