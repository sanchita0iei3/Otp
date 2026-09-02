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

# 1. ORIGINAL LOGO LOGIC (Ye sabse pehle dikhega)
def get_platform_logo(source):
    s = source.lower()
    logos = {
        "whatsapp": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1024px-WhatsApp.svg.png",
        "facebook": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Facebook_Logo_2023.png/1024px-Facebook_Logo_2023.png",
        "fb": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Facebook_Logo_2023.png/1024px-Facebook_Logo_2023.png",
        "instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1024px-Instagram_logo_2016.svg.png",
        "insta": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1024px-Instagram_logo_2016.svg.png",
        "google": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_Reference_Icon.svg/1024px-Google_Reference_Icon.svg.png",
        "telegram": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/1024px-Telegram_logo.svg.png",
        "snapchat": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c4/Snapchat_logo.svg/1024px-Snapchat_logo.svg.png",
        "apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1024px-Apple_logo_black.svg.png"
    }
    # Default agar platform na mile
    return logos.get(next((k for k in logos if k in s), None), "https://cdn-icons-png.flaticon.com/512/2156/2156475.png")

# 2. COUNTRY LOGO (FLAG) & SHORT CODE (IN, US)
def get_country_details(number):
    try:
        if not str(number).startswith('+'):
            number = '+' + str(number)
        parsed = phonenumbers.parse(number)
        iso = region_code_for_number(parsed).upper() # BIG Code (IN, US)
        flag = "".join(chr(127397 + ord(c)) for c in iso) # Flag Logo
        return flag, iso
    except:
        return "🌐", "UN"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        data = payload.get('data', {})
        source = data.get('source', 'System')
        number = data.get('number', 'N/A')
        message = data.get('message', '')

        # OTP Extract (4-8 digits)
        otp_match = re.search(r'\b\d{4,8}\b', message)
        otp = otp_match.group(0) if otp_match else "NULL"

        # Platform Logo URL aur Country Details
        logo_url = get_platform_logo(source)
        flag, short_code = get_country_details(number)

        # --- DESIGN TEMPLATE ---
        # Header Line: [Flag] [ShortCode] [Number]
        caption = (
            f"{flag} <b>{short_code}</b> <code>{number}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{message}\n\n"
            f"🔑 <b>OTP:</b> <code>{otp}</code>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        # Telegram SendPhoto API - Isse LOGO sabse pehle aayega
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        markup = {"inline_keyboard": [[{"text": f"🔑 {otp} 📋", "callback_data": "copy"}]]}

        requests.post(url, data={
            "chat_id": GROUP_ID,
            "photo": logo_url, # Ye raha aapka Original Logo (sabse pehle)
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(markup)
        })

        return "Success", 200
    except Exception as e:
        return str(e), 500

@app.route('/')
def home(): return "Original Logo Platform Live!"
