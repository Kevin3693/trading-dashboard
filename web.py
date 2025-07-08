from flask import Flask, render_template_string, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Strategy Configuration
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

# Fetch current price from Binance
def fetch_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        res = requests.get(url, timeout=5)
        price = float(res.json()["price"])
        print(f"[fetch_price] {symbol} => {price}")
        return price
    except Exception as e:
        print(f"[fetch_price] Error for {symbol}: {e}")
        return None

# Analyze price to decide signal
def analyze_symbol(symbol):
    price = fetch_price(symbol)
    if price is None:
        return None

    # Simulate a fake percentage change just for UI testing
    change = round((price % 10 - 5) / 5 * 100, 2)  # returns between -100 to +100

    if change <= strategy["BUY_THRESHOLD"]:
        action = "BUY"
    elif change >= strategy["SELL_THRESHOLD"]:
        action = "SELL"
    else:
        action = "HOLD"  # ensure something is always returned

    return {"symbol": symbol, "price": price, "action": action}

# Background thread to check prices every 10 seconds
def start_price_watcher():
    def run():
        print("🔄 Starting price watcher thread...")
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        while True:
            results = []
            for sym in symbols:
                result = analyze_symbol(sym)
                print(f"[Watcher] {sym} => {result}")
                if result:
                    results.append(result)
            strategy["TRACKED_SYMBOLS"] = results
            time.sleep(10)

    threading.Thread(target=run, daemon=True).start()

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
    start_price_watcher()
    app.run(host="0.0.0.0", port=10000)
