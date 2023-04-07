import os
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

    with open('./data/offers.pickle', 'rb') as f:
        # dump the data to the file
        offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, offers)
    modified_links = [i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[0]]
    send_links_with_timeout(modified_links)

    # Проставляем статус просмотра квартир
    for i in offers:
        if i['Result'] == dict_convert[0]:
            i['ViewedInBot'] = 1

    with open('./data/offers.pickle', 'wb') as f:
        pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)


@bot.message_handler(commands=["show_specified"])
def show_specified_flats(message):

    with open('./data/specified_offers.pickle', 'rb') as f:
        # dump the data to the file
        specified_offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, specified_offers)
    modified_links = [i['Link'] + '\n' for i in filtered_offers]
    send_links_with_timeout(modified_links)

    # Проставляем статус просмотра квартир
    for i in specified_offers:
        i['ViewedInBot'] = 1

    with open('./data/specified_offers.pickle', 'wb') as f:
        pickle.dump(specified_offers, f, protocol=pickle.HIGHEST_PROTOCOL)


@bot.message_handler(commands=["show_cool"])
def show_cool(message):

    with open('./data/offers.pickle', 'rb') as f:
        # dump the data to the file
        offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, offers)
    modified_links = [i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[2]]
    send_links_with_timeout(modified_links)

    # Проставляем статус просмотра квартир
    for i in offers:
        i['ViewedInBot'] = 1

    with open('./data/offers.pickle', 'wb') as f:
        pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)

@bot.message_handler(commands=["set_link"])
def set_link(message):

    specified_link = message.text.split()[1]

    with open('specified_link.pickle', 'wb') as f:
        pickle.dump(specified_link, f)


def scheduler():
    while True:
        offers_quantity = main.proceed_flats()
        bot.send_message("@cian_news", text = f"Загружено {offers_quantity}. Выгрузить новые квартиры можно командой /show_raw или /show_cool")
        time.sleep(24 * 60 * 60)

def scheduler_specified():
    while True:

        time.sleep(15)

        if 'specified_link.pickle' in os.listdir('./'):
            with open('specified_link.pickle', 'rb') as f:
                specified_link = pickle.load(f)
        else:
            specified_link = None

        offers_quantity = specified_main.proceed_specified_flats(main_link=specified_link)
        bot.send_message("@cian_news", text = f"Загружено {offers_quantity}. Выгрузить новые квартиры можно командой /show_specified")
        time.sleep(60 * 60)

thread1 = Thread(target=bot.infinity_polling)
thread2 = Thread(target=scheduler)
thread3 = Thread(target=scheduler_specified)

thread1.start()
thread2.start()
thread3.start()