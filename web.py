from flask import Flask, render_template_string, request, jsonify
import requests, threading, time, random

app = Flask(__name__)

# Strategy Configuration
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

# --- Use CoinGecko for public price data ---
def fetch_price(symbol):
    coingecko_ids = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum",
        "BNBUSDT": "binancecoin"
    }
    try:
        coin_id = coingecko_ids[symbol]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url, timeout=5)
        price = res.json()[coin_id]["usd"]
        print(f"[fetch_price] {symbol} => {price}")
        return price
    except Exception as e:
        print(f"[fetch_price] Error for {symbol}: {e}")
        return None

def analyze_symbol(symbol):
    price = fetch_price(symbol)
    if price is None:
        print(f"[analyze_symbol] Skipping {symbol}, no price.")
        return None

    change = random.uniform(-2, 2)  # simulate % change
    print(f"[analyze_symbol] {symbol} change: {change:.2f}%")

    if change <= strategy["BUY_THRESHOLD"]:
        action = "BUY"
    elif change >= strategy["SELL_THRESHOLD"]:
        action = "SELL"
    else:
        action = "HOLD"

    return {"symbol": symbol, "price": price, "action": action}

# ✅ Render-safe scheduler (no infinite thread!)
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
<head><title>Trading Dashboard</title></head>
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

# ⬅️ Start the price watcher loop
watch_prices()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
