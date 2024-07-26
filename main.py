from keep_alive import keep_alive
import telebot
import datetime
import time
import os
import subprocess
import re
from dotenv import load_dotenv
from flask import Flask
import threading

# Load environment variables from a .env file
load_dotenv()

bot_token = '7340174561:AAE89h4NQWPGsarH3TNNT7A2vYPgN65lV50'
bot = telebot.TeleBot(bot_token)
processes = []
ADMIN_ID = 6628250996
allowed_group_id = -4274699297

bot = telebot.TeleBot(bot_token)

bot_active = True  # Global variable to track the bot's status
bot_start_time = time.time()

# Constants
MAX_SPAM_COUNT = 100
DEFAULT_LAP = "50"

def TimeStamp():
    return str(datetime.date.today())

def mask_phone_number(phone_number):
    # Mask the middle three digits with 'xxx'
    if len(phone_number) == 10:
        return phone_number[:3] + 'xxx' + phone_number[6:]
    elif len(phone_number) == 11:
        return phone_number[:4] + 'xxx' + phone_number[7:]
    return phone_number  # Return unmasked if length doesn't match expected formats

def check_bot_status(func):
    """Decorator to check if the bot is active."""
    def wrapper(message, *args, **kwargs):
        if bot_active:
            return func(message, *args, **kwargs)
        else:
            bot.reply_to(message, 'Bot đang tắt, vui lòng đợi một chút.')
    return wrapper

@bot.message_handler(commands=['start', 'help'])
@check_bot_status
def send_welcome(message):
    bot.reply_to(message, "Chào mừng bạn! Đây là bot của tôi.")

@bot.message_handler(commands=['spam'])
@check_bot_status
def spam(message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    args = message.text.split()
    
    if len(args) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP SỐ ĐIỆN THOẠI')
        return

    phone_number = args[1]
    lap = args[2] if len(args) > 2 else DEFAULT_LAP

    if not lap.isnumeric() or not (0 < int(lap) <= MAX_SPAM_COUNT):
        bot.reply_to(message, "Vui Lòng Spam Trong Khoảng 1 - 100 Thôi !!")
        return
        
    if not re.match(r"^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$", phone_number):
        bot.reply_to(message, 'SỐ ĐIỆN THOẠI KHÔNG HỢP LỆ !')
        return

    if phone_number in ["0363161355"]:
        bot.reply_to(message, "Spam cái gì thằng ngu")
        return

    file_path = os.path.join(os.getcwd(), "sms.py")
    if not os.path.isfile(file_path):
        bot.reply_to(message, "Tệp sms.py không tồn tại.")
        return

    try:
        process = subprocess.Popen(["python", file_path, phone_number, lap])
        processes.append(process)
        masked_phone_number = mask_phone_number(phone_number)
        
        # First, send a placeholder message
        placeholder_message = bot.reply_to(message, "Đang xử lý yêu cầu...")

        # Now, delete the original message
        bot.delete_message(message.chat.id, message.message_id)

        # Send the final reply message
        bot.edit_message_text(
            chat_id=placeholder_message.chat.id,
            message_id=placeholder_message.message_id,
            text=f'🚀 ➤ Xin chào: {username}\n➤ USER ID: [ {user_id} ]\n➤ Bạn đã gửi yêu cầu tấn công thành công đến số📱: [ {masked_phone_number} ]\n➤ Ngày: {TimeStamp()}🚀'
        )
    except Exception as e:
        bot.reply_to(message, f'Không thể thực hiện yêu cầu: {e}')

@bot.message_handler(commands=['ktool'])
@check_bot_status
def help(message):
    help_text = '''
Danh sách lệnh:
┏━━━━━━━━━━━━━━━━━┓
┣➤ /spam: {SĐT} ✅
┣➤ /ktool: Danh sách lệnh ✅
┣➤ /time: Thời Gian HĐ Bot ✅
┣➤ /status: Lượt Chạy Bot ✅
┣➤ /admin: Thông Tin Admin ✅
┣➤ /taitool: KToolV5 ✅
┗━━━━━━━━━━━━━━━━━┛
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
@check_bot_status
def status(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return
    process_count = len(processes)
    bot.reply_to(message, f'Số quy trình đang chạy: {process_count}.')

@bot.message_handler(commands=['time'])
@check_bot_status
def show_uptime(message):
    current_time = time.time()
    uptime_seconds = current_time - bot_start_time
    minutes, seconds = divmod(int(uptime_seconds), 60)
    bot.reply_to(message, f'Bot Đã Hoạt Động Được: {minutes} phút, {seconds} giây')

@bot.message_handler(commands=['admin'])
def admin_info(message):
    zalo_box = os.getenv('ZALO_BOX', 'https://zalo.me/g/phmuwh591')
    youtube_url = os.getenv('YOUTUBE_URL', 'https://www.youtube.com/@K-toolv5')
    admin_sdt = os.getenv('ADMIN_SDT', '0363161335')
    admin_message = f"Thông tin liên hệ của Admin:\n\nBox Zalo: {zalo_box}\nZalo: {admin_sdt}\nyoutube: {youtube_url}"
    bot.reply_to(message, admin_message)

@bot.message_handler(commands=['taitool'])
@check_bot_status
def download_ktoolv5(message):
    download_url = os.getenv('DOWNLOAD_URL', 'https://vuongquocanhkhoakey.000webhostapp.com/1.html')
    bot.reply_to(message, f"Link tải ktoolv5: {download_url}")

@bot.message_handler(commands=['on'])
def turn_on_bot(message):
    global bot_active
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot_active = True
        bot.reply_to(message, 'Bot đã được bật.')
    else:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')

# Handle invalid commands
@bot.message_handler(func=lambda message: True, content_types=['text'])
def invalid_command(message):
    if not message.text.startswith('/'):
        return  # Do nothing if it's not a command
    bot.reply_to(message, 'Lệnh không hợp lệ. Vui lòng sử dụng lệnh /ktool để xem danh sách lệnh.')

# Setup a simple web server to keep the bot running
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

bot.infinity_polling(timeout=60, long_polling_timeout=1)
