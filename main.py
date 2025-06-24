import os
import asyncio
import threading
import time
import requests
from telegram import Bot
from flask import Flask, render_template, request

# Load environment variables from Replit Secrets
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Initialize Telegram Bot
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Strategy thresholds (can be updated via dashboard)
strategy = {
    "BUY_THRESHOLD": -1.0,
    "SELL_THRESHOLD": 1.0,
    "TAKE_PROFIT": 1.5,
    "STOP_LOSS": -1.5
}

SYMBOL = "BTCUSDT"

# Async Telegram sender
async def send_telegram_message(message):
    await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Wrapper to call async send from sync context
def send_message(message):
    asyncio.run(send_telegram_message(message))

# Dummy price checker for testing
def fetch_current_price():
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except:
        return None

# Flask dashboard
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    global strategy
    if request.method == "POST":
        try:
            strategy["BUY_THRESHOLD"] = float(request.form.get("BUY_THRESHOLD", -1.0))
            strategy["SELL_THRESHOLD"] = float(request.form.get("SELL_THRESHOLD", 1.0))
            strategy["TAKE_PROFIT"] = float(request.form.get("TAKE_PROFIT", 1.5))
            strategy["STOP_LOSS"] = float(request.form.get("STOP_LOSS", -1.5))
            send_message("✅ Strategy updated from dashboard.")
        except Exception as e:
            print("Error updating strategy:", e)
    return render_template("dashboard.html", strategy=strategy)

# Start Flask in thread
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# Send startup message
send_message("✅ Bot is live!\nUse /status to check position.")
