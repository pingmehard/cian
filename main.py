import urllib.request
import pickle
import datetime
from collections import Counter
import platform
import os
import json

from selenium import webdriver

from tensorflow.keras.models import load_model

import numpy as np

import utils
import parser_utils

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
main_link = config['main_link']
model_path = config['model_path']
model_path_additional = config['model_path_additional']


def make_conclusion(preds_vector):

    '''
    Выводим предсказанный класс квартиры
    '''

    global dict_convert

    preds = [np.argmax(i) for i in preds_vector]

    count_preds = Counter(preds)

    max_index = max(count_preds.items(), key = lambda x: x[1])

    if count_preds[0] > 3:
        return dict_convert[0]

    return dict_convert[max_index[0]]


def proceed_flats(main_link = main_link, task_name = 'offers'):

    global dict_convert, model_path, model_path_additional

    # загружаем обученную модель для предсказания класса изображений
    try:
        model = load_model(model_path)
    except:
        model = load_model(model_path_additional)

    model.compile(optimizer='adam',
             loss='categorical_crossentropy',
             metrics=['categorical_accuracy'])

    # adding options to chrome
    options = webdriver.ChromeOptions()
    for option in config['main_chrome_options']:
        options.add_argument(option)

    # try:
    #     driver = webdriver.Remote(
    #         command_executor="http://172.17.0.2:4444/wd/hub",
    #         options=options
    # )
    # except:

    driver = webdriver.Chrome(config['chrome_web_driver'][platform.system()], options=options)
    offers_load_status = False

    try:
        with open(config['offers'] + '{task_name}.pickle', 'rb') as f:
            backup_offers = pickle.load(f)
            offers_load_status = True

        offer_links = [offer['Link'] for offer in backup_offers]
    except:
        offer_links = []
        print('Нет файла дампа загрузки, начинается новая процедура сохранения')

    # Парсер начинает загрузку квартир
    offers = parser_utils.proceed(
        driver=driver, 
        main_link=main_link, 
        offers_load_status=offers_load_status, 
        offer_links=offer_links,
        )

    driver.close()

    # загружаем все изображения по ссылкам и добавляем вектора от модели
    for offer in offers:

        data_images = []
        preds = []

        # создаем вектор изображения и добавляем в список
        for image_link in offer['Images']:
            
            if "cian_images" in os.listdir('./'):
                image_name = config['cian_images_catalogue'] + f"{image_link.split('/')[-1]}"
            else:
                break

            try:
                urllib.request.urlretrieve(image_link, image_name)
                data = utils.get_image_vector(380, image_name)
                data_images += [data]
            except:
                pass
        
        try:
            # предсказываем класс изображения
            preds = model.predict(np.array(data_images))
            # сохраняем предсказанный класс в атрибуты изображения
            offer['Predicts'] = preds
            # создаем итоговый вектор с предсказанной бизнес-категорией
            offer['Result'] = make_conclusion(offer['Predicts'])
            # для бота создаем атрибут даты, чтобы иметь возможность 
            # выгружать последние определенные квартиры с определенным результатом
            # Check проставляем для отметки просмотра
            offer['LoadDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
            offer['ViewedInBot'] = 0
        except Exception as e:
            print(len(data_images))
            print(e)

            # сохраняем предсказанный класс в атрибуты изображения
            offer['Predicts'] = []
            # создаем итоговый вектор с предсказанной бизнес-категорией
            offer['Result'] = []
            # для бота создаем атрибут даты, чтобы иметь возможность 
            # выгружать последние определенные квартиры с определенным результатом
            # Check проставляем для отметки просмотра
            offer['LoadDate'] = '-'
            offer['ViewedInBot'] = 1

    # сохраняем полученные данные по изображениям
    # если бэкап уже был, то добавляем к бэкапу новые загруженные квартиры
    if offers_load_status:
        backup_offers += offers
        with open(config['offers'] + '{task_name}.pickle', 'wb') as f:
            pickle.dump(backup_offers, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        # иначе сохраняем первые офферы квартир
        with open(config['offers'] + '{task_name}.pickle', 'wb') as f:
            pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)

    return len(offers)



if __name__ == '__main__':
    proceed_flats()