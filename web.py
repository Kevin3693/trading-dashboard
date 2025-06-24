from flask import Flask, render_template, request, redirect
import threading
import json

app = Flask(__name__, template_folder='templates')

# Shared strategy config (live memory object)
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5,
    "TRACKED_SYMBOLS": []
}

# 👁 Used by bot to sync with dashboard
def get_strategy():
    return strategy

# 🧠 Endpoint to view + update
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

def start_dashboard():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
