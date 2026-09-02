from flask import Flask, request
import requests
import json

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = "8888631821:AAFAd8QCPXu3Zyv6GZsRzHw9Q_4oEBwdEig"
GROUP_ID = "-1004295923465" # Yaad se -100 ke saath (e.g., "-1001234567")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

@app.route('/', methods=['GET'])
def home():
    return "Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return "No Data", 400
            
        # Data nikalna
        sender = data.get('sender', 'OTP System')
        otp = data.get('message', data.get('otp', 'No Code'))

        # Professional Design
        design = (
            f"🚀 <b>NEW OTP RECEIVED</b> 🚀\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Source:</b> {sender}\n"
            f"🔑 <b>OTP:</b> <code>{otp}</code>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        send_to_telegram(design)
        return "Success", 200
    except Exception as e:
        return str(e), 500
