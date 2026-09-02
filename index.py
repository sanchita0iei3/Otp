from flask import Flask, request
import requests
import json
import re
import phonenumbers
from phonenumbers import region_code_for_number

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = "8888631821:AAFAd8QCPXu3Zyv6GZsRzHw9Q_4oEBwdEig"
GROUP_ID = "-1004295923465"

# 1. Platform Logo/Emoji Mapping (Saare bade platforms)
def get_platform_info(source):
    s = source.lower()
    mapping = {
        "whatsapp": "🟢", "facebook": "🔵", "fb": "🔵", "instagram": "🟣", 
        "insta": "🟣", "google": "🔴", "telegram": "💠", "tg": "💠", 
        "snapchat": "🟡", "apple": "🍎", "microsoft": "💻", "amazon": "🟠",
        "netflix": "🛑", "twitter": "✖️", "x": "✖️", "linkedin": "🟦",
        "tiktok": "🖤", "uber": "🚕", "zomato": "🔴", "swiggy": "🟠",
        "paytm": "🔵", "phonepe": "🟣", "tinder": "🔥", "discord": "👾"
    }
    for key, emoji in mapping.items():
        if key in s:
            return emoji
    return "📱"

# 2. All World Country Flag + 2-Letter Capital Short Code
def get_country_details(number):
    try:
        if not number.startswith('+'):
            number = '+' + number
        
        # Phone library se country code (IN, US, GB, etc.) nikalna
        parsed_num = phonenumbers.parse(number)
        iso_code = region_code_for_number(parsed_num).upper() # Example: IN
        
        # ISO Code se Flag Emoji banana (Example: IN -> 🇮🇳)
        flag = "".join(chr(127397 + ord(c)) for c in iso_code)
        
        return flag, iso_code
    except:
        return "🌐", "UN"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        if not payload: return "No Data", 400
            
        data = payload.get('data', {})
        source = data.get('source', 'N/A')
        number = data.get('number', 'N/A')
        msg_body = data.get('message', '')

        # OTP Extract karna (4-8 digits)
        otp_match = re.search(r'\b\d{4,8}\b', msg_body)
        otp = otp_match.group(0) if otp_match else "----"

        # Platform aur Country details nikalna
        p_logo = get_platform_emoji(source) # Platform Logo
        flag, country_short = get_country_details(number) # Flag aur IN/US/GB

        # --- TEMPLATE DESIGN ---
        # Line 1: [Logo] [Flag] [ShortCode] [Number]
        # Line 2: Full Message
        header = f"{p_logo} {flag} <b>{country_short}</b> <code>{number}</code>"
        
        full_design = (
            f"{header}\n\n"
            f"{msg_body}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"👉 Tap to Copy: <code>{otp}</code>"
        )

        # Telegram Button setup
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        markup = {
            "inline_keyboard": [[{"text": f"🔑 {otp} 📋", "callback_data": "copy"}]]
        }
        
        requests.post(url, json={
            "chat_id": GROUP_ID,
            "text": full_design,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(markup)
        })

        return "Success", 200
        
    except Exception as e:
        return str(e), 500

# Helper function for platform
def get_platform_emoji(source):
    # (Same as mapping above)
    return get_platform_info(source)

@app.route('/')
def home(): return "Professional OTP System Active!"
