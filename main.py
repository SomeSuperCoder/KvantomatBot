import telebot
from telebot import types
import requests
import json
import hashlib

API_TOKEN = '7211701424:AAHDw1WFM4m5TFlv6RC-g3Q2Zpd5rVdwCnM'
bot = telebot.TeleBot(API_TOKEN)

USER_STATES = {}
USER_LOGINS = {}

STUDENT_BUTTON_TEXT = "Ученик"
TEACHER_BUTTON_TEXT = "Педагог/Администратор"

BASE_URL = "https://roughy-precious-neatly.ngrok-free.app"

DEFAULT_PASSWORD_HASH = "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f"

def check_login_credentials(login, hashed_password):
    response = requests.get(f"{BASE_URL}/api/check_credentials?login={login}&hashed_password={hashed_password}");

    try:
        response.raise_for_status();
    except BaseException as e:
        print(f"Server error!\nDetails:\n{e.__class__.__name__}: {e}");
        return False;

    return json.loads(response.text)

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(STUDENT_BUTTON_TEXT, TEACHER_BUTTON_TEXT)
    bot.send_message(message.chat.id, f"Вы {STUDENT_BUTTON_TEXT} или {TEACHER_BUTTON_TEXT}", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in [STUDENT_BUTTON_TEXT, TEACHER_BUTTON_TEXT])
def handle_response(message):
    if message.text == STUDENT_BUTTON_TEXT:
        USER_STATES[message.chat.id] = 'awaiting_access_code'
        bot.send_message(message.chat.id, "Введите код доступа ученика:")
    elif message.text == TEACHER_BUTTON_TEXT:
        USER_STATES[message.chat.id] = 'awaiting_login'
        bot.send_message(message.chat.id, "Введите логин:")

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'awaiting_access_code')
def get_access_code(message):
    access_code = message.text

    if check_login_credentials(access_code, DEFAULT_PASSWORD_HASH):
        bot.send_message(message.chat.id, f"[Нажмите сюда чтобы перейти в Квантомат]({BASE_URL}/auto_auth?login={access_code}&hashed_password={DEFAULT_PASSWORD_HASH})", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Неверный код доступа. Нажмите чтобы перезапустить бота -> /start")

    del USER_STATES[message.chat.id]  # Clear the state

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'awaiting_login')
def get_login(message):
    login = message.text
    USER_LOGINS[message.chat.id] = login
    USER_STATES[message.chat.id] = 'awaiting_password'
    bot.send_message(message.chat.id, "Введите пароль:")

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'awaiting_password')
def get_password(message):
    login = USER_LOGINS[message.chat.id]
    password = message.text
    hashed_password = hashlib.sha256(password.encode()).hexdigest();

    if check_login_credentials(login, hashed_password):
        bot.send_message(message.chat.id, f"[Нажмите сюда чтобы перейти в Квантомат]({BASE_URL}/auto_auth?login={login}&hashed_password={hashed_password})", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Неверный логин и пароль. Нажмите чтобы перезапустить бота -> /start")
    del USER_STATES[message.chat.id]  # Clear the state

# Start polling
bot.polling()
