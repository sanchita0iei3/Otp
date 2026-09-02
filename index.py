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

# Platform Icons (Header aur Button ke liye)
def get_platform_info(source):
    s = source.lower()
    if "whatsapp" in s: return "🟢", "💬"
    if "google" in s: return "🔴", "📩"
    if "facebook" in s or "fb" in s: return "🔵", "👥"
    if "telegram" in s or "tg" in s: return "💠", "🤖"
    return "📱", "📲"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        data = payload.get('data', {})
        source = data.get('source', 'MASTER').upper()
        number = str(data.get('number', ''))
        full_msg = data.get('message', '')

        # OTP Extract karna
        otp_match = re.search(r'\b\d{3}[-]?\d{3}\b|\b\d{4,8}\b', full_msg)
        otp = otp_match.group(0) if otp_match else "000-000"

        # Country Info (Flag, ISO, Dial Code)
        try:
            num_obj = phonenumbers.parse(number if number.startswith('+') else '+' + number)
            iso = region_code_for_number(num_obj).upper()
            flag = "".join(chr(127397 + ord(c)) for c in iso)
            dial_code = num_obj.country_code
        except:
            iso, flag, dial_code = "UN", "🌐", "00"

        # Number Parts (Last 4 digits aur Prefix)
        last_4 = number[-4:] if len(number) > 4 else number
        prefix = number[:9] if len(number) > 9 else number

        # Platform Icons
        header_icon, btn_icon = get_platform_info(source)

        # --- DESIGN TEMPLATE (AS PER SCREENSHOT) ---
        # Line 1: [Flag] [ISO] • [Logo][DialCode] • [SOURCE] - [Last4]
        # Line 2: Fixed Text (Chinese/Status)
        # Line 3: Language
        # Line 4: Flame + Prefix
        
        design = (
            f"{flag} {iso} • {header_icon}{dial_code} • <b>{source}</b> - {last_4}\n"
            f"正在营业\n"
            f"English\n"
            f"🔥 Prefix <code>{prefix}</code>"
        )

        # Telegram Buttons
        # Green Button (Left) | Blue Button (Right)
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": f"{header_icon} 📋 {otp}", 
                        "callback_data": "copy"
                    },
                    {
                        "text": "🚀 Number Bot ↗️", 
                        "url": "https://t.me/your_bot_link" # Yahan apne bot ka link dalo
                    }
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": GROUP_ID,
            "text": design,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        })

        return "Success", 200
    except Exception as e:
        return str(e), 500

@app.route('/')
def home(): return "Layout Sync Active!"
