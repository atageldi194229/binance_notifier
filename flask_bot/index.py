import os
import sys
from flask import Flask
import threading
import telebot
import env_config

from subscriptions import get_subscriptions, set_subscriptions
from telebot import types

bot = telebot.TeleBot(env_config.telegram_bot_api_key)

def send_message_to_subsriptions(html_mess):
    subscriptions = get_subscriptions()
    
    for subcriber_chat_id in subscriptions:
        bot.send_message(subcriber_chat_id, html_mess, parse_mode='html')
        

@bot.message_handler(commands=['start'])
def start(message):
    print("BOT /START")
    mess = f'Hi, <b>{message.from_user.first_name} {message.from_user.last_name}</b> \n/help'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(commands=['help'])
def help(message):
    print("BOT /HELP")
    start = types.KeyboardButton('/start')
    subscribe = types.KeyboardButton('/subscribe')
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(start, subscribe)
    
    bot.send_message(message.chat.id, "Help", reply_markup=markup)

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    print("BOT /SUBSCRIBE")
    subscriptions = get_subscriptions()
    subscriptions.append(message.chat.id)
    set_subscriptions(subscriptions)
    
    mess = f'<b>{message.from_user.first_name} subscribed.</b>'
    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler()
def get_user_text(message):
    print("BOT MESSAGE")
    bot.send_message(message.chat.id, f"<code>{message}</code>", parse_mode='html')


def run_forever():
    print("BOT IS STARTED")
    bot.polling(non_stop=True)
    
# asyncio.create_task(run_forever())

try:
    b = threading.Thread(name='background', target=run_forever)
    b.start()
    print("HEY I AM WORKING")
    # bot.send_message(1391638092, "Bot server started")
except Exception as e:
    os.execv(sys.argv[0], sys.argv)


# Start flask server
app = Flask(__name__)

@app.route('/')
def index():
    message = "Bot server index /"
    send_message_to_subsriptions(message)
    return message


@app.route('/message/<message>')
def message(message):
    send_message_to_subsriptions(message)
    return message
  
  
app.run(port=3001)