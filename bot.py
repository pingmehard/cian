import datetime
import time
import pickle
from threading import Thread

import telebot

from creds import token
from main import proceed_flats

dict_convert = {
        0 : "remont edition",
        1 : "neponal nah",
        2 : "babka edition",
        3 : "ebat` berem"
    }

cian_link = "https://www.cian.ru/"

bot = telebot.TeleBot(token)



def send_message_bot(text):

    bot.send_message(chat_id = "@cian_news", text = text)

@bot.message_handler(commands=["show_raw"])
def show_raw_flats(message):

    with open('./data/offers.pickle', 'rb') as f:
            # dump the data to the file
            offers = pickle.load(f)

    filtered_offers = filter(lambda x: datetime.datetime.today().strftime('%Y-%m-%d') == x['LoadDate'], offers)

    for text in [cian_link + i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[0]]:

        try:
            res = send_message_bot(text)
        except:
            time.sleep(60)

        time.sleep(.5)

def sheduler():
    while True: 
        proceed_flats()
        time.sleep(24 * 60 * 60)

thread1 = Thread(target=bot.infinity_polling)
thread2 = Thread(target=sheduler)

thread1.start()
thread2.start()