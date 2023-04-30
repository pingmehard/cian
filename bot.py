import time
import pickle
from threading import Thread
import json

import telebot

from creds import token
import main
import specified_main

# configs and several default vars
with open("config.json", "r") as f:
    config = json.load(f)

# dict_convert = config['dict_convert']
dict_convert = {
    0: 'remont edition',
    1: 'neponal nah',
    2: 'babka edition',
    3: 'ebat` berem'
    }

cian_link = config['cian_link']
group_name = config['dev_group_name'] if config['dev_mode'] else config['group_name']
specified_link = config['specified_link']

bot = telebot.TeleBot(token)



def send_message_bot(text, chat_id):
    bot.send_message(chat_id = chat_id, text = text)


def send_links_with_timeout(iter_object, chat_id):
    for text in iter_object:
        try:
            res = send_message_bot(text, chat_id)
        except:
            time.sleep(60)

        time.sleep(.5)

def construct_message(offers):

    '''
    Делает текстовое сообщение для вывода квартиры из словаря сохраненных данных
    '''

    text = ''
    texts = []
    for off in offers:
        if 'FirstHistoryDate' in off:
            text += 'Первая дата публикации: ' + str(off['FirstHistoryDate']) + '\n'
        if 'HouseInfo' in off:
            if off['HouseInfo']:
                text += 'Тип дома: ' + str(off['HouseInfo'].get('Тип дома', '-')) + '\n'
        text += off['Link'] + '\n'
        texts += [text]
        text = ''

    return texts


@bot.message_handler(commands=["show_raw"])
def show_raw_flats(message):

    with open(config['offers'] + 'offers.pickle', 'rb') as f:
        offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, offers)
    modified_links = [i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[0]]
    send_links_with_timeout(modified_links, chat_id = group_name)

    # set viewed status for flats
    for i in offers:
        if i['Result'] == dict_convert[0]:
            i['ViewedInBot'] = 1

    with open(config['offers'] + 'offers.pickle', 'wb') as f:
        pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)


@bot.message_handler(commands=["show_specified"])
def show_specified_flats(message):

    with open(config['offers'] + 'specified_offers.pickle', 'rb') as f:
        # dump the data to the file
        specified_offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, specified_offers)
    modified_links = [i['Link'] + '\n' for i in filtered_offers]
    send_links_with_timeout(modified_links, chat_id = group_name)

    # Проставляем статус просмотра квартир
    for i in specified_offers:
        i['ViewedInBot'] = 1

    with open(config['offers'] + 'specified_offers.pickle', 'wb') as f:
        pickle.dump(specified_offers, f, protocol=pickle.HIGHEST_PROTOCOL)


@bot.message_handler(commands=["show_cool"])
def show_cool(message):

    with open(config['offers'] + 'offers.pickle', 'rb') as f:
        offers = pickle.load(f)

    filtered_offers = filter(lambda x: x['ViewedInBot'] == 0 and x['Result'] == dict_convert[2], offers)
    modified_links = construct_message(filtered_offers)
    send_links_with_timeout(modified_links, chat_id = group_name)

    # set flats status 
    for i in offers:
        if i['Result'] == dict_convert[2]:
            i['ViewedInBot'] = 1

    with open(config['offers'] + 'offers.pickle', 'wb') as f:
        pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)


@bot.message_handler(commands=["set_link"])
def set_link(message):

    specified_link = message.text.split()[1]

    # adding new link for specialized living complex
    with open("config.json", "r") as f:
        config = json.load(f)
    config['specified_link'] = specified_link
    with open("config.json", "w") as f:
        json.dump(config, f)

def scheduler():
    while True:
        offers_quantity = main.proceed_flats()
        bot.send_message(group_name, text = f"Загружено {offers_quantity}. Выгрузить новые квартиры можно командой /show_raw или /show_cool")

        if offers_quantity > 0:
            with open(config['offers'] + 'offers.pickle', 'rb') as f:
                # dump the data to the file
                offers = pickle.load(f)

            filtered_offers = filter(lambda x: x['ViewedInBot'] == 0, offers)
            modified_links = [i['Link'] + '\n' for i in filtered_offers if i['Result'] == dict_convert[2]]

            if not config['dev_mode']:
                print('Выгружаем новые классные квартиры во вторую группу')
                send_links_with_timeout(modified_links, chat_id="@flats_c_beta")
                print("Квартиры выгружены")

        time.sleep(config['main_update_every_seconds'])

def scheduler_specified():
    while True:

        time.sleep(15)

        # for specified link update
        with open("config.json", "r") as f:
            config = json.load(f)

        offers_quantity = specified_main.proceed_specified_flats(main_link=config['specified_link'])

        if offers_quantity > 0:
            bot.send_message(group_name, text = f"Загружено {offers_quantity}. Выгрузить новые квартиры можно командой /show_specified")

        time.sleep(config['specified_update_every_seconds'])


thread1 = Thread(target=bot.infinity_polling)
thread2 = Thread(target=scheduler)
thread3 = Thread(target=scheduler_specified)

thread1.start()
thread2.start()
thread3.start()