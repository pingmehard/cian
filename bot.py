import datetime
import time
import pickle
from threading import Thread

import telebot

from creds import token
import main
import specified_main

dict_convert = {
        0 : "remont edition",
        1 : "neponal nah",
        2 : "babka edition",
        3 : "ebat` berem"
    }

cian_link = "https://www.cian.ru/"

bot = telebot.TeleBot(token)

with open('./data/offers.pickle', 'rb') as f:
    # dump the data to the file
    offers = pickle.load(f)

with open('./data/specified_offers.pickle', 'rb') as f:
    # dump the data to the file
    specified_offers = pickle.load(f)



def send_message_bot(text):
    bot.send_message(chat_id = "@cian_news", text = text)

def send_links_with_timeout(iter_object):
    for text in iter_object:
        try:
            res = send_message_bot(text)
        except:
            time.sleep(60)

        time.sleep(.5)


@bot.message_handler(commands=["show_raw"])
def show_raw_flats(message):

    global offers

    filtered_offers = filter(lambda x: datetime.datetime.today().strftime('%Y-%m-%d') == x['LoadDate'], offers)
    modified_links = [cian_link + i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[0]]
    send_links_with_timeout(modified_links)


@bot.message_handler(commands=["show_specified"])
def show_specified_flats(message):

    global specified_offers

    filtered_offers = filter(lambda x: datetime.datetime.today().strftime('%Y-%m-%d') == x['LoadDate'], specified_offers)
    modified_links = [cian_link + i['Link'] + '\n' for i in filtered_offers]
    send_links_with_timeout(modified_links)


@bot.message_handler(commands=["show_cool"])
def show_specified_flats(message):

    global offers

    filtered_offers = filter(lambda x: datetime.datetime.today().strftime('%Y-%m-%d') == x['LoadDate'], offers)
    modified_links = [cian_link + i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[2]]
    send_links_with_timeout(modified_links)


def scheduler():
    while True: 
        main.proceed_flats()
        time.sleep(24 * 60 * 60)

def scheduler_specified():
     while True: 
        specified_main.proceed_specified_flats()
        time.sleep(60 * 60)

thread1 = Thread(target=bot.infinity_polling)
thread2 = Thread(target=scheduler)
thread3 = Thread(target=scheduler_specified)

thread1.start()
thread2.start()
thread3.start()