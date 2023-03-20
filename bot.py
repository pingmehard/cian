import telebot

from creds import token

bot = telebot.TeleBot(token)

def send_message_bot(text):

    bot.send_message(chat_id = "@cnews_channel", text = text)