# web.py
from flask import Flask, render_template, request, redirect
import threading
import json
import requests
import time

app = Flask(__name__, template_folder='templates')

# Shared strategy config
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

# Coin list to monitor
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# Background worker to fetch prices

def update_prices():
    while True:
        tracked = []
        for symbol in SYMBOLS:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            try:
                response = requests.get(url).json()
                price = float(response['price'])

                # Dummy logic: if last digit of price < 5, suggest buy
                action = "HOLD"
                if str(int(price))[-1] in "01234":
                    action = "BUY"
                elif str(int(price))[-1] in "56789":
                    action = "SELL"

                tracked.append({"symbol": symbol, "price": price, "action": action})
            except Exception as e:
                tracked.append({"symbol": symbol, "price": "Error", "action": "Error"})
        strategy["TRACKED_SYMBOLS"] = tracked
        time.sleep(15)  # Update every 15 seconds

# Get strategy (used by bot)
def get_strategy():
    return strategy

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

# Start price updater in background
t = threading.Thread(target=update_prices)
t.daemon = True
t.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
