import os
import threading
import time
import requests
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__, template_folder='templates')

strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        try:
            strategy["BUY_THRESHOLD"] = float(request.form["buy_threshold"])
            strategy["SELL_THRESHOLD"] = float(request.form["sell_threshold"])
            strategy["TAKE_PROFIT"] = float(request.form["take_profit"])
            strategy["STOP_LOSS"] = float(request.form["stop_loss"])
        except:
            pass
        return redirect("/")
    return render_template("dashboard.html", strategy=strategy)

@app.route("/data")
def data():
    return jsonify(strategy["TRACKED_SYMBOLS"])

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
    change = round((price % 10 - 5) / 5 * 100, 2)

    if change <= strategy["BUY_THRESHOLD"]:
        action = "BUY"
    elif change >= strategy["SELL_THRESHOLD"]:
        action = "SELL"
    else:
        action = "HOLD"

    return {"symbol": symbol, "price": price, "action": action}

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    start_price_watcher()
    app.run(host="0.0.0.0", port=port)
