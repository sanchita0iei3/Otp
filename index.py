from flask import Flask, request
import requests
import json
import re

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = "8888631821:AAFAd8QCPXu3Zyv6GZsRzHw9Q_4oEBwdEig"
GROUP_ID = "-1004295923465" # -100 ke saath

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
    return "OTP Extractor is Live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        if not payload:
            return "No Data", 400
            
        inner_data = payload.get('data', {})
        
        # 1. Data Extract karna
        source = inner_data.get('source', 'N/A')
        number = inner_data.get('number', 'N/A')
        full_message = inner_data.get('message', '')

        # 2. OTP nikalne ka logic (Sirf digits nikalna 4-8 length ki)
        otp_match = re.search(r'\b\d{4,8}\b', full_message)
        otp = otp_match.group(0) if otp_match else "Not Found"

        # 3. Ekdam Clean Design (Sirf 3 line)
        # <code> tag se OTP par click karte hi copy ho jayega
        clean_design = (
            f"<b>Source:</b> {source}\n"
            f"<b>Number:</b> {number}\n"
            f"<b>OTP:</b> <code>{otp}</code>"
        )

        # 4. Group mein bhejna
        send_to_telegram(clean_design)
        return "Success", 200
        
    except Exception as e:
        return str(e), 500
