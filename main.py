import os
import openai
import telebot
from flask import Flask, request

# === Настройки ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='HTML')

# === Flask веб-сервер ===
app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 Бот работает!"

@app.route("/" + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "", 200

# === Ответ от OpenAI ===
def ask_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

# === Команда /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот с искусственным интеллектом 🤖\n\nПросто напиши мне что угодно в ЛС, или упомяни меня в группе — @{} — и я постараюсь помочь!".format(bot.get_me().username)
    )

# === Команда /help ===
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "❓ <b>Как пользоваться:</b>\n\n▫ В личке — просто пиши вопрос или запрос\n▫ В группе — упомяни меня @{} и напиши вопрос\n\nЯ подключен к OpenAI и стараюсь отвечать как ChatGPT 💬".format(bot.get_me().username)
    )

# === Обработка сообщений ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.type in ["group", "supergroup"]:
        if f"@{bot.get_me().username}" in message.text:
            clean = message.text.replace(f"@{bot.get_me().username}", "").strip()
            reply = ask_gpt(clean)
            bot.reply_to(message, reply)
    else:
        reply = ask_gpt(message.text)
        bot.reply_to(message, reply)

# === Запуск сервера ===
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR-RENDER-URL.onrender.com/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
